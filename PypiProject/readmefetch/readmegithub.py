# Readme from raw github api - Classify
import time
from collections import defaultdict
import requests
from pypidesckeywords.manifestload import LocalLoadProcess


class GithubReadme:

    """  get readme from raw github url
         assumption: all package names in manifest.json have '-' and not '_', '.' etc. """

    def __init__(self):
        self.repo_orgrepo_readme = defaultdict(list)
        self.stats = defaultdict(int)
        self.elapsed_time = 0

    def append_readme(self, req, repo):

        if "_" in repo:
            repo = repo.replace("_", "-")
        self.repo_orgrepo_readme[repo].append(req.text)
        print("response_code:{val}".format(val=req.status_code))

    def call_readme_extensions(self, repo, org):

        if org == "":
            self.repo_orgrepo_readme[repo].append("")
            print("ORG NOT PRESENT")
        else:
            url = "https://raw.githubusercontent.com/{val1}/{val2}/master/README.md".format(val1=org, val2=repo)
            req = requests.get(url)
            if req.status_code == 200:
                self.append_readme(req, repo)
            else:
                url = "https://raw.githubusercontent.com/{val1}/{val2}/master/README.rst".format(val1=org, val2=repo)
                req = requests.get(url)
                if req.status_code == 200:
                    self.append_readme(req, repo)
                else:
                    url = "https://raw.githubusercontent.com/{val1}/{val2}/master/README.txt".format(val1=org,
                                                                                                     val2=repo)
                    req = requests.get(url)
                    if req.status_code == 200:
                        if req.status_code == 200:
                            self.append_readme(req, repo)
                    else:
                        url = "https://raw.githubusercontent.com/{val1}/{val2}/master/README".format(val1=org,
                                                                                                     val2=repo)
                        req = requests.get(url)
                        if req.status_code == 200:
                            self.append_readme(req, repo)
                        else:
                            url = "https://raw.githubusercontent.com/{val1}/{val2}/master/README.markdown".format(
                                val1=org,
                                val2=repo)
                            req = requests.get(url)
                            if req.status_code == 200:
                                self.append_readme(req, repo)
                            else:
                                url = "https://raw.githubusercontent.com/{val1}/{val2}/master/README.org".format(
                                    val1=org,
                                    val2=repo)
                                req = requests.get(url)
                                if req.status_code == 200:
                                    self.append_readme(req, repo)
                                else:
                                    if "-" in repo:
                                        repo = repo.replace("-", "_")
                                        self.call_readme_extensions(repo, org)
                                        return
                                    if "_" in repo:
                                        repo = repo.replace("_", "-")
                                    self.repo_orgrepo_readme[repo].append("")
                                    print("response_code:{val} -- {val1} -- repo: {val2} -- org: {val3}".
                                          format(val=req.status_code,
                                                 val1="README NA or README NA WITH POPULAR EXTENSION", val2=repo,
                                                 val3=org))

    def get_readme(self, package_names):

        start_time = time.time()
        count = 0

        for repo, org in package_names.items():
            """ adding org-repo against every package name """

            count += 1
            # if count == 200:
            #     break

            self.repo_orgrepo_readme[repo].append(org + "/" + repo)
            self.call_readme_extensions(repo, org)
            print("completion % {val}".format(val=100*count/len(package_names.keys())))

        self.elapsed_time = time.time() - start_time

    def calculate_stats(self):

        total_count = 0
        org_repo_count = 0
        readme_count = 0

        for repo in self.repo_orgrepo_readme.keys():
            total_count += 1
            org_repo = self.repo_orgrepo_readme[repo][0].split('/')
            if org_repo[0] != "":
                org_repo_count += 1
            if self.repo_orgrepo_readme[repo][1] != "":
                readme_count += 1

        self.stats['Total-Repo-Count'] = total_count
        self.stats['Org-Repo-Count'] = org_repo_count
        self.stats['Readme-Count'] = readme_count
        self.stats['Total-Time'] = self.elapsed_time


def main():

    Load1 = LocalLoadProcess()
    package_names = Load1.JsonUploader(localpath="/home/antrived/Dump/SearchEngineData/PypiData/PypiDataOrgRepo",
                                       filename="repo_org_pairs.json")

    readme_extract = GithubReadme()
    readme_extract.get_readme(package_names)
    Load1.JsonSaver(dictfile=readme_extract.repo_orgrepo_readme,
                    localpath="/home/antrived/Dump/SearchEngineData/GithubReadmeData/rawgithub",
                    filename="repo_orgrepo_readme.json")

    readme_extract.calculate_stats()
    Load1.JsonSaver(dictfile=readme_extract.stats,
                    localpath="/home/antrived/Dump/SearchEngineData/GithubReadmeData/rawgithub",
                    filename="stats.json")


