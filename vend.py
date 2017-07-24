import datetime
import requests
import os
import csv
import json
import sys
from datetime import date, datetime, timedelta, time

outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}

# Convert Vend default date string into a datetime object
def convert_date(date_string):
    return(datetime.strptime(date_string,'%Y-%m-%dT%H:%M:%S+00:00')
    - timedelta(hours=4))

# Split list of sales using the times in time_splits as the barriers. The list
# is composed of time objects.
def split_sales(sales,time_splits=[]):
    next_split = time_splits.pop()
    sales_list = []
    section = []
    for sale in sales:
        if convert_date(sale['sale_date']).time() > next_split and len(time_splits):
            sales_list.append(section)
            section = []
        section.append(sale)
    return sales_list

class Vend:

    def __init__(self, company_name, user_agent, token):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent":user_agent,"Authorization": "Authorization Bearer {}".format(token)})
        self.user_agent = user_agent
        self.company_name = company_name
        self.token = token
        self.base_url = "https://{}.vendhq.com/api/2.0".format(company_name)
        self.params = []
        self.data = []
    # Takes list of parameters seperated by '/' to the endpoint URL
    def __build_url(self, endpoint, parameters=[]):
        if parameters:
            p = '/'.join([str(param) for param in parameters])
            endpoint = "{}/{}".format(str(endpoint), p)
        return "{}/{}".format(self.base_url, endpoint)

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
