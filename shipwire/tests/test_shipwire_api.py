

from shipwire.shipwire_api import *
from shipwire.common import *


class MutedShipwireAPI(ShipwireAPI):
    """
    This classed is used to mock the connection to the shipwire api
    backend, and defining custom responses for tests.
    """
    def __init__(self, *args, **kargs):
        ShipwireAPI.__init__(self, *args, **kargs)
        self.__pending_responses = []
        self.test_hook = None
        self.requests_made = 0

    def _add_response(self, response_text):
        self.__pending_responses.append(response_text)

    def post_and_fetch(self, post_xml, api_uri_part):
        self.requests_made += 1
        if self.test_hook is not None:
            self.test_hook(self, post_xml, api_uri_part)
        return self.__pending_responses.pop(0)


def test_api_query():
    """
    Test to see if the "post_and_fetch" handler works.
    Note that this may fail if the shipwire service is down.
    """

    api = ShipwireAPI(
        "nobody@donotreply.pleasedonotregisterthistld",
        "123456", 
        "production")

    api_target = "RateServices.php"
    
    raw_req = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE RateRequest SYSTEM "http://www.shipwire.com/exec/download/RateRequest.dtd">
<RateRequest>
<Username>nobody@donotreply.pleasedonotregisterthistld</Username>
<Password>123456</Password>
<Order id="12579">
<Warehouse>0</Warehouse>
<AddressInfo type="ship">
<Address1>321 Foo bar lane</Address1>
<Address2>Apartment #2</Address2>
<City>Nowhere</City>
<State>CA</State>
<Country>US</Country>
<Zip>12345</Zip>
</AddressInfo>
<Item num="0">
<Code>12345</Code>
<Quantity>1</Quantity>
</Item>
</Order>
</RateRequest>
    """.strip()

    expected_reply = """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE 
RateResponse SYSTEM "http://www.shipwire.com/exec/download/RateResponse.dtd">
<RateResponse>
  <Status>Error</Status>
  <ErrorMessage>Could not verify Username/EmailAddress and Password
  combination</ErrorMessage>
</RateResponse>
    """.strip()
    
    actual_reply = api.post_and_fetch(raw_req, api_target)
    assert actual_reply.strip() == expected_reply.strip()


def test_inventory_lookup():
    """
    Tests ShipwireAPI._inventory_lookup.
    """
    api = MutedShipwireAPI(
        "nobody@donotreply.pleasedonotregisterthistld",
        "123456", 
        "production")

    api._add_response("""
    <?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE InventoryUpdateResponse SYSTEM "http://www.shipwire.com/exec/download/InventoryUpdateResponse.dtd">
<InventoryUpdateResponse>
<Status>Test</Status>
<Product code="fake_sku_0001"
quantity="2"
good="2"
pending="300"
backordered="0"
reserved="15"
shipping="7"
shipped="7013"
consuming="0"
consumed="0"
creating="0"
created="0"
availableDate="2012-01-19"
shippedLastDay="13"
shippedLastWeek="84"
shippedLast4Weeks="401"
orderedLastDay="15"
orderedLastWeek="99"
orderedLast4Weeks="416" />
<Product code="fake_sku_0002"
quantity="2"
good="2"
pending="500"
backordered="0"
reserved="17"
shipping="0"
shipped="1997"
consuming="0"
consumed="0"
creating="0"
created="0"
availableDate="2012-02-21"
shippedLastDay="11"
shippedLastWeek="74"
shippedLast4Weeks="221"
orderedLastDay="19"
orderedLastWeek="90"
orderedLast4Weeks="242" />
<TotalProducts>2</TotalProducts>
<ProcessingTime units="ms">221</ProcessingTime>
</InventoryUpdateResponse>
    """.strip())

    def request_check(api, post_xml, api_uri_part):
        pass
    api.test_hook = request_check

    sku_set = ["fake_sku_0001", "fake_sku_0002"]
    report = api._inventory_lookup(sku_set)
    assert api.requests_made == 1
    assert type(report) == dict
    for warehouse, stock in report.items():
        assert warehouse in WAREHOUSE_CODES
        assert type(stock) == list
        for inventory in stock:
            assert inventory.code in sku_set
            assert inventory.quantity == 2
