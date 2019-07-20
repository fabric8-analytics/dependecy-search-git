""" extract description and keywords from pypi.org """

from pypidesckeywords.manifestload import LocalLoadProcess
from pypidesckeywords.extractdata import PypiOrgDataExtraction
import json


def mainx():
    # Process 'manifest.json' to get unique packages in 'manifestpckunique.json'
    Load1 = LocalLoadProcess()
    Temp = Load1.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData", filename="manifest.json")
    Temp1 = Load1.ManifestProcessing(Temp)
    Load1.JsonSaver(dictfile=Temp1, localpath="/home/antrived/Dump/SearchEngineData", filename="manifestpckunique.json")
    Load1.JsonSaver(dictfile=Load1.stats, localpath="/home/antrived/Dump/SearchEngineData", filename="stats.json")
    print("NUMBER OF UNIQUE PACKAGES:", len(Temp1['packagename']))

    # load file 'manifestpckunique.json'
    Load1 = LocalLoadProcess()
    pkgnames = Load1.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData", filename="manifestpckunique.json")

    # extract pypi.org description data
    P1 = PypiOrgDataExtraction()
    P1.PackageDescKeywordsExraction(pkgnames=pkgnames)
    print("--------------------------------------------------------------------------------------------")
    print("PACKAGE DESCRIPTION:")
    print(json.dumps(P1.packagedescription))
    print("--------------------------------------------------------------------------------------------")
    print("PACKAGE KEYWORDS:")
    print(json.dumps(P1.keywords))
    print("--------------------------------------------------------------------------------------------")
    print(" Secs:", P1.elapsedtime, "\n", "Mins:", P1.elapsedtime/60, "\n", "Hours:", P1.elapsedtime/60/60)
    print("--------------------------------------------------------------------------------------------")
    print("NUMBER OF PACKAGES: {val}".format(val=P1.totalcount))
    print("NUMBER OF PACKAGES WITH DESCRIPTION: {val}".format(val=P1.descriptionpckcount))
    print("NUMBER OF PACKAGES WITH KEYWORDS: {val}".format(val=P1.keywordspckcount))

    # save files "manifestpckdescription.json" and "manifestpckkeywords.json"
    LoadX = LocalLoadProcess()
    LoadX.JsonSaver(dictfile=P1.packagedescription, localpath="/home/antrived/Dump/SearchEngineData/PypiData", filename="manifestpckdescription.json")
    LoadX.JsonSaver(dictfile=P1.keywords, localpath="/home/antrived/Dump/SearchEngineData/PypiData", filename="manifestpckkeywords.json")
    LoadX.JsonSaver(dictfile=P1.stats, localpath="/home/antrived/Dump/SearchEngineData/PypiData", filename="stats.json")


def mainy():
    # load all unique packages
    load_json = LocalLoadProcess()
    package_names = load_json.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData", filename="manifestpckunique.json")

    # extracting org for packages
    org_extractor = PypiOrgDataExtraction()
    org_extractor.orgextract(package_names)

    # save repo-org-pairs in local
    load_json.JsonSaver(dictfile=org_extractor.repo_org_pairs, localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo",filename="repo_org_pairs.json")
    load_json.JsonSaver(dictfile=org_extractor.stats, localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo", filename="stats.json")


if __name__ == "__main__":
    # mainx()
    mainy()
