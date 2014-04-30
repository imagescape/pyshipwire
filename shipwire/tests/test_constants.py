

from shipwire.common import *


def test_warehouses():
    """
    Test to see if warehouse data exists for all available
    jurisdictions.
    """
    assert WAREHOUSES.has_key("United States")
    assert WAREHOUSES.has_key("Canada")
    assert WAREHOUSES.has_key("United Kingdom")
    assert WAREHOUSES.has_key("China")
    assert WAREHOUSES.has_key("Brazil")
    assert WAREHOUSES.has_key("Germany")
    assert WAREHOUSES.has_key("Australia")


def test_shipping_options():
    """
    Test to see if all available shipping options are present.
    """
    assert SHIPPING.has_key("GD")
    assert SHIPPING.has_key("2D")
    assert SHIPPING.has_key("1D")
    assert SHIPPING.has_key("E-INTL")
    assert SHIPPING.has_key("INTL")
    assert SHIPPING.has_key("PL-INTL")
    assert SHIPPING.has_key("PM-INTL")


def test_eu():
    """
    Test the is_eu function.
    """
    for country in EU_COUNTRIES: 
        assert is_eu(country)

    not_eu = [
        "United States",
        "Canada",
        "The Moon",
        "Peru",
        "Hutzselvania",
        "Madagascar",
    ]
    for country in not_eu:
        assert not is_eu(country)
