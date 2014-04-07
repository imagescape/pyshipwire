

from shipwire.test_api import *


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


def test_bs_api():
    """
    Tests to the LoremIpsumAPI.inventory_lookup call for correctness.
    """
    api = LoremIpsumAPI("test_account", "test_password", "test")
    db = BS_PRODUCT_DATABASE

    should_be_none = api.inventory_lookup("fake_sku")
    assert should_be_none is None

    for product_sku in db.keys():
        inventory = api.inventory_lookup(product_sku)
        assert inventory is not None

        if product_sku == "003":
            assert inventory.keys.count("Philadelphia")
            assert inventory.keys.count("London")
            assert inventory["London"] == 2
