
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
