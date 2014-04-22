
import requests

from shipwire.common import *


class ShipwireAPI(ShipwireBaseAPI):
    def __init__(self, account_email, password, server):
        """
        Arguments 'account_email' and 'password' correspond to the
        shipwire account.  Argument 'server' must be one of
        "production", or "test".  Both correspond to Shipwire's actual
        API.
        """
        self.__email = account_email
        self.__pass = password
        self.__server = server
        assert server in ["production", "test"]

    def post_and_fetch(self, post_xml, api_uri_part):
        """
        This function posts xml to the server and returns the reply.
        Function is exposed for easy overloading for unit tests.
        """

        uri = "https://api.shipwire.com/exec/" + api_uri_part
        if self.__server == "test":
            uri = "https://api.beta.shipwire.com/exec/" + api_uri_part,
        data = str(post_xml)
        headers = {'content-type': 'application/xml'}
        response = requests.post(uri, data=data, headers=headers)
        return response.text

    def _inventory_lookup(self, sku_list):
        """
        Returns inventory data for the given list of skus.  This may imply
        multiple api calls to shipwire's api for each warehouse.  This can
        probably be threaded, but that is outside of the scope of the common
        api class.

        This function should return a dict where each key is a
        warehouse code, and the value is a list of Inventory object
        instances.

        Like so:
        { "warehouse" : [<Inventory>, ...] }
        """
        raise NotImplementedError("Inventory lookup backend..")
