
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


EU_COUNTRIES = (
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "United Kingdom",
)
EU_ISO_CODES = tuple([iso_for_country(n) for n in EU_COUNTRIES])


def is_eu(country):
    """
    Returns True if the country is a member of the European Union.
    """
    if iso_for_country(country) in EU_ISO_CODES:
        return True
    else:
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
        else:
            self.sku_list = []

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

    def _get_cached(self, product_sku):
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
        
    def _set_cached(self, product_sku, value):
        """
        Cache inventory info for a given sku.
        """
        self.cache[product_sku] = {
            "stamp" : time.time(),
            "data" : value,
            }

    #------------------------------------------------------------------
    # API-inspecific methods:

    def get_availability(self, sku, estimate_ok=True):
        """
        Returns a list of which countries for which the given sku is in
        stock.
        """
        query = self.inventory_lookup([sku], estimate_ok)[sku]
        available = []
        for warehouse, inventory in query.items():
            if inventory.quantity > 0:
                available.append(warehouse)
        
        countries = [country_for_warehouse(code) for code in available]
        return tuple(set(countries))


    def inventory_lookup(self, sku_list, estimate_ok=False):
        """
        Pass a list of SKUs to perform an inventory lookup.
        Results are a dictionary in the format of:

        {"sku" : {"warehouse" : <Inventory>}}
        """

        results = {} # {"sku" : {"warehouse" : <Inventory>}}
        missing = []
            
        if type(sku_list) in [str, unicode]:
            sku_list = [sku_list]

        # remove non-unique items:
        sku_list = list(set(sku_list))

        if estimate_ok:
            for sku in sku_list:
                entry = self._get_cached(sku)
                if entry:
                    results[sku] = entry
                else:
                    missing.append(sku)
        else:
            missing = sku_list

        if missing:
            new_items = self._inventory_lookup(missing)
            found = {}
            for warehouse, inv_list in new_items.items():
                for entry in inv_list:
                    sku = entry.code
                    if not found.has_key(sku):
                        found[sku] = {}
                    found[sku][warehouse] = entry
                    
            for sku, data in found.items():
                results[sku] = data
                self._set_cached(sku, data)

        return results


    def optimal_order_splitting(self, shipping_address, cart):
        """
        Returns a SplitCart object which contains the most practical split
        for situations when the order cannot be fulfilled from just
        one location, and a list of SKUs that couldn't be shipped.

        Shipwire does this to an extent in their backend, but it is
        proprietary, and does not assume domestic shipping is better
        than not splitting the order.
        """

        def cart_split(stock, sku_req):
            """
            Determines recusively which warehouses can fulfill most of the
            sku_req.
            """

            splits = {} # { "warehouse" : { "sku" : quantity } }
            versions = {} # { "warehouse" : { "sku" : quantity } }
            remainder = {} # { "sku" : quantity }

            # for each warehouse, determine which subset of product
            # can be served by it:
            for warehouse in stock.keys():
                versions[warehouse] = {}
                for sku, quant in sku_req.items():
                    try:
                        if stock[warehouse][sku] >= quant:
                            versions[warehouse][sku] = quant
                    except KeyError:
                        pass

            # From the possible versions, determine which warehouse
            # caught the most product in the order:
            best_wh = None
            best_ct = 0
            for wh_code, data in versions.items():
                count = len(data.keys())
                if count > best_ct:
                    best_wh = wh_code
                    best_ct = count
            if not best_wh:
                # no sku:quantity in the req could be neatly served by
                # any of the warehouses.
                return {}, sku_req
            else:
                # add the best warehouse to the order split, update
                # the remainder stocking info, and recurse on the
                # remaining warehouses.
                splits[best_wh] = versions[best_wh]
                new_req = {}
                for sku in sku_req.keys():
                    if not versions[best_wh].has_key(sku):
                        new_req[sku] = sku_req[sku]
                new_stock = {}
                for code in stock.keys():
                    if code != best_wh:
                        new_stock[code] = stock[code]

                if len(new_req.keys()) > 0 and len(new_stock.keys()) > 0:
                    new_split, new_remainder = cart_split(new_stock, new_req)
                    for key, val in new_split.items():
                        splits[key] = val
                    return splits, new_remainder

                else:
                    return splits, new_req

        def add_regional_data(stock, warehouse, inventory):
            """
            Used for splitting inventory_lookup into regional stocking
            information.
            """
            if not stock.has_key(warehouse):
                stock[warehouse] = {}
            stock[warehouse][inventory.code] = inventory.quantity

        # generate regional stocking info based on shipping address:
        domestic = {}
        intl = {}
        query = self.inventory_lookup(cart.sku_list, estimate_ok=False)
        for sku, data in query.items():
            for warehouse, inventory in data.items():
                if inventory.quantity > 0:
                    if is_domestic(shipping_address, warehouse):
                        add_regional_data(domestic, warehouse, inventory)
                    else:
                        add_regional_data(intl, warehouse, inventory)

        # traveling salesman setup
        results = {}
        remainder = {}
        for sku in cart.sku_list:
            if remainder.has_key(sku):
                remainder[sku] += 1
            else:
                remainder[sku] = 1

        if domestic:
            # The portion of the cart that can be shipped entirely
            # from the domestic set is returned into 'results' (dict
            # warehouse:[sku...]) or such.  Returned "remainder"
            # contains everything else.
            results, remainder = cart_split(domestic, remainder)

        if remainder and intl:
            # The portion of the cart that can be shipped entirely
            # from international warehouses is returned into
            # 'intl_results', if necessary.  Returned "remainder" is
            # everything that couldn't be shipped.
            intl_results, remainder = cart_split(intl, remainder)

            for warehouse, sku_list in intl_results.items():
                if results.has_key(warehouse):
                    results[warehouse] += intl_results[warehouse]
                else:
                    results[warehouse] = intl_results[warehouse]

        # FIXME:
        # 
        # Handling for quantities that can't be served by an
        # individual warehouse but can be either partially or fully
        # servered by several.
        #

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

    def _inventory_lookup(self, sku_list):
        """
        Returns inventory data for the given list of skus.  This may imply
        multiple api calls to shipwire's api for each warehouse.  This
        can probably be threaded, but that is outside of the scope of
        the common api class.

        This function should return a dict where each key is a
        warehouse code, and the value is a list of Inventory object
        instances.

        Like so:
        { "warehouse" : [<Inventory>, ...] }

        """
        raise NotImplementedError("Inventory lookup backend..")

    def _get_single_cart_quotes(self, ship_address, warehouse, cart):
        """
        Returns the shipping quotes for a given cart of items and warehouse.
        """
        raise NotImplementedError("Shipping quotes backend.")

    def _place_single_cart_order(self, ship_address, warehouse, cart, ship_method):
        """
        Places an order for a given warehouse and cart of items.  Generally
        better to call this indirectly via the "place_order" method.
        """
        raise NotImplementedError("Order placement backend.")
