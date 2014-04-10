

import time

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
    
    api = LoremIpsumAPI("test_account", "test_password", "test")
    db = BS_PRODUCT_DATABASE
    sku = "sku_0001"
    db_record = db[sku]

    first = api.inventory_lookup(sku)["CHI"].quantity
    assert first == 10

    db_record["stock_info"]["CHI"] = 9

    second = api.inventory_lookup(sku)["CHI"].quantity
    assert second == 9

    db_record["stock_info"]["CHI"] = 3

    third = api.inventory_lookup(sku, True)["CHI"].quantity
    assert third == 9

    api.cache_expire = 0
    fourth = api.inventory_lookup(sku, True)["CHI"].quantity
    assert fourth == 3
    

def test_get_shipping_options():
    """
    Test the get_shipping_options method.
    """
    api = LoremIpsumAPI("test_account", "test_password", "test")
    cart = ["sku_0002", "sku_0002", "sku_0003"]
    addr = AddressInfo(
        "Some Body",
        "12345 S Someplace Rd",
        "",
        "Duster",
        "IN",
        "United States",
        "47999",
        "123-4567",
        "nobody@donotreply.pleasedonotregisterthistld",
    )

    opts = api.get_shipping_options(addr, "PHL", cart)

    for local_method in LOCAL_SHIPPING:
        assert opts.has_key(local_method)
    for intl_method in INTL_SHIPPING:
        assert not opts.has_key(intl_method)
    for value in opts.values():
        assert type(value[0]) == str
        assert type(value[1]) == float
    
    opts = api.get_shipping_options(addr, "UK", cart)
    
    for local_method in LOCAL_SHIPPING:
        assert not opts.has_key(local_method)
    for intl_method in INTL_SHIPPING:
        assert opts.has_key(intl_method)
    for value in opts.values():
        assert type(value[0]) == str
        assert type(value[1]) == float


def test_place_order():
    """
    Test the mechanism for placing fake orders.
    """

    api = LoremIpsumAPI("test_account", "test_password", "test")
    db = BS_PRODUCT_DATABASE
    cart = ["sku_0002", "sku_0002", "sku_0003"]
    warehouse = "PHL"
    addr = AddressInfo(
        "Some Body",
        "12345 S Someplace Rd",
        "",
        "Duster",
        "IN",
        "United States",
        "47999",
        "123-4567",
        "nobody@donotreply.pleasedonotregisterthistld",
    )
    acknowledgement = api.place_order(addr, warehouse, cart, "GD")
