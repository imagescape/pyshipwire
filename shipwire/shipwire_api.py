
from StringIO import StringIO
from threading import Thread
import time

from lxml import etree
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
        ShipwireBaseAPI.__init__(self, account_email, password, server)

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

        product_template = "<ProductCode>{0}</ProductCode>"
        req_template = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE InventoryUpdateResponse SYSTEM "http://www.shipwire.com/exec/download/InventoryUpdateResponse.dtd">
<InventoryUpdate>
    <Username>{0}</Username>
    <Password>{1}</Password>
    <Server>{2}</Server>
    <Warehouse>{3}</Warehouse>
    {4}
    <IncludeEmpty/>
</InventoryUpdate>
        """.strip()

        def gen_req(warehouse, sku_list):
            product_lines = "\n".join(
                [product_template.format(sku) for sku in sku_list])
            return req_template.format(
                self.__email, 
                self.__pass, 
                self.__server, 
                warehouse, 
                product_lines)
            
        requests = []
        for warehouse in WAREHOUSE_CODES:
            requests.append(gen_req(warehouse, sku_list))

        class ReqThread(Thread):
            """
            Performing the requests one after another is too slow.  This class
            wraps the post_and_fetch call so that several can be ran
            in parallel.
            """
            def __init__(self, api, request):
                self.data = ""
                self.req = request
                self.api = api
                Thread.__init__(self)
            def run(self):
                self.data = self.api.post_and_fetch(
                    self.req, "InventoryServices.php")

        start_time = time.time()
        pool = [ReqThread(self, req) for req in requests]
        for thread in pool:
            thread.start()
        for thread in pool:
            thread.join()
        total = time.time()-start_time
        responses = [thread.data for thread in pool]

        report = {}
        for warehouse, raw in zip(WAREHOUSE_CODES, responses):
            # note that lxml blows up when you pass it unicode
            fileob = StringIO(str(raw))
            root = etree.parse(fileob).xpath("/InventoryUpdateResponse")[0]
            items = []
            for entry in root.xpath("Product"):
                inv = Inventory()
                inv.code = entry.attrib["code"]
                inv.quantity = int(entry.attrib["quantity"])
                items.append(inv)
            report[warehouse] = items

        return report
