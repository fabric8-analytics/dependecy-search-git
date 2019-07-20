""" Pypi.org data extraction - Desc and Keywords - Part 2 """
# Extract packages description from Pypi.org and Save 'packagenames + description' json to local

from pypidesckeywords.manifestload import LocalLoadProcess
import json
from collections import defaultdict
import requests
import time
import re


class PypiOrgDataExtraction:
    """  Pypi description and keywords extraction """
    def __init__(self):
        # these variables are mainly for 'PackageDescKeywordsExraction'
        self.packagedescription = defaultdict(str)
        self.descriptionpckcount = 0
        self.keywords = defaultdict(str)
        self.keywordspckcount = 0
        self.totalcount = 0
        self.starttime = 0
        self.elapsedtime = 0
        self.stats = defaultdict(str)
        # these variables are mainly for 'orgextract'
        self.repo_org_pairs = defaultdict(str)
        self.stats = defaultdict(int)

    def PackageDescKeywordsExraction(self, pkgnames):

        """ extracts description and keywords from pypi.org """

        self.starttime = time.time()

        for pck in pkgnames['packagename']:
            try:
                URL = "https://pypi.org/pypi/{packagename}/json".format(packagename=pck)
                r = requests.get(url=URL)
                data = r.json()
                # if error, execution will jump from here to 'Exception'
                print("Match found for '{val}'".format(val=pck))
                self.packagedescription[pck] = data['info']['description']
                self.keywords[pck] = data['info']['keywords']
                # some values are "UNKNOWN", replace with "" (commented out as increases time)
                if self.packagedescription[pck] == "UNKNOWN":
                    self.packagedescription[pck] = ""
                # some values are null, replace with ""
                if self.keywords[pck] is None:
                    self.keywords[pck] = ""
                # some keywords were separated by ' ' and some by ','
                if "," not in self.keywords[pck]:
                    self.keywords[pck] = self.keywords[pck].replace(" ", ",")
            except Exception as _exc:
                print("No match found for '{val}' -- Exception: '{val1}'".format(val=pck, val1=str(_exc)))
                # even if package not present in pypi.org, keep its value in 'self.packagedescription'
                self.packagedescription[pck] = ""
                self.keywords[pck] = ""
            if self.packagedescription[pck] != "":
                self.descriptionpckcount = self.descriptionpckcount + 1
            if self.keywords[pck] != "":
                self.keywordspckcount = self.keywordspckcount + 1
            self.totalcount = self.totalcount + 1
            self.elapsedtime = time.time() - self.starttime

            # populating stats
            self.stats['number-of-packages'] = self.totalcount
            self.stats['number-of-packages-with-desc'] = self.descriptionpckcount
            self.stats['number-of-packages-with-keywords'] = self.keywordspckcount
            elapsedtimehours = self.elapsedtime/60/60  # added later
            self.stats['Runtime-hours'] = elapsedtimehours  # added later

    # def PackageSaver(self):
    #     with open(os.path.join('/home/antrived/Dump', 'manifestpckdescription.json'), 'w') as outfile:
    #         json.dump(self.packagedescription, outfile)

    def orgextract(self, package_names):

        """ get github url from pypi.org
            get org and repo names from github url """

        start_time = time.time()
        print("start date-time={val}".format(val=time.strftime("%D %H:%M", time.localtime(int(start_time)))))
        total_repo_count = 0
        org_present_count = 0
        # count = 0

        for pckg_name in package_names['packagename']:

            # if count == 50:
            #     break
            # count += 1

            try:

                URL = "https://pypi.org/pypi/{packagename}/json".format(packagename=pckg_name)
                r = requests.get(url=URL)
                data = r.json()

                url_value = ""
                print("pypi match found for: {val}".format(val=pckg_name))

                # find 1st instance of github url and get org and repo names
                for key_name in data['info'].keys():
                    # "project_urls" has to be looped separately as its a dict
                    if key_name != "project_urls":
                        # avoiding null, {}, [] and 'description' in dict values
                        if data['info'][key_name] is not None and \
                                type(data['info'][key_name]) != list and type(data['info'][key_name]) != dict\
                                and key_name != "description":
                            if "https://github.com" in data['info'][key_name] \
                                    or "http://github.com" in data['info'][key_name] \
                                    or "https://www.github.com" in data['info'][key_name] \
                                    or "http://www.github.com" in data['info'][key_name]:
                                url_value = data['info'][key_name]
                                break
                    else:
                        if data['info'][key_name] is not None:
                            for key_n in data['info'][key_name].keys():
                                if "https://github.com" in data['info'][key_name][key_n] \
                                        or "http://github.com" in data['info'][key_name][key_n] \
                                        or "https://www.github.com" in data['info'][key_name][key_n] \
                                        or "http://www.github.com" in data['info'][key_name][key_n]:
                                    url_value = data['info'][key_name][key_n]
                                break
                        break

                """ get org and repo names from url """

                if "https://github.com" in url_value or "http://github.com" in url_value \
                        or "https://www.github.com" in url_value or "http://www.github.com" in url_value:
                    if url_value.count("/") > 4:
                        t1 = re.search('github.com/(.*)/', url_value)
                    else:
                        t1 = re.search('github.com/(.*)', url_value)
                    t1 = str(t1.group(1))
                    t1 = t1.split('/')
                    self.repo_org_pairs[pckg_name] = t1[0]
                    # print("repo-org-pairs: {val}".format(val=json.dumps(repo_org_pairs)))
                else:
                    print("GITHUB.COM URL NOT FOUND IN PYPI INFORMATION")
                    self.repo_org_pairs[pckg_name] = ""
                    # print("repo-org-pairs: {val}".format(val=json.dumps(repo_org_pairs)))

            except Exception as _exc:
                print("NO PYPI MATCH FOUND FOR: {val} -- Exception: '{val1}'".format(val=pckg_name, val1=str(_exc)))
                self.repo_org_pairs[pckg_name] = ""
                # print("repo-org-pairs: {val}".format(val=json.dumps(repo_org_pairs)))

            # counting 'repos searched' and 'repos where org found'
            total_repo_count += 1
            if self.repo_org_pairs[pckg_name] != "":
                org_present_count += 1
            # print("start date-time={val}; % completion={val1}".format(val=time.strftime("%D %H:%M", time.localtime(int(start_time))), val1=100*total_repo_count/19113))
            print("% completion={val1}".format(val1=100 * total_repo_count / 19113))

        elapsed_time = time.time() - start_time
        print("----------------------STATS-------------------------")
        print("Time-hours: {val}".format(val=elapsed_time/60/60))
        print("Total-Repos-Searched: {val}".format(val=total_repo_count))
        print("Organization-Present-For: {val}".format(val=org_present_count))
        print("----------------------------------------------------")

        self.stats['Time-hours'] = elapsed_time/60/60
        self.stats['Total-Repos-Searched'] = total_repo_count
        self.stats['Organization-Present-For'] = org_present_count


def main():
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


if __name__ == "__main__":
    main()







## add logger;