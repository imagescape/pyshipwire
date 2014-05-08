
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
    "sku_0004" : {
        "name" : "Super Deluxe Premium Widget MX PRO MX",
        "stock_info" : {
            "TOR" : 1,
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

    def _inventory_lookup(self, sku_set):
        """
        Don't call this method directly; use
        inventory_lookup(product_skus, caching) instead!

        If warehouse set is None, poll for all warehouses.
        """

        def fake_stock_info(warehouse, sku):
            item = Inventory()
            item.quantity = 0
            item.code = sku

            if BS_PRODUCT_DATABASE.has_key(sku):
                record = BS_PRODUCT_DATABASE[sku]
                try:
                    item.quantity = record["stock_info"][warehouse]
                except KeyError:
                    pass
            return item
        
        report = {}
        for code in WAREHOUSE_CODES:
            report[code] = [fake_stock_info(code, sku) for sku in sku_set]
        return report

    def _place_single_cart_order(self, order_number, ship_address, warehouse, cart, ship_method):
        """
        Don't call this method directly; use
        place_order(shipping_address, split_cart) instead!

        Places an order for a given warehouse and cart of items.  Generally
        better to call this indirectly via the "place_order" method.

        Returns (status_code, order_number, transaction_id).
        """
        return ("accepted", order_number, "fake_transaction_id")

    def _get_single_cart_quotes(self, ship_address, warehouse, cart):
        """
        Don't call this method directy; use
        get_shipping_options(ship_address, split_cart) instead!

        This function fetches shipping quotes for a given warehouse
        and cart of itmes.
        """
        rate_set = LOCAL_SHIPPING
        if not is_domestic(ship_address, warehouse):
            rate_set = INTL_SHIPPING
        options = {}
        for code in rate_set:
            options[code] = SHIPPING[code], TEST_RATES[code] * len(cart.sku_list)
        return options
