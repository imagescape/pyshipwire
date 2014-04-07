

from shipwire.common import *


BS_PRODUCT_DATABASE = {
    "sku_0001" : {
        "name" : "Basic Widget",
        "stock_info" : {
            "Chicago" : 10,
            "London" : 1,
        },
    },
    "sku_0002" : {
        "name" : "Deluxe Widget",
        "stock_info" : {
            "Philadelphia" : 2,
            "London" : 1,
        },
    },
    "sku_0003" : {
        "name" : "Premium Widget MX PRO",
        "stock_info" : {
            "Philadelphia" : 1,
            "London" : 2,
        },
    },
}


class LoremIpsumAPI(ShipwireBaseAPI):
    """
    LoremIpsumAPI is an implementation of ShipwireBaseAPI that can be
    used for testing purposes, without ever touching the shipwire backend.
    """

    def __init__(self, account_email=None, password=None, server=None):
        """
        All arguments are optional in this case, because they are not used
        for anything.
        """
        # FIXME: still require some authentication credentials so that
        # a connection failure can be demonstrated.
        pass
    
    def inventory_lookup(self, product_sku, estimate_ok=None):
        """
        Returns stocking information for a given product.
        """
        if BS_PRODUCT_DATABASE.has_key("product_sku"):
            return BS_PRODUCT_DATABASE["product_sku"]["stock_info"],
        else:
            return None
