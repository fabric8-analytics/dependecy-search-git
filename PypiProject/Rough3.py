import time
from collections import defaultdict
import requests
from pypidesckeywords.manifestload import LocalLoadProcess

api_token = "f753f9550d2ff8616a7cd9c8688236c517d23140"

json = {
    'query': '{{organization(login: "{0}"){{name url repository(name: "{1}")\
         {{name url description repositoryTopics(first: 100){{nodes{{topic {{name}}}}}}}}}}}}'
        .format(str('eofs'), str('aws'))}
headers = {'Authorization': 'token %s' % api_token}
api_url = 'https://api.github.com/graphql'

response = requests.post(url=api_url, json=json, headers=headers)
git_content = response.json()

print(git_content)






