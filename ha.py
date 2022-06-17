import requests

URL = 'https://chart3.spsystem.info/pserver/chartdata_query.php?days=1&second=300&prod_code=HSIM2&data_mode=3'

res = requests.get(url=URL)

print(res.text)
print(type(res.text))
