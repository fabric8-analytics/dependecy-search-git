# extract readme data from bigquery:

import time
from collections import defaultdict
from google.cloud import bigquery
import os
from pypidesckeywords.manifestload import LocalLoadProcess



class ExtractReadme:
    """ get readme from bigquery for pypi packages """
    def __init__(self):
        self.repo_orgrepo = {}
        self.all_orgrepo_readme = {}
        self.repo_orgrepo_readme = {}
        self.elapsedtime_f1 = 0
        self.elapsedtime_f2 = 0
        self.stats = defaultdict(int)

    def get_all_readme(self):

        """ get all org-repo and readme from bigquery """

        starttime = time.time()
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/antrived/Dropbox/Redhat_Work/Docs/4-Important-Credentials/Bigquery-ServiceAccount1.json'
        client = bigquery.Client()
        query = (
                """
                # SELECT files.repo_name, files.path, con.id, con.content # files.path gives file name info
                SELECT files.repo_name, con.content
                FROM `bigquery-public-data.github_repos.contents` AS con
                INNER JOIN `bigquery-public-data.github_repos.files` AS files
                ON files.id = con.id
                WHERE files.path LIKE "README%"
                # LIMIT 10
                """
        )
        # count:'3138803'
        query_job = client.query(query)  # API request
        rows = query_job.result()  # Waits for query to finish

        for row in rows:
            self.all_orgrepo_readme[row[0]] = row[1]

        self.elapsedtime_f1 = time.time() - starttime

    def readme_for_pypi(self, repo_org_names):

        """ get readme for pypi org-repo """

        starttime = time.time()

        for key in repo_org_names.keys():
            self.repo_orgrepo[key] = repo_org_names[key]+"/"+key

        print("-----------------------------------------------------")
        # print(self.repo_orgrepo)
        print("-----------------------------------------------------")
        # print(self.all_orgrepo_readme)

        # merge repo_orgrepo with all_orgrepo_readme
        d1 = self.repo_orgrepo
        d2 = self.all_orgrepo_readme
        temp = dict([(d1v, "") for (d1k, d1v) in d1.items()])
        temp.update(d2)
        d3 = dict([(d1k, [d1v, temp[d1v]]) for (d1k, d1v) in d1.items()])

        self.repo_orgrepo_readme = d3

        print("-----------------------------------------------------")
        # print(self.repo_orgrepo_readme)

        self.elapsedtime_f2 = time.time() - starttime

    def generate_stats(self):

        """ count packages with readme
            saves runtime of above 2 functions """

        total_count = 0
        readme_count = 0
        for key in self.repo_orgrepo_readme.keys():
            total_count += 1
            if self.repo_orgrepo_readme[key][1] != "":
                readme_count += 1

        self.stats['total-package-count'] = total_count
        self.stats['packages-with-readme-count'] = readme_count
        self.stats['get_all_readme-fn-hours'] = self.elapsedtime_f1/60/60
        self.stats['readme_for_pypi-fn-hours'] = self.elapsedtime_f2/60/60


def main():
    load1 = LocalLoadProcess()
    repo_org_names = load1.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo", filename="repo_org_pairs.json")

    getreadme = ExtractReadme()
    getreadme.get_all_readme()
    getreadme.readme_for_pypi(repo_org_names)
    getreadme.generate_stats()

    load1.JsonSaver(dictfile=getreadme.repo_orgrepo_readme,
                                localpath="/home/antrived/Dump/SearchEngineData/GithubReadmeData/bigquery",
                                filename="repo_orgrepo_readme.json")
    load1.JsonSaver(dictfile=getreadme.stats,
                                localpath="/home/antrived/Dump/SearchEngineData/GithubReadmeData/bigquery",
                                filename="stats.json")


if __name__ == "__main__":
    main()

