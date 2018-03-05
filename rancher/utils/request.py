import requests
import logging

log = logging.getLogger(__name__)

class Request:
	def __init__(self, auth=None, headers=None):
		self.auth    = auth
		self.headers = headers
		# Define REST API methods
		self.get     = self.request(requests.get)
		self.put     = self.request(requests.put)
		self.post    = self.request(requests.post)
		self.delete  = self.request(requests.delete)

	def request(self, requestMethod):
		""" Get a decorated method """
		def req(url, *args, **kwargs):
			log.info("Request ({}); {}".format(requestMethod.__name__.upper(), url))
			return requestMethod(url, *args, auth=self.auth, headers=self.headers, **kwargs)
		return req

	def encode(self, url, **kwargs):
		params = kwargs
		query = "&".join(map(lambda key: "%s=%s" %(key, params[key]), params))
		if query:
			query = "?{}".format(query)
		return "{}{}".format(url, query)


if __name__ == "__main__":
	import pprint
	# Make some tests
	Request.auth = "hello"
	Request.headers = "hi"
	r = Request()
	print(r.auth, r.headers)