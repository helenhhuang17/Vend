import datetime
import requests
import os

class Vend:
    s = requests.Session()
    s.headers.update({'User-Agent':'theharvardshop_stocktools_JS'})

    def __init__(self, company_name, user_agent, access_token):
        self.user_agent = user_agent
        self.company_name = company_name
        self.access_token = access_token
        self.base_url = "https://{}.vendhq.com/api/2.0".format(self.company_name)
        self.__params = {}
        self.data = []

    def __headers(self):
        # Set headers for request
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    def __build_build_url(self, endpoint, parameters=[]):
        # This is responsible to build request urls
        if parameters:
            p = '/'.join([str(param) for param in parameters])
            endpoint = "{}/{}".format(str(endpoint), p)
        return "{}/{}".format(self.base_url, endpoint)

    def __build_get_request(self, endpoint, parameters=None, dict=None):
        # Build GET requests
        url = self.__build_build_url(endpoint, parameters=parameters)

        try:
            response = requests.get(url, headers=self.__headers(), params=self.__params)
            if response.status_code != 200:
                raise AssertionError()

            json_response = response.json()
            return json_response
        except Exception as e:
            # FIXME handle this
            return None

    def __get_response(self, endpoint, parameters=None,params={}):
        url = self.__build_build_url(endpoint, parameters=parameters)
        r = requests.get(url,headers=self.__headers(),params=params)
        return r.json()



    def get_customers(self, id=None, code=None, email=None, since=None):
        # Get list of customers
        parameters = self.__fix_parameters({
            "id": id,
            "code": code,
            "email": email,
            "since": since
        })

        return self.__get_response('customers', parameters=parameters)

    def get_customer(self, unique_id):
        # get single customer
        parameters = self.__fix_parameters({"unique_id": unique_id})

        return self.__get_response('customers', parameters=parameters)

    def add_customer(self, data={}):
        # Add customer POST
        return self.__get_response('customers', data=data)

    def get_products(self):
        # Get list of products, this will fetch all products and add it to an list object

        return self.__get_response(endpoint='products')

    def get_product(self, unique_id):
        # get single product
        return self.__get_response(endpoint='products', parameters=[unique_id])

    def add_product(self):
        # Add product POST

        return self.__build_get_request('products', parameters=[])

    def get_sales(self, since=None, tag=None, status=[], outlet_id=None):

        """
                This will get all sales since the beginning, this is resource intensive and not recommended.
                If you specify with parameter it will return all data in that time frame
                https://developers.vendhq.com/documentation/api/0.x/register-sales.html
                in the documentation: Dont rely on being able to get all the register sales for a retailer in a single API call.
        """

        #parameters = self.__fix_parameters({'tag': tag, 'status': status,
                                        #    'outlet_id': outlet_id})

        response = self.__get_response(endpoint='search',params={"order_by":"date","order_direction":"descending","page_size":100,"type":"sales"})
        return response

    def get_sale(self, unique_id):
        return self.__get_response(endpoint='sales', parameters=[unique_id])

    def add_sale(self, ):
        return self.__build_post_request('customers', data=data)

    def __fix_parameters(self, parameters):
        for parameter in parameters.keys():
            if not parameters[parameter]:
                parameters.pop(parameter)

        return parameters
    def get_outlets(self):
        return self.__get_response(endpoint='outlets')

"""
Stock Control
Customers
Outlets
Payment Types
Products
Register Sales
Registers
Suppliers
Taxes
Users
Webhooks
"""
