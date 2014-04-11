

from shipwire.shipwire_api import *
from shipwire.common import *


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
