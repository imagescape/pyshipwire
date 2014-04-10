
import time
import itertools

WAREHOUSES = {
    "United States" : {
        "CHI" : "Chicago",
        "LAX" : "Los Angeles",
        "PHL" : "Philidelphia",
    },
    "Canada" : {
        "TOR" : "Toronto",
        "VAN" : "Vancouver",
    },
    "United Kingdom" : {
        "UK" : "London",
    },
}

# the following line extracts the warehouse codes from the above dict,
# eg: ('CHI', 'LAX', 'PHL', 'TOR', 'VAN', 'UK')
WAREHOUSE_CODES =  tuple(itertools.chain(*[i.keys() for i in WAREHOUSES.values()]))
    
# FIXME:
# missing are warehouse codes for Hong Kong (China), Rio de Janeiro
# (Brazil), Frankfurt (Germany), and Sydney (Australia).  The shipwire
# api faq does not provide them, and the company this author works for
# doesn't currently use those warehouses, so trial and error via the
# api will not yeild any answers either...
# (http://www.shipwire.com/w/developers/xml-real-time-inventory-faq/)

SHIPPING = {
    "GD" : "Domestic Ground Shipping (2 - 7 days)",
    "2D" : "Domestic Priority Shipping (2 - 4 days)",
    "1D" : "Domestic Express Shipping (1 - 3 days)",

    "E-INTL" : "International Economy Shipping",
    "INTL" : "International Standard Shipping",
    "PL-INTL" : "International Plus Shipping",
    "PM-INTL" : "International Premium Shipping",
}


class AddressInfo(object):
    """
    Represents a shipping address.
    """
    def __init__(self, name, addr1, addr2, city, state, country, zipcode, phone, email):
        self.name = name
        self.addr1 = addr1
        self.addr2 = addr2
        self.city = city
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.phone = phone
        self.email = email


class Inventory(object):
    """
    Represents inventory information.
    """
    def __init__(self):
        self.code = None # sku?
        self.quantity = 0


class ShipwireBaseAPI(object):
    """
    Base class for to be used for ShipwireAPI and TestAPI.
    """
    
    def __init__(self, account_email, password, server):
        """
        Arguments 'account_email' and 'password' correspond to the
        shipwire account.  Argument 'server' must be one of
        "production", or "test".  Both correspond to Shipwire's actual
        API.
        """
        self.cache = {}
        self.cache_expire = 60*5 # seconds

    def __get_cached(self, product_sku):
        """
        If the inventory info for a given product sku is present and the
        cache stamp isn't too old, return it.  If the cache stamp is
        too old, remove it from cache and return None.  If the item is
        not present at all, return none.
        """
        if self.cache.has_key(product_sku):
            entry = self.cache[product_sku]
            if time.time() - entry["stamp"] > self.cache_expire:
                self.cache.pop(product_sku)
                return None
            else:
                return entry["data"]
        else:
            return None
        
    def __set_cached(self, product_sku, value):
        """
        Cache inventory info for a given sku.
        """
        self.cache[product_sku] = {
            "stamp" : time.time(),
            "data" : value,
            }

    #------------------------------------------------------------------
    # API-inspecific methods:

    def inventory_lookup(self, product_sku, estimate_ok=False):
        """
        Connect to shipwire and find out stocking information for a given
        product.  If estimate_ok is true, then the implementation
        might return a cached value.
        """
        cached = self.__get_cached(product_sku)
        if cached and estimate_ok:
            return cached
        else:
            inventory = [self.inventory_for_warehouse(product_sku, w) \
                         for w in WAREHOUSE_CODES]
            result = dict(zip(WAREHOUSE_CODES, inventory))
            self.__set_cached(product_sku, result)
            return result

    def optimal_order_splitting(self, ship_address, cart):
        """
        Returns a list of cart objects for the most pratical split for
        situations when the order cannot be fulfilled from just one
        location.  Shipwire does this to an extent in their backend,
        but it is optimized for sending all products from one
        location, and not optimized for shipping cost.
        
        The "cart" currently is just a list of product SKUs.
        Quantities should be expressed by having the SKU appear in the
        list multiple times.
        """
        raise NotImplementedError("Order Splitting")

    #------------------------------------------------------------------
    # Backend-specific methods:

    def inventory_for_warehouse(self, product_sku, warehouse):
        """Shipwire's api doesn't say the per-warehouse stocking information
        if you query per product.  The solution is to query it for
        each warehouse.  Use the "inventory_lookup" for this data in
        agregate.
        """
        raise NotImplementedError("Inventory Lookup")
        pass

    def get_shipping_options(self, ship_address, warehouse, cart):
        """
        The parameter 'cart' is a list of product SKUs; multiple quantites
        should be expressed by the SKU appearing in the list multiple
        times.

        This function may need to be called multiple times in the
        event that the order is split.
        """
        raise NotImplementedError("Get Shipping Options")

    def place_order(self, ship_address, warehouse, cart, shipping_method):
        """
        The parameter 'cart' is a list of product SKUs; multiple quantites
        should be expressed by the SKU appearing in the list multiple
        times.
        
        This function may need to be called multiple times in the
        event that the order is split.
        """
        raise NotImplementedError("Order Placement")
