

WAREHOUSES = {
    "Chicago" : "United States",
    "Los Angeles" : "United States",
    "Philadelphia" : "United States",

    "Toronto" : "Canada",
    "Vancouver" : "Canada",

    "Rio de Janeiro" : "Brazil",

    "Hong Kong" : "China",

    "London" : "United Kingdom",

    "Frankfurt" : "Germany",

    "Sydney" : "Australia",
}


SHIPPING = {
    "GD" : "Domestic Ground Shipping (2 - 7 days)",
    "2D" : "Domestic Priority Shipping (2 - 4 days)",
    "1D" : "Domestic Express Shipping (1 - 3 days)",

    "E-INTL" : "International Economy Shipping",
    "INTL" : "International Standard Shipping",
    "PL-INTL" : "International Plus Shipping",
    "PM-INTL" : "International Premium Shipping",
}


class ShipwireBaseAPI(object):
    """
    Base class for to be used for ShipwireAPI and TestAPI.
    """
    
    def __init__(self, account_email, password, server):,
        """
        Arguments 'account_email' and 'password' correspond to the
        shipwire account.  Argument 'server' must be one of
        "production", or "test".  Both correspond to Shipwire's actual
        API.
        """
        pass

    def inventory_lookup(self, product_sku, estimate_ok=False):
        """
        Connect to shipwire and find out stocking information for a given
        product.  If estimate_ok is true, then the implementation
        might return a cached value.
        """
        pass

    def get_shipping_options(self, ship_address, cart):
        pass

    def place_order(self, ship_address, warehouse, cart, shipping_method):
        pass
