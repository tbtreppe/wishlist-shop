
import urllib
import requests

# set the api key in headers
headers = {
    "apikey": '2797b24d-1fef-4568-89ac-45423bf372d6'
}

# format the query
# q: the search term
# hl: return results in English
query = {
    "q": "photo of blue jeans",
    "hl": "en"
}

# build to url to make request
url = f"https://api.goog.io/v1/images/" + urllib.parse.urlencode(query)

resp = requests.get(url, headers=headers)
results = resp.json()
print(results)

# run in ipython to test and make sure it works. can change query here to check