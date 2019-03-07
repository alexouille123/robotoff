from typing import List, Dict

import requests

from robotoff.utils import get_logger

http_session = requests.Session()

POST_URL = "https://world.openfoodfacts.org/cgi/product_jqm2.pl"
DRY_POST_URL = "https://world.openfoodfacts.net/cgi/product_jqm2.pl"
AUTH = ("roboto-app", "4mbN9wJp8LBShcH")
AUTH_DICT = {
    'user_id': AUTH[0],
    'password': AUTH[1],
}

API_URL = "https://world.openfoodfacts.org/api/v0"
PRODUCT_URL = API_URL + "/product"

logger = get_logger(__name__)


def get_product(product_id: str, fields: List[str]=None):
    fields = fields or []
    url = PRODUCT_URL + "/{}.json".format(product_id)

    if fields:
        # requests escape comma in URLs, as expected, but openfoodfacts server
        # does not recognize escaped commas.
        # See https://github.com/openfoodfacts/openfoodfacts-server/issues/1607
        url += '?fields={}'.format(','.join(fields))

    r = http_session.get(url)

    if r.status_code != 200:
        return

    data = r.json()

    if data['status_verbose'] != 'product found':
        return

    return data['product']


def add_category(barcode: str, category: str, dry=False):
    params = {
        'code': barcode,
        'add_categories': category,
        **AUTH_DICT
    }
    update_product(params, dry=dry)


def update_quantity(barcode: str, quantity: str, dry=False):
    params = {
        'code': barcode,
        'quantity': quantity,
        **AUTH_DICT
    }
    update_product(params, dry=dry)


def save_ingredients(barcode: str, ingredient_text: str,
                     lang: str = None, dry=False):
    ingredient_key = ('ingredients_text' if lang is None
                      else f'ingredients_{lang}_text')
    params = {
        'code': barcode,
        ingredient_key: ingredient_text,
        **AUTH_DICT,
    }
    update_product(params, dry=dry)


def add_emb_code(barcode: str, emb_code: str, dry=False):
        params = {
            'code': barcode,
            'add_emb_codes': emb_code,
            'comment': "Adding packager code (automated edit)",
            **AUTH_DICT,
        }
        update_product(params, dry=dry)


def add_label_tag(barcode: str, label_tag: str, dry=False):
    params = {
        'code': barcode,
        'add_labels': label_tag,
        'comment': "Adding label tag (automated edit)",
        **AUTH_DICT,
    }
    update_product(params, dry=dry)


def update_product(params: Dict, dry=False):
    if dry:
        r = http_session.get(DRY_POST_URL, params=params,
                             auth=('off', 'off'))
    else:
        r = http_session.get(POST_URL, params=params)

    r.raise_for_status()
    json = r.json()

    status = json.get('status_verbose')

    if status != "fields saved":
        logger.warn(
            "Unexpected status during product update: {}".format(
                status))
