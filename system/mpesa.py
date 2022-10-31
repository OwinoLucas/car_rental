import base64
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import json
import pdb

time = datetime.now()
now = time.strftime("%Y%m%d%H%M%S")
print(now)
passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
encode_data = "{0}{1}{2}".format(
    str(174379), passkey, now)

encoded = base64.b64encode(encode_data.encode())
# print(encoded)
decoded_password = encoded.decode('utf-8')
print(decoded_password)
consumer_key = "DnOz4VuK1gQHOhlVWKfUDuchjHsq7r0m"
consumer_secret = "TUG9BBO67yS2aA2T"
api_URL ="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
r = requests.request("GET",api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
print(r.json())
json_response = r.json()

my_access_token = json_response['access_token']


def lipa_na_mpesa(total_amount, phoneNumber):

    access_token = my_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
    'Authorization': 'Bearer %s' % access_token
    }

    payload = {
        "BusinessShortCode": "174379",
        "Password": decoded_password,
        "Timestamp": now,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": total_amount,
        "PartyA": phoneNumber,
        "PartyB": "174379",
        "PhoneNumber": phoneNumber,
        "CallBackURL": "https://mydomain.com/path",
        "AccountReference": "Car Rental",
        "TransactionDesc": "Pay to Car Rentals"
    }

    response = requests.request("POST", api_url, headers = headers, json = payload)
    # pdb. set_trace()
 

    print(response.text)