if __name__ == "__main__":
    main()




""" 
Imp Summary:
Different README extensions, priority wise (from BQ query) :
Most occuring(~99%) - .md, .rst, .txt, <nothing>, markdown, org
Others = osx, chromium, rdoc, fr.md, rdoc, yasmet, pod, textile
All = {'README.rst': '', 'README.md': '', 'README.fr.md': '', 'README': '', 'README.rdoc': '', 'README.txt': '', 'README.adoc': '', 'README.markdown': '', 'README.zh_cn.md': '', 'README.mdown': '', 'README.textile': '', 'README2.md': '', 'README_DE.md': '', 'README.osx': '', 'README_codestyle.md': '', 'README.org': '', 'README.TXT': '', 'README.pixmaps': '', 'README_FILES/RESTRICTION_CLASS_README': '', 'README_LOGIN': '', 'README.md~': '', 'README.plotting': '', 'README.html': '', 'README/Json/json_editor_online.png': '', 'README.EMB-712': '', 'README.MD': '', 'README_files/figure-html/unnamed-chunk-22.png': '', 'README_MEAN.md': '', 'README.CodingStyle.md': '', 'README_SCREENSHOTS/templates/leave_form.html': '', 'README_files/figure-markdown_github/unnamed-chunk-2-1.png': '', 'README.IRIX': '', 'README.rst~': '', 'README.translations': '', 'README.old.md': '', 'README.mkdn': '', 'README.pod': '', 'README.FAQ': '', 'README.RangeSensor_GP2Y0A21YK': '', 'README_cache/markdown_github-ascii_identifiers/unnamed-chunk-3_b4b386ef71a05ab55c3eb01182e6e420.rdx': '', 'README_cache/markdown_github/unnamed-chunk-3_27f907fdad6382b1740759ef7407013c.rdx': '', 'README_cache/markdown_github-ascii_identifiers/unnamed-chunk-1_c916d86f71e8b4032c8066181c5bbba5.rdx': '', 'README_cache/markdown_github-ascii_identifiers/global_07ad68b3b28082d888348b2286100e9c.rdx': '', 'README_cache/markdown_github-ascii_identifiers/unnamed-chunk-2_13a04015cac38d228e4010f1f084f816.rdx': '', 'README_cache/markdown_github/unnamed-chunk-1_1a51de3c76161ddf05933d3980844c8d.rdx': '', 'README-REPO': '', 'README.UW/README.CALL_STATS': '', 'README.Amiga': '', 'README.Windows.txt': '', 'README_CN.txt': '', 'README/output_31_0.png': '', 'README.wg': '', 'README_files/bootstrap-3.3.1/js/bootstrap.min.js': '', 'README.install.pod': '', 'README_PLUGINS': '', 'README_EN.md': '', 'README.png': '', 'README.version': '', 'README_files/figure-markdown_strict/unnamed-chunk-28-10.png': '', 'README.pdf': '', 'README_unparse.md': '', 'README-ko.md': '', 'README.es.md': '', 'README_cache/markdown_github-ascii_identifiers/unnamed-chunk-3_e6b209837cfb6bd2dba0ae2922d0270c.rdx': '', 'README.vagrant.md': '', 'README-EN.md': '', 'README.dev': '', 'README-developers.md': '', 'README.Rmd': '', 'README.GlotPress': '', 'README_API.md': '', 'README.w32': '', 'README.PATCHES': '', 'README.txt~': '', 'README 2.md': '', 'README.old': '', 'README.debian': '', 'README-facilitator.md': '', 'README_zh.md': '', 'README.chromium': '', 'README.fixme': '', 'README.it.md': '', 'README.PACKAGERS': '', 'README.CREDITS': '', 'README.mediawiki': '', 'README.unprivileged': '', 'README_BUILD_FIRESTORM_WIN32.txt': '', 'README_files/number_of_2D_points_(Desktop).png': '', 'README-CN.md': '', 'README.win32': '', 'README-aspnet.md': '', 'README-mn.md': '', 'README-zh-cn.md': '', 'README (2).md': '', 'README_files/figure-markdown_strict/unnamed-chunk-23-36.png': '', 'README-py3.md': '', 'README_file_formats_and_descriptions.md': '', 'README/Channels.md': '', 'README.Japanese.md': '', 'README/CREDITS': '', 'README.yasmet': ''}

Insights:
Others and All impact less than 2% of repos
Many-many repo names have changed, they are slightly different or there is re-route (repo-org is from Mar starting, currently its May end) - so we need latest package names
Many dependencies with names like 'pyramid_jwt' are saved as 'pyramid-jwt'(and pyramid_chameleon, flask_fontpicker)...need to to correct this...but 'python-bioformats' is 'python-bioformats'
"""

""" 
check for rodluger/k2plr,  
"""
