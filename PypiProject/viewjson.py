# View Files

import json
import os


class LoadFromLocal:

    def __init__(self):
        pass

    def packagesupload(self, localpath, filename):
        with open(os.path.join(localpath, filename)) as pkgnames:
            return json.load(pkgnames)


if __name__ == "__main__":
    Load1 = LoadFromLocal()
    # package_names = Load1.packagesupload(localpath="/home/antrived/Dump/SearchEngineData/GitGraphData", filename="graphql_git_keywords_recur.json")
    # package_names = Load1.packagesupload(localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo",
    #                                    filename="repo_org_pairs.json")
    package_names = Load1.packagesupload(localpath="/home/antrived/Dump/SearchEngineData/GithubReadmeData/rawgithub",
                                       filename="repo_orgrepo_readme.json")
    print(package_names)



package_names_mini = {}
count = 0

for pck in package_names.keys():
    package_names_mini[pck] = package_names[pck]
    count += 1
    if count == 3:
        break


# print(package_names_mini)
print(count)



from pypidesckeywords.manifestload import LocalLoadProcess
Load1 = LocalLoadProcess()
Load1.JsonSaver(dictfile=package_names_mini, localpath="/home/antrived/Dump/SearchEngineData/dummy", filename="sample3.json")


# -------------------------------------------------------
