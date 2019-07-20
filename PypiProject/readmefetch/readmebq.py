# BACKUP

# extract readme data from bigquery:

from google.cloud import bigquery
import os

""" get org-repo and readme from bigquery """

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/antrived/Dropbox/Redhat_Work/Docs/4-Important-Credentials/Bigquery-ServiceAccount1.json'

client = bigquery.Client()

QUERY = (
    # ' SELECT repo_name, path, id FROM `bigquery-public-data.github_repos.files` WHERE path LIKE "README%" LIMIT 5 '
    # ' SELECT * FROM `bigquery-public-data.github_repos.files` WHERE path LIKE "README%" LIMIT 20 '
        """
        # SELECT files.repo_name, files.path, con.id, con.content # files.path gives file name info
        SELECT files.repo_name, files.path
        FROM `bigquery-public-data.github_repos.contents` AS con
        INNER JOIN `bigquery-public-data.github_repos.files` AS files
        ON files.id = con.id
        WHERE files.path LIKE "README%"
        LIMIT 10000
        """
)
# count:'3138803'

query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

orgrepo_readme = {}

for row in rows:
    print(row[1])
    orgrepo_readme[row[1]] = ""

print(orgrepo_readme)

# ---------------------------------------------






#
#
# # Combining 2 dicts
# from collections import defaultdict
#
#
# # load repo_org data from local and get readme for the same
# load1 = LocalLoadProcess()
# repo_org_names = load1.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo/dummy", filename="repo_org_dummy.json")
#
# repo_orgrepo = {}
#
# for key in repo_org_names.keys():
#     repo_orgrepo[key] = repo_org_names[key]+"/"+key
#
# # orgrepo_readme = {}
# # orgrepo_readme['wikele/atic'] = 'readme text 1'
# # orgrepo_readme['tema-orange/FriendsCoreDataCoding'] = 'readme text 2'
# # orgrepo_readme['xyz_org/xyz_repo'] = 'readme text 3'
# # orgrepo_readme['aaa_org/aaa_repo'] = 'readme text 4'
#
# # print("-----------------------------------------------------")
# # print(repo_orgrepo)
# # print("-----------------------------------------------------")
# # print(orgrepo_readme)
#
# d1=repo_orgrepo
# d2=orgrepo_readme
# temp = dict([(d1v, "") for (d1k, d1v) in d1.items()])
# temp.update(d2)
# d3 = dict([(d1k, [d1v, temp[d1v]]) for (d1k, d1v) in d1.items()])
#
# repo_orgrepo_readme = d3
#
# # print("-----------------------------------------------------")
# # print(repo_orgrepo_readme)
#
# load1.JsonSaver(dictfile=repo_orgrepo_readme,
#                     localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo/dummy",
#                     filename="repo_orgrepo_readme_dummy.json")
#
# load1.JsonSaver(dictfile=orgrepo_readme,
#                     localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo/dummy",
#                     filename="orgrepo_readme_dummy.json")
#
#



