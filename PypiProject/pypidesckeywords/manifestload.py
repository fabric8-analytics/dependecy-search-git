""" Pypi.org data extraction - Desc and Keywords - Part 1 """
# Load manifest.json from local; bring in simpler format like {"packagename": ["torch", "keras",]} and save in local
# Note: manifest.json has complex structure and multiple manifests/requirements.txt

# -------------------------------------------------------
import json
import os
from collections import defaultdict


class LocalLoadProcess:

    def __init__(self):
        self.stats = defaultdict(str)

    def JsonUploader(self, localpath, filename):
        with open(os.path.join(localpath, filename)) as pkgnames:
            return json.load(pkgnames)

    def ManifestProcessing(self, manifestscollated):

        """ creates dict with unique package names """

        manifestuniquepck = []
        manifestuniquepckdict = defaultdict(list)
        # count = 0
        for manifest in manifestscollated['package_dict']['bigquery_data']:
            manifestuniquepck = list(set(manifestuniquepck + manifest))
            # this commented code is to test for few manifests
            # count += 1
            # if count == 4:
            #     break
        manifestuniquepckdict['packagename'] = manifestuniquepck
        self.stats['unique-package-count'] = len(manifestuniquepckdict['packagename'])
        return manifestuniquepckdict

    def JsonSaver(self, dictfile, localpath, filename):
        with open(os.path.join(localpath, filename), 'w') as outfile:
            json.dump(dictfile, outfile)


# if __name__ == "__main__":
#     Load1 = LoadFromLocal()
#     print(Load1.packagesupload(localpath="/home/antrived/Dump", filename="manifest.json"))

def main():
    # Process 'manifest.json' to get unique packages in 'manifestpckunique.json'
    Load1 = LocalLoadProcess()
    Temp = Load1.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData", filename="manifest.json")
    Temp1 = Load1.ManifestProcessing(Temp)
    Load1.JsonSaver(dictfile=Temp1, localpath="/home/antrived/Dump/SearchEngineData", filename="manifestpckunique.json")
    Load1.JsonSaver(dictfile=Load1.stats, localpath="/home/antrived/Dump/SearchEngineData", filename="stats.json")
    print("NUMBER OF UNIQUE PACKAGES:", len(Temp1['packagename']))

if __name__ == "__main__":
    main()




# print(len(Temp['package_dict']['bigquery_data']))
# # Stats: 69134 manifests are there

# -------------------------------------------------------
