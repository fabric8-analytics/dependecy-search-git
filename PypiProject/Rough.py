""" Backup- Get data from github graphql """

import time
from collections import defaultdict
import requests
from pypidesckeywords.manifestload import LocalLoadProcess


api_token = "f753f9550d2ff8616a7cd9c8688236c517d23140"


class GraphqlPypiData:

    def __init__(self):

        self.description = defaultdict(str)
        self.keywords = defaultdict(list)
        self.stats = defaultdict(int)
        self.elapsed_time = 0

    def extract_data(self, package_names):

        start_time = time.time()
        count = 0

        for repo, org in package_names.items():

            count += 1
            if count == 500:
                break

            json = {
                    'query': '{{organization(login: "{0}"){{name url repository(name: "{1}")\
                    {{name url description repositoryTopics(first: 100){{nodes{{topic {{name}}}}}}}}}}}}'
                    .format(str(org), str(repo))}
            headers = {'Authorization': 'token %s' % api_token}
            api_url = 'https://api.github.com/graphql'

            response = requests.post(url=api_url, json=json, headers=headers)
            git_content = response.json()

            try:
                if git_content['data']['organization']['repository']['description']:
                    print("---------------- description key exists for: {val}/{val1}".format(val=org, val1=repo))
                    self.description[repo] = git_content['data']['organization']['repository']['description']
            except Exception as _exc:
                print("NO DESCRIPTION KEY FOR {val}/{val1} - error:{val2}".format(val=org, val1=repo, val2=_exc))
                self.description[repo] = ""
            finally:
                if self.description[repo]:
                    pass
                else:
                    self.description[repo] = ""

            try:
                if git_content['data']['organization']['repository']['repositoryTopics']:
                    print("---------------- keywords key exists for: {val}/{val1}".format(val=org, val1=repo))
                    try:
                        for node in git_content['data']['organization']['repository']['repositoryTopics']['nodes']:
                            self.keywords[repo].append(node['topic']['name'])
                    except Exception as _exc:
                        print("NO KEYWORD FOUND")
                        self.keywords[repo].append("")
            except Exception as _exc:
                print("NO KEYWORD KEY FOR {val}/{val1} - error:{val2}".format(val=org, val1=repo, val2=_exc))
                self.keywords[repo].append("")
            finally:
                if self.keywords[repo]:
                    pass
                else:
                    self.keywords[repo].append("")

            print("% completion:{val}".format(val=100*count/len(package_names.keys())))

        self.elapsed_time = time.time() - start_time

    def calculate_stats(self):

        total_count_desc_json = 0
        total_count_keywords_json = 0
        desc_count = 0
        keyword_count = 0

        for repo in self.description.keys():
            total_count_desc_json += 1
            if self.description[repo] != "":
                desc_count += 1
        for repo in self.keywords.keys():
            total_count_keywords_json += 1
            if len(self.keywords[repo][0]) != 0:
                keyword_count += 1

        self.stats['Total-Repos-In-Description-Json'] = total_count_desc_json
        self.stats['Total-Repos-In-Keywords-Json'] = total_count_keywords_json
        self.stats['Repos-with-Description'] = desc_count
        self.stats['Repos-with-Keywords'] = keyword_count
        self.stats['Total-Time'] = self.elapsed_time


def main():

    Load1 = LocalLoadProcess()
    package_names = Load1.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo",
                                       filename="repo_org_pairs.json")

    graphqlextract = GraphqlPypiData()
    graphqlextract.extract_data(package_names)
    graphqlextract.calculate_stats()


    Load1.JsonSaver(dictfile=graphqlextract.description,
                    localpath="/home/antrived/Dump/SearchEngineData/GitGraphData",
                    filename="graphql_git_description.json")
    Load1.JsonSaver(dictfile=graphqlextract.keywords,
                    localpath="/home/antrived/Dump/SearchEngineData/GitGraphData",
                    filename="graphql_git_keywords.json")
    Load1.JsonSaver(dictfile=graphqlextract.stats,
                    localpath="/home/antrived/Dump/SearchEngineData/GitGraphData",
                    filename="stats.json")


if __name__ == "__main__":
    main()






"""
things to consider /  cases to handle:
- output format: 2 files for desc and keywords. format = ['repo':'desc', 'repo1':'desc1'] and ['repo':'keyw,keyw1', 'repo1':'']

- org not present - has "errors" as a key OR check explicitly and don't do api call
- repo name invalid(org present) - has "errors" as a key - check for "_" also
    - (str('rocky'), str('uncompyle2')) has "errors" as a key

- (may not be required) desc not present - like for ___ - output: "description":"" - can do by checking len()
- keyword not present like for 'pyatom/pyatom' - output: "nodes":[] - can do by checking len()

- try "_" where "-" is present in package name and 200 not returned

- special output:
  - str('kennethreitz'), str('requests-foauth') AND (str('VUnit'), str('vunit-hdl') - desc and nodes keys not present - chk by try/except
    - combine this with "'errors' as a key" output


Correct Sample Output:
{
"data":{
     "organization":{
          "name":"tensorflow",
          "url":"https://github.com/tensorflow",
          "repository":{
               "name":"tensorflow",
               "url":"https://github.com/tensorflow/tensorflow",
               "description":"An Open Source Machine Learning Framework for Everyone",
               "repositoryTopics":{
                   "nodes":[
                        {
                        "topic":{
                        "name":"tensorflow"
                        }
                        },
                        {
                        "topic":{
                        "name":"machine-learning"
                        }


Sample error output:
{
"data":{
    "organization":null
},
"errors":[
{
        "type":"NOT_FOUND",
        "path":[
            "organization"
        ],  
        "locations":[
                {
                "line":1,
                "column":2
                }
        ],
        "message":"Could not resolve to an Organization with the login of 'rocky'."
}
]
}


Another incorrect output:
{
"data":{
    "organization":{
        "name":"VUnit",
        "url":"https://github.com/VUnit",
        "repository":null
}
}
}


"""