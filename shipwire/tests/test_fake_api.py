

from shipwire.test_api import *
from shipwire.common import *


def test_fake_api_auth():
    """
    Test to be sure LoremIpsumAPI implements fake auth of some kind.
    """
    # should pass
    LoremIpsumAPI("test_account", "test_password", "test")
    fails = 0
    try:
        # should fail
        LoremIpsumAPI("OEUHNOETCHU", "test_password", "test")
    except:
        fails += 1
    try:
        # should fail
        LoremIpsumAPI("test_account", "OEUHNOETCHU", "test")
    except:
        fails += 1
    try:
        # should fail
        LoremIpsumAPI("test_account", "test_password", "OEUHNOETCHU")
    except:
        fails += 1
    assert fails == 3


def test_bs_inventory_lookup():
    """
    Tests the inventory_for_warehouse call by calling
    inventory_lookup.
    """
    
    api = LoremIpsumAPI("test_account", "test_password", "test")
    db = BS_PRODUCT_DATABASE

    for sku in db.keys():
        stock_info = db[sku]["stock_info"]
        inventory = api.inventory_lookup(sku)
        for code in WAREHOUSE_CODES:
            if stock_info.has_key(code):
                assert inventory[code] is not None
                assert inventory[code].code == sku # this is not confusing at all nope
                assert inventory[code].quantity == stock_info[code]
            else:
                assert inventory[code] is None

    for value in api.inventory_lookup("fake_sku").values():
        assert value is None

    
def test_cache_invalidation():
    """
    Tests caching for inventory lookups.
    """
    raise NotImplementedError("Cache invalidation test.")
