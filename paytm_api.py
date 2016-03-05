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
		return response




	def updateCatalogListing(self, sku_list, quantity_list, price_list=None, mrp_list=None, status_list=None):
		if self.sandbox == True:
			url = 'https://catalogadmin-dev.paytm.com/v1/merchant/%s/product.json' % self.merchant_id
		else:
			url = 'https://catalogadmin.paytm.com/v1/merchant/%s/product.json' % self.merchant_id

		payload = {'data':[]}

		if mrp_list == None:
			for sku, qty in zip(sku_list, quantity_list):
				payload['data'].append({'paytm_sku':sku,
										'qty':qty})
		else:
			for sku, price, qty, mrp, status in zip(sku_list, price_list, quantity_list, mrp_list, status_list):
				payload['data'].append({'sku':sku,
										'qty':qty,
										'mrp':mrp,
								   		'price':price,
								   		'status':status,
								   		'override_price':'yes'})

		params = {'authtoken':self.token}
		headers = {'Content-Type':'application/json'}

		response = self.Session.post(url, headers = headers, params=params , data = json.dumps(payload))
		return response





	def getCookie(self):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/authorize'
		else:
			url = 'https://fulfillment.paytm.com/authorize'

		params = {'authtoken':self.token}

		response = self.Session.get(url, params = params)
		return response.json()






	def fetchOrders(self, limit=None, order_ids_list=None, status=None):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/orders.json' % self.merchant_id
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/orders.json' % self.merchant_id



		try:
			order_ids = ','.join(order_ids_list)    # '''Order ids should be string type.'''
			params = {'authtoken':self.token,
				  'limit':limit,
				  'order_ids':order_ids,
				  'status':status}
		except TypeError:
			order_ids = None
			params = {'authtoken':self.token,
				  'limit':limit,
				  'order_ids':order_ids,
				  'status':status}

		headers = {'Connection':'keep-alive',
				   'Cache-Control':'max-age=0'}

		response = self.Session.get(url, headers=headers ,params=params)
		return response






	def acknowledgeOrder(self, order_id, order_item_id_list):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/fulfillment/ack/%s' % (self.merchant_id, order_id)
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/fulfillment/ack/%s' % (self.merchant_id, order_id)


		'''
		This method will take any valid order id and return the corresponding status.
		If status or that order id is 2 then it will be changeds to 5 and order id will move to acknowledged.
		If status is different than 2 then a corresponding error msg will occur.

		order_id and item_ids in params are of int type.
		'''

		params = {'authtoken':self.token}

		payload = {'item_ids':order_item_id_list,
				   'status':1}

		response = self.Session.post(url, params=params, data=payload)
		return response






	def fetchCourierPartner(self, order_id):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/shippers' % self.merchant_id
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/shippers' % self.merchant_id

		params = {'authtoken':self.token,
				  'order_id':order_id}

		response = self.Session.get(url, params=params)
		return response





	def createShipment(self, order_id, shipping_description, tracking_url, shipper_id, order_item_id):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/fulfillment/create/%s' % (self.merchant_id, order_id)
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/fulfillment/create/%s' % (self.merchant_id, order_id)

		headers = {'Content-Type':'application/json'}
		params = {'authtoken':self.token}
		payload = {'shipping_description':shipping_description,
				   'shipper_id':shipper_id,
				   'tracking_URL':tracking_url,
				   'order_item_ids':[order_item_id]}

		response = self.Session.post(url, data=json.dumps(payload), headers=headers, params=params)
		return response







	def fetchPackingLabel(self, fulfillment_ids_list):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/fulfillment/pdf/bulkfetch'  % self.merchant_id
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/fulfillment/pdf/bulkfetch'  % self.merchant_id


		fulfill_ids = ','.join(fulfillment_ids_list)

		params = {'authtoken':self.token,
				  'fulfillment_ids':fulfill_ids,
				  'template':'shared',
				  'ffUpdate':True}

		response = self.Session.get(url, params=params)
		return response



	def fetchFulfillments(self, order_item_id=None):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/fulfillments.json' % self.merchant_id
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/fulfillments.json' % self.merchant_id

		params = {'authtoken':self.token,
				  'order_item_id':order_item_id}

		response = self.Session.get(url, params=params)
		return response




	def createManifest(self, fulfillment_ids_list = None):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/fulfillment/manifest'  % self.merchant_id
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/fulfillment/manifest'  % self.merchant_id


		try:
			fulfillment_id_string = ','.join(fulfillment_ids_list)
			payload = {'fulfillment_ids':fulfillment_id_string}
		except TypeError:
			print 'No fulfillment id provided.'
			payload = {}

		params = {'authtoken':self.token}
		response = self.Session.post(url, params=params, data=payload)
		return response




	def downloadManifest(self, manifest_id_list):
		if self.sandbox == True:
			url = 'https://fulfillment-dev.paytm.com/v1/merchant/%s/fulfillment/download/manifest' % self.merchant_id
		else:
			url = 'https://fulfillment.paytm.com/v1/merchant/%s/fulfillment/download/manifest' % self.merchant_id
		
		manifest_id_string = ','.join(manifest_id_list)
		params = {'authtoken':self.token,
				  'manifest_id': manifest_id_string}

		response = self.Session.get(url, params=params)
		return response