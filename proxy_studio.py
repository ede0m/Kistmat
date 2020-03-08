import requests
from urllib.parse import urlparse

def validate_proxy_url(proxy_url):
	url = urlparse(proxy_url)
	if url.scheme != 'https':
		print('please use https')
		return False
	if url.hostname == None:
		print('invalid host')
		return False
	if url.port == None:
		print('please specify a port')
		return False
	return True

def try_proxy(proxy_url):
	test_url = 'https://httpbin.org/ip'
	s = requests.Session()
	try:
		r2 = s.get(proxy_url, proxies = {'https' : proxy_url}, verify=False)
		if r2.status_code == 200:
			print('this proxy worked!')
			return True
	except Exception as e:
		print('this proxy could not connect ... \n\n' + str(e) + '\n')
		return False

def get_usable_https_proxies():
	print('Not yet supported - Coming soon!')