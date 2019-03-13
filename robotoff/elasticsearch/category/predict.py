import operator
import pathlib
from typing import Iterable, Dict

from robotoff.products import ProductDataset
from robotoff import settings
from robotoff.utils import dump_jsonl, get_logger

from robotoff.utils.es import get_es_client
from robotoff.elasticsearch.category.match import predict_category


logger = get_logger(__name__)


def generate_dataset(client, products: Iterable[Dict]) -> Iterable[Dict]:
    for product in products:
        predictions = []

        for lang in product['languages_codes']:
            product_name = product.get(f"product_name_{lang}")

            if not product_name:
                continue

            prediction = predict_category(client, product_name, lang)

            if prediction is None:
                continue

            category, score = prediction
            predictions.append((lang, category, score))
            continue

        if predictions:
            # Sort by descending score
            sorted_predictions = sorted(predictions,
                                        key=operator.itemgetter(2),
                                        reverse=True)

            prediction = sorted_predictions[0]
            lang, category, score = prediction

            yield {
                'barcode': product['code'],
                'category': category,
                'matcher_lang': lang,
                'model': 'matcher',
            }


def predict(output_path: pathlib.Path):
    dataset = ProductDataset(settings.JSONL_DATASET_PATH)

    product_iter = (dataset.stream()
                           .filter_nonempty_text_field('code')
                           .filter_nonempty_text_field('product_name')
                           .filter_empty_tag_field('categories_tags')
                           .filter_nonempty_tag_field('countries_tags')
                           .filter_nonempty_tag_field('languages_codes')
                           .iter())

    logger.info("Performing prediction on products without categories")

    es_client = get_es_client()
    prediction_dataset = generate_dataset(es_client, product_iter)
    dump_jsonl(output_path, prediction_dataset)