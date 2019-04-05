import json

from robotoff.products import serialize_pb
from robotoff.settings import PROJECT_DIR

PRODUCT_JSON_DIR = PROJECT_DIR / 'tests' / 'resources' / 'products'


def test_serialize_pb():
    with open(PRODUCT_JSON_DIR / '00218894.json', 'r') as f:
        product = json.load(f)

    serial = serialize_pb(product)
    assert serial.code == "00218894"

    serialized = serial.SerializeToString()
    print(serialized)
