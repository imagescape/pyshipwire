

from shipwire.common import *


def test_iso_for_country():
    """
    Test the function that normalizes country names into something we
    can use in queries etc.
    """

    assert iso_for_country("United States") == "USA"
    assert iso_for_country("united states") == "USA"
    assert iso_for_country("united_states") == "USA"
    assert iso_for_country("US") == "USA"
    assert iso_for_country("USA") == "USA"
    assert iso_for_country("PERU") == "PER"
    assert iso_for_country("per") == "PER"
    assert iso_for_country("PE") == "PER"
    assert iso_for_country("Canada") == "CAN"
    assert iso_for_country("canada") == "CAN"
    assert iso_for_country("ca") == "CAN"


def test_country_for_warehouse():
    """
    Tests the function that looks up a country iso code for a given
    warehouse code.
    """
    assert country_for_warehouse("PHL") == "USA"
    assert country_for_warehouse("CHI") == "USA"
    assert country_for_warehouse("LAX") == "USA"
    assert country_for_warehouse("TOR") == "CAN"
    assert country_for_warehouse("VAN") == "CAN"
    assert country_for_warehouse("UK") == "GBR"
    

def test_is_domestic():
    """
    Tests the code that determines if an address is from the same
    country as a given warehouse.
    """

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

    assert is_domestic(addr, "CHI")
    assert is_domestic(addr, "LAX")
    assert is_domestic(addr, "PHL")
    assert not is_domestic(addr, "TOR")
    assert not is_domestic(addr, "VAN")
    assert not is_domestic(addr, "UK")
