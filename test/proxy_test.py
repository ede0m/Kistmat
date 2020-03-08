import requests

s = requests.Session()

proxyList = ['https://72.35.40.34:8080','https://75.151.213.85:8080', 'https://138.68.8.149:8080']
usable_IP = []
url = 'https://httpbin.org/ip'

for item in proxyList:
    try: 	
	    r2 = requests.get(url, proxies = {'https' : item}, verify=False)
	    if r2.status_code == 200:
	        print("\nIt worked! " + item + '\n')
	        usable_IP.append(item)
    except Exception as e:
    	print('\ncouldn\'t connect' + '\n')

print('\n-------------\nusable proxies: ')
print(usable_IP)
print('\n')