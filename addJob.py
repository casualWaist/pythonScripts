# using shopvox's api to add a new job for testing

import requests
import json

aID = '*'
token = '*'
creds = '&account_id=%s&authToken=%s' % (aID, token)

values = {
    "job": {
      "companyName": "Walk-In",
      "companyId": "",
      "contactName": "",
      "contactId": "",
      "name": "Post Test",
      "description": "",
      "poNumber": "",
      "quantity": 2,
      "dueDate": "2019-11-10",
      "dueDateFrom": "2019-11-10",
      "billingAddressName": "",
      "billingAddressStreet": "",
      "billingAddressStreet1": "",
      "billingAddressCity": "",
      "billingAddressState": "",
      "billingAddressZip": "",
      "billingAddressCountry": "",
      "shippingAddressName": "",
      "shippingAddressStreet": "",
      "shippingAddressStreet1": "",
      "shippingAddressCity": "",
      "shippingAddressState": "",
      "shippingAddressZip": "",
      "shippingAddressCountry": "",
      "designDetails": "",
      "productionDetails": "",
      "shippingDetails": "",
      "installDetails": "",
      "workflow": "",
      "productionManager": "",
      "projectManager": "",
      "salesRep": "",
      "shippingMethod": ""
    }
  }

url = 'https://api.shopvox.com/v1/jobs/?%s' % creds

post = requests.post(url, json=values)

data = json.loads(post.content.decode('utf-8'))

print(data)
