import requests
import json

class Paytm:
	def __init__(self, merchant_id, username, password, client_id, client_secret, sandbox=False):
		self.merchant_id = merchant_id
		self.username = username
		self.password = password
		self.client_id = client_id
		self.client_secret = client_secret
		self.sandbox = sandbox

		self.Session = self.getSession()
		self.token = self.getToken()




	def getSession(self):
		session = requests.Session()
		return session




	def getAuthCode(self):
		if self.sandbox == True:
			url = 'https://persona-dev.paytm.com/oauth2/authorize'
		else:
			url = 'https://persona.paytm.com/oauth2/authorize'

		payload = {'username':self.username,
				   'password':self.password,
				   'client_id':self.client_id,
				   'notredirect':True,
				   'response_type':'code'}

		response = self.Session.post(url, data=payload)
		code = response.json()['code']
		return code




	def getToken(self):
		if self.sandbox == True:
			url = 'https://persona-dev.paytm.com/oauth2/token'
		else:
			url = 'https://persona.paytm.com/oauth2/token'

		code = self.getAuthCode()

		payload = {'grant_type':'authorization_code',
				   'code':code,
				   'client_id':self.client_id,
				   'client_secret':self.client_secret}

		response = self.Session.post(url, data=payload)
		token = response.json()['access_token']
		return token





	def getCatalogListing(self, status=None, is_in_stock=None, limit=None, after_id=None, before_id=None, sku=None):
		if self.sandbox == True:
			url = 'https://catalogadmin-dev.paytm.com/v1/merchant/%s/catalog.json' % self.merchant_id
		else:
			url = 'https://catalogadmin.paytm.com/v1/merchant/%s/catalog.json' % self.merchant_id

		params = {'authtoken':self.token,
				  'status':status,
				  'is_in_stock':is_in_stock,
				  'stock':1,
				  'limit':limit,
				  'after_id':after_id,
				  'before_id':before_id,
				  'columns':'Thumbnail',
				  'skus':sku}

		response = self.Session.get(url, params =params)
		return response.json()



	def updateCatalogListing(self, sku_list, price_list, qty_list, mrp_list, status_list):
		if self.sandbox == True:
			url = 'https://catalogadmin-dev.paytm.com/v1/merchant/%s/product.json' % self.merchant_id
		else:
			url = 'https://catalogadmin.paytm.com/v1/merchant/%s/product.json' % self.merchant_id

		payload = {'data':[]}

		for sku, price, qty, mrp, status in zip(sku_list, price_list, qty_list, mrp_list, status_list):
			payload['data'].append({'sku':sku,
								   'mrp':mrp,
								   'price':price,
								   'qty':qty,
								   'status':status,
								   'override_price':'yes'})

		params = {'authtoken':self.token}
		headers = {'Content-Type':'application/json'}

		response = self.Session.post(url, headers = headers, params=params , data = json.dumps(payload))
		return response.json()




	def getCookie(self):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/authorize'
		else:
			url = 'https://fulfillment.paytm.com/authorize'

		params = {'authtoken':self.token}

		response = self.Session.get(url, params = params)
		return response.json()





	def fetchOrders(self, limit=None, order_ids=None, status=None):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/orders.json' % self.merchant_id
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/orders.json' % self.merchant_id

		params = {'authtoken':self.token,
				  'limit':limit}

		headers = {'Connection':'keep-alive',
				   'Cache-Control':'max-age=0'}

		response = self.Session.get(url, headers=headers ,params=params)
		return response.json()

	def acknowledgeOrder(self, order_id, item_ids):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/fulfillment/ack/%s' % (self.merchant_id, order_id)
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/fulfillment/ack/%s' % (self.merchant_id, order_id)

		params = {'authtoken':self.token}

		payload = {'item_ids':item_ids,
				   'status':1}

		response = self.Session.post(url, params=params, data=payload)
		return response.json()



# x = Paytm(21492, 'api.integration@paytm.com', 'paytm123', 'api-int', '251b2340185643ac7522ceee74287b5b', sandbox=True)
# order_id = 1194469775
# item_id = [1232622181]
# print x.acknowledgeOrder(order_id, item_id)
# # print x.fetchOrders(status=2, limit=3)