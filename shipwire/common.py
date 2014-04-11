
import os
import time
import csv
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

LOCAL_SHIPPING = ("GD", "2D", "1D")
INTL_SHIPPING = ("E-INTL", "INTL", "PL-INTL", "PM-INTL")



countries_path = os.path.join(os.path.split(__file__)[0], "countries.csv")
with open(countries_path, "r") as countries_file:
    COUNTRIES = tuple([tuple(line) for line in csv.reader(countries_file)])
del countries_path
del countries_file


def iso_for_country(country):
    """
    Determines the 3 letter iso code for a given country name which may
    be formatted as either an iso code (2 or 3 letters) or the common
    name.
    """
    for line in COUNTRIES:
        normalized_line = [i.upper() for i in line]
        normalized_target = country.upper().replace("_", " ")
        if normalized_line.count(normalized_target):
            return line[-1]
    return None


def country_for_warehouse(warehouse_code):
    """
    Returns the 3 letter iso country code for which a given warehouse
    is located.
    """
    for country_name, country_set in WAREHOUSES.items():
        if country_set.has_key(warehouse_code):
            return iso_for_country(country_name)
    return None


def is_domestic(shipping_address, warehouse_code):
    """
    Returns true if a shipping address and warehouse are in the same
    country as one another, otherwise returns False.
    """
    shipping_country = iso_for_country(shipping_address.country)
    warehouse_country = country_for_warehouse(warehouse_code)
    if shipping_country is not None and warehouse_country is not None:
        return shipping_country == warehouse_country
    else:
        # FIXME: maybe raise an error here?
        return False


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


class CartItems(object):
    """
    Class storing shopping cart information.
    """
    def __init__(self, sku_list=None):
        if sku_list is not None:
            self.sku_list = sku_list

    def add_item(self, sku, quantity):
        """Add some quantity of SKUs to the cart."""
        for i in range(quantity):
            self.sku_list.append(sku)


class SplitCart(object):
    """
    Class representing an order split.
    """
    def __init__(self):
        self.order_split = {}

    def add_cart(self, warehouse, cart):
        assert type(cart) == CartItems
        assert warehouse in WAREHOUSE_CODES
        self.order_split[warehouse] = cart


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
            inventory = [self._inventory_for_warehouse(product_sku, w) \
                         for w in WAREHOUSE_CODES]
            result = dict(zip(WAREHOUSE_CODES, inventory))
            self.__set_cached(product_sku, result)
            return result

    def optimal_order_splitting(self, shipping_address, cart):
        """
        Returns a SplitCart object which contains the most practical split
        for situations when the order cannot be fulfilled from just
        one location, and a list of SKUs that couldn't be shipped.

        Shipwire does this to an extent in their backend, but it is
        proprietary, and does not assume domestic shipping is better
        than not splitting the order.
        """
        
        # The way this should work:

        # 1. Generate a subset of warehouses that are domestic to the
        # shipping address.

        ## a. for each warehouse in the subset, for each unique sku in
        ## the cart, poll the availability of the items in the
        ## domestic warehouse set.

        ## b. determine which warehouse is able to provide the most of
        ## the items in the cart.  Place those into a new cart (tagged
        ## with the warehouse), subtract the quantities from the
        ## cached inventory results for that warehouse.  Remove the
        ## warehouse from the cached inventory results.  Repeat until
        ## no items remaining in the cart can be satisfied by any of
        ## the warehouses OR until there are no items remaining in the
        ## cart.

        # 2. Generate a subset of warehouses that are not domestic to the
        # shipping address.

        ## a. use the algorithm described for step 1, but with
        ## warehouses that are relatively international to the
        ## shipping address.

        # NOTE, if there is a tie between two warehouses, the tie
        # should be broken by shipping cost.

        def cart_split(warehouse_set, sku_list):
            """
            Takes a list of warehouses and a cart object.  Returns a dict that
            splits the cart, and a cart containing remaining skus.
            """
            ## FIXME
            return {}, sku_list

        # Generate the list of warehouses that are domestic to the
        # shipping address, and those that are not:
        domestic = []
        intl = []
        for warehouse in WAREHOUSE_CODES:
            if is_domestic(shipping_address, warehouse):
                domestic.append(warehouse)
            else:
                intl.append(warehouse)

        results = {}
        remainder = cart.sku_list

        if domestic:
            results, remainder = cart_split(domestic, remainder)

        if intl:
            intl_results, remainder = cart_split(intl, remainder)
            for warehouse, sku_list in intl_results.items():
                if results.has_key(key):
                    results[warehouse] += intl_results[warehouse]
                else:
                    results[warehouse] = intl_results[warehouse]
            
        split_cart = SplitCart()
        for warehouse, sku_list in results.items():
            split_cart.add_cart(warehouse, CartItems(sku_list))
        return split_cart, remainder

    def get_shipping_options(self, shipping_address, split_cart):
        """
        The parameter 'cart' is an instance of the SplitCart class.
        
        Returns a dictionary in which the keys are warehouse codes,
        and the values are the shipping quotes for the carts
        corresponding to that warehouse.

        Use the "optimal_order_splitting" method to generate
        'split_cart'.
        """
        assert type(shipping_address) == AddressInfo
        assert type(split_cart) == SplitCart

        split_options = {}
        for warehouse, cart in split_cart.order_split.items():
            split_options[warehouse] = self._get_single_cart_quotes(
                shipping_address, warehouse, cart)
        return split_options
        
    def place_order(self, shipping_address, split_cart, shipping_methods):
        """
        The parameter 'cart' is an instance of the SplitCart class.

        The parameter 'shipping_methods' is a dict who's keys are
        warehouse codes and who's values are shipping codes.

        Raises an error if any of the orders failed to place, so be
        sure to catch for that.

        Use the "optimal_order_splitting" method to generate
        'split_cart'.
        """
        assert type(shipping_address) == AddressInfo
        assert type(split_cart) == SplitCart
        assert type(shipping_methods) is dict
        for warehouse, shipping in shipping_methods.items():
            assert warehouse in WAREHOUSE_CODES
            assert shipping in SHIPPING.keys()

        api_results = []

        for warehouse, cart in split_cart.order_split.items():
            method = shipping_methods[warehouse]
            api_results.append(
                self._place_single_cart_order(
                    shipping_address, warehouse, cart, method))
        return api_results

    #------------------------------------------------------------------
    # Backend-specific methods:

    def _inventory_for_warehouse(self, product_sku, warehouse):
        """Shipwire's api doesn't say the per-warehouse stocking information
        if you query per product.  The solution is to query it for
        each warehouse.  Use the "inventory_lookup" for this data in
        agregate.
        """
        raise NotImplementedError("Inventory Lookup")
        pass

    def _get_single_cart_quotes(self, ship_address, warehouse, cart):
        """
        Returns the shipping quotes for a given cart of items and warehouse.
        """
        raise NotImplementedError("Shipping quotes for singular cart.")

    def _place_single_cart_order(self, ship_address, warehouse, cart, ship_method):
        """
        Places an order for a given warehouse and cart of items.  Generally
        better to call this indirectly via the "place_order" method.
        """
        raise NotImplementedError("Place order for single cart.")
