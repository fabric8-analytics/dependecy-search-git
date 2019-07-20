# Get manifest_latest.json

from collections import defaultdict
from google.cloud import bigquery
import os
from pypidesckeywords.manifestload import LocalLoadProcess
import json

""" get org-repo and readme from bigquery """

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/antrived/Dropbox/Redhat_Work/Docs/4-Important-Credentials/Bigquery-ServiceAccount1.json'

client = bigquery.Client()

query = """
    # SELECT files.repo_name, files.path, con.id, con.content # files.path gives file name info
    SELECT con.content
    FROM `bigquery-public-data.github_repos.contents` AS con
    INNER JOIN `bigquery-public-data.github_repos.files` AS files
    ON files.id = con.id
    WHERE files.path LIKE 'requirements.txt'
    # LIMIT 100
"""

query_job = client.query(query)  # API request
rows = query_job.result()

orgrepo_readme = defaultdict(list)

for row in rows:
    # print(row)
    list = []
    list.append(row[0])
    orgrepo_readme['manifests'].append(list)

print(orgrepo_readme)

savejson = LocalLoadProcess()
savejson.JsonSaver(dictfile=orgrepo_readme, localpath="/home/antrived/Dump/SearchEngineData",filename="manifest_latest_raw.json")





# ----------------------------------------------------





class LoadFromLocal:

    def __init__(self):
        pass

    def packagesupload(self, localpath, filename):
        with open(os.path.join(localpath, filename)) as pkgnames:
            return json.load(pkgnames)



from collections import defaultdict



Load1 = LoadFromLocal()
# print(Load1.packagesupload(localpath="/home/antrived/Dump/SearchEngineData", filename="manifestpckunique.json"))
package_names = Load1.packagesupload(localpath="/home/antrived/Dump/SearchEngineData", filename="manifest_latest_raw.json")
# print(package_names)


lista = package_names


# lista = {}
# lista['manifests'] = [['awfaf\naf_egs\nafeaf'], ['thd-sr\neasgER\nsdffsd'], [''], []]
listb = defaultdict(list)

# print(lista)

for listx, i in zip( lista['manifests'], range(0, len(lista['manifests'])) ):
    for val in listx:
        listy = []
        if val == "" or val is None:
            listy.append("")
        else:
            temp = val.split("\n")
            for t in temp:
                listy.append(t)
    listb['manifests'].append(listy)

print(listb)
print(len(listb['manifests']))

manifestuniquepck = []
manifestuniquepckdict = defaultdict(list)
for manifest in listb['manifests']:
    manifestuniquepck = list(set(manifestuniquepck + manifest))
manifestuniquepckdict['packagename'] = manifestuniquepck
print(manifestuniquepckdict['packagename'])
print(len(manifestuniquepckdict['packagename']))






from pypidesckeywords.manifestload import LocalLoadProcess

savejson = LocalLoadProcess()
savejson.JsonSaver(dictfile=manifestuniquepckdict,
                    localpath="/home/antrived/Dump/SearchEngineData",
                    filename="manifest_latest_raw_unique.json")



""" extract unique packages 
cleaning:
remove text starting with # or after #
pick text before == and <= and then =
maybe convert all " to something else like ;
keep if only 'text - _' (can be combined with step 1)
convert to lowercase;
remove by length (take longest name from manifest.json) -- longest_pck: django-tastypie-with-file-upload-and-model-form-validation - length: 58
remove spaces
after initial steps; if anything apart from 'text - _' then remove
"""



""" check all of them against pypi.org """
