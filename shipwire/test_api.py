

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

    def __init__(self, account_email, password, server):
        """
        Arguments 'account_email' and 'password' correspond to the
        shipwire account.  Argument 'server' must be one of
        "production", or "test".  Both correspond to Shipwire's actual
        API.
        """

        if server not in ["test", "production"]:
            raise ValueError("Bad target server.")

        if not (account_email == "test_account" \
                and password == "test_password" \
                and server == "test"):
            raise NotImplementedError("Fake failure for fake auth.")
    
    def inventory_lookup(self, product_sku, estimate_ok=None):
        """
        Returns stocking information for a given product.
        """
        if BS_PRODUCT_DATABASE.has_key(product_sku):
            return BS_PRODUCT_DATABASE[product_sku]["stock_info"]
        else:
            return None
