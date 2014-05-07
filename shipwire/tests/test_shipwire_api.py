
from StringIO import StringIO

from lxml import etree

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

    for warehouse in WAREHOUSE_CODES:
        api._add_response("""
    <?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE InventoryUpdateResponse SYSTEM "http://www.shipwire.com/exec/download/InventoryUpdateResponse.dtd">
<InventoryUpdateResponse>
  <Status>0</Status>
  <Product code="fake_sku_0001" quantity="2" pending="0" good="2" backordered="0" reserved="0" shipping="0" shipped="18" consuming="0" creating="0" consumed="0" created="0" shippedLastDay="0" shippedLastWeek="0" shippedLast4Weeks="0" orderedLastDay="0" orderedLastWeek="0" orderedLast4Weeks="0"/>
  <Product code="fake_sku_0002" quantity="2" pending="0" good="2" backordered="0" reserved="4" shipping="1" shipped="37" consuming="0" creating="0" consumed="0" created="0" shippedLastDay="0" shippedLastWeek="3" shippedLast4Weeks="12" orderedLastDay="0" orderedLastWeek="3" orderedLast4Weeks="13"/>
  <TotalProducts>2</TotalProducts>
  <ProcessingTime units="ms" host="w1.lwb.shipwire.com">53</ProcessingTime>
</InventoryUpdateResponse>
        """.strip())

    def request_check(api, post_xml, api_uri_part):
        # this will blow up if the request is badly formatted
        fileob = StringIO(post_xml)
        root = etree.parse(fileob).xpath("/InventoryUpdate")[0]
        user = root.xpath("Username")[0].text
        passwd = root.xpath("Password")[0].text
        server = root.xpath("Server")[0].text
        warehouse = root.xpath("Warehouse")[0].text
        codes = root.xpath("ProductCode")
        assert user == api._ShipwireAPI__email
        assert passwd == api._ShipwireAPI__pass
        assert server == api._ShipwireAPI__server
        assert warehouse in WAREHOUSE_CODES

        assert len(codes) == 2
        for code in codes:
            assert code.text in ["fake_sku_0001", "fake_sku_0002"]
        
    api.test_hook = request_check

    sku_set = ["fake_sku_0001", "fake_sku_0002"]
    report = api._inventory_lookup(sku_set)
    assert api.requests_made > 0
    assert type(report) == dict
    assert len(report.keys()) > 0
    for warehouse, stock in report.items():
        assert warehouse in WAREHOUSE_CODES
        assert type(stock) == list
        for inventory in stock:
            assert inventory.code in sku_set
            assert inventory.quantity == 2


def test_shipping_query():
    """
    Tests ShipwireAPI._get_single_cart_quotes.
    """
    api = MutedShipwireAPI(
        "nobody@donotreply.pleasedonotregisterthistld",
        "123456", 
        "production")

    api._add_response("""
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE 
RateResponse SYSTEM "http://www.shipwire.com/exec/download/RateResponse.dtd">
<RateResponse>
  <Status>OK</Status>
  <Order sequence="1">
    <Quotes>
      <Quote method="GD">
        <Warehouse>Chicago</Warehouse>
        <Service deliveryConfirmation="YES" trackable="YES"
        signatureRequired="NO">FedEx Ground</Service>
        <CarrierCode>FDX GD</CarrierCode>
        <Cost currency="USD" converted="NO" originalCurrency="USD"
        originalCost="34.90">34.90</Cost>
        <Subtotals>
          <Subtotal type="Freight">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="25.90">25.90</Cost>
          </Subtotal>
          <Subtotal type="Insurance">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="9.00">9.00</Cost>
          </Subtotal>
          <Subtotal type="Packaging">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="0.55">0.55</Cost>
          </Subtotal>
          <Subtotal type="Handling" includedInCost="NO">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="0.00">0.00</Cost>
          </Subtotal>
        </Subtotals>
        <DeliveryEstimate>
          <Minimum units="days">1</Minimum>
          <Maximum units="days">5</Maximum>
        </DeliveryEstimate>
      </Quote>
      <Quote method="2D">
        <Warehouse>Chicago</Warehouse>
        <Service deliveryConfirmation="YES" trackable="YES"
        signatureRequired="NO">UPS Second Day Air</Service>
        <CarrierCode>UPS 2D</CarrierCode>
        <Cost currency="USD" converted="NO" originalCurrency="USD"
        originalCost="98.71">98.71</Cost>
        <Subtotals>
          <Subtotal type="Freight">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="88.96">88.96</Cost>
          </Subtotal>
          <Subtotal type="Insurance">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="9.75">9.75</Cost>
          </Subtotal>
          <Subtotal type="Packaging">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="0.56">0.56</Cost>
          </Subtotal>
          <Subtotal type="Handling" includedInCost="NO">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="0.00">0.00</Cost>
          </Subtotal>
        </Subtotals>
        <DeliveryEstimate>
          <Minimum units="days">2</Minimum>
          <Maximum units="days">2</Maximum>
        </DeliveryEstimate>
      </Quote>
      <Quote method="1D">
        <Warehouse>Chicago</Warehouse>
        <Service deliveryConfirmation="YES" trackable="YES"
        signatureRequired="NO">USPS Express Mail</Service>
        <CarrierCode>USPS XP</CarrierCode>
        <Cost currency="USD" converted="NO" originalCurrency="USD"
        originalCost="141.89">141.89</Cost>
        <Subtotals>
          <Subtotal type="Freight">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="135.14">135.14</Cost>
          </Subtotal>
          <Subtotal type="Insurance">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="6.75">6.75</Cost>
          </Subtotal>
          <Subtotal type="Packaging">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="0.55">0.55</Cost>
          </Subtotal>
          <Subtotal type="Handling" includedInCost="NO">
            <Cost currency="USD" converted="NO" originalCurrency="USD"
            originalCost="0.00">0.00</Cost>
          </Subtotal>
        </Subtotals>
        <DeliveryEstimate>
          <Minimum units="days">1</Minimum>
          <Maximum units="days">1</Maximum>
        </DeliveryEstimate>
      </Quote>
    </Quotes>
    <Warnings>
      <Warning>Order was marked residential; now marked
      commercial</Warning>
    </Warnings>
  </Order>
  <ProcessingTime units="ms" host="w1.lwb.shipwire.com">
  790</ProcessingTime>
</RateResponse>
        """.strip())

    def request_check(api, post_xml, api_uri_part):
        # this will blow up if the request is badly formatted
        fileob = StringIO(post_xml)
        root = etree.parse(fileob).xpath("/RateRequest")[0]
        user = root.xpath("Username")[0].text
        passwd = root.xpath("Password")[0].text
        server = root.xpath("Server")[0].text
        order = root.xpath("Order")[0]
        addr = order.xpath("AddressInfo")[0]
        items = order.xpath("Item")
        assert len(items) == 2

    api.test_hook = request_check

    addr = AddressInfo(
        "Some Body",
        "12345 S Someplace Rd",
        "",
        "Duster",
        "IN",
        "United States",
        "47999",
        "123-4567",
        "nobody@donotreply.pleasedonotregisterthistld",
    )
    warehouse = "CHI"
    cart = CartItems()
    cart.add_item("fake_sku_1", 1)
    cart.add_item("fake_sku_2", 10)

    report = api._get_single_cart_quotes(addr, warehouse, cart)
    for code, data in report.items():
        assert SHIPPING.has_key(code)
        assert SHIPPING[code] == data[0]
        assert data[1] > 0


def test_order_placement():
    """
    Tests ShipwireAPI._place_single_cart_order.
    """
    assert False

