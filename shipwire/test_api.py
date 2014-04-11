
from shipwire.common import *


BS_PRODUCT_DATABASE = {
    "sku_0001" : {
        "name" : "Basic Widget",
        "stock_info" : {
            "CHI" : 10,
            "UK" : 1,
        },
    },
    "sku_0002" : {
        "name" : "Deluxe Widget",
        "stock_info" : {
            "PHL" : 2,
            "UK" : 1,
        }
    },
    "sku_0003" : {
        "name" : "Premium Widget MX PRO",
        "stock_info" : {
            "PHL" : 1,
            "UK" : 2,
        },
    },
}


TEST_RATES = {
    # arbitrary shipping rates
    "GD" : 5.0,
    "2D" : 10.0,
    "1D" : 30.0,
    "E-INTL" : 50.0,
    "INTL"   : 80.0,
    "PL-INTL" : 100.0,
    "PM-INTL" : 120.0,
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
        ShipwireBaseAPI.__init__(self, account_email, password, server)

        if server not in ["test", "production"]:
            raise ValueError("Bad target server.")

        if not (account_email == "test_account" \
                and password == "test_password" \
                and server == "test"):
            raise NotImplementedError("Fake failure for fake auth.")

    def inventory_for_warehouse(self, product_sku, warehouse):
        """
        Polls the stocking information for a given warehouse.  The method
        "inventory_lookup" calls this method to build a better report,
        so use that instead.
        """
        if BS_PRODUCT_DATABASE.has_key(product_sku):
            record = BS_PRODUCT_DATABASE[product_sku]
            try:
                stock = record["stock_info"][warehouse]
            except KeyError:
                stock = 0
            
            if stock:
                data = Inventory()
                data.code = product_sku # not sure if this is correct
                data.quantity = stock
                return data
            else:
                return None
        else:
            return None

    def get_shipping_options(self, ship_address, warehouse, cart):
        """
        The parameter 'cart' is a list of product SKUs; multiple quantites
        should be expressed by the SKU appearing in the list multiple
        times.

        This function may need to be called multiple times in the
        event that the order is split.
        """
        
        rate_set = LOCAL_SHIPPING
        if not is_domestic(ship_address, warehouse):
            rate_set = INTL_SHIPPING
        options = {}
        for code in rate_set:
            options[code] = SHIPPING[code], TEST_RATES[code] * len(cart)
        return options
        
    def place_order(self, shipping_address, warehouse, cart, shipping_method):
        """
        The parameter 'cart' is a list of product SKUs; multiple quantites
        should be expressed by the SKU appearing in the list multiple
        times.
        
        This function may need to be called multiple times in the
        event that the order is split.
        """

        raise NotImplementedError("Fake Order Placement")
