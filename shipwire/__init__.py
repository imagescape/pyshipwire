



class ShipwireAPI (object):
    """
    This class wraps the shipwire API.  Instance it and use the class's
    methods to perform shipwire API calls.
    """

    def __init__(self, account_email, password, server):
        """
        Arguments 'account_email' and 'password' correspond to the
        shipwire account.  Argument 'server' must be one of
        "production", "test", or None.  If None, no calls to the
        shipwire service will be made.  None is used for debugging,
        and will use a fake "database" of product SKUs.
        """
        self.__email = account_email
        self.__pass = password

        assert server in ["production", "test", None]
        self.__server = server

    def inventory_lookup(self, product_sku):
        """
        """
        # FIXME don't generically return arbitrary data :P
        return [
            ("USA", 10),
            ("UK", 10),
        ]
                
    def get_shipping_options(self, shipping_address, cart):
        pass

    def place_order(self, shipping_address, warehouse, cart, shipping_method):
        pass
