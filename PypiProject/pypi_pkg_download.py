""" Pypi package download info - working code in Jupyter """


# import libraries
from google.cloud import bigquery
# pip install --upgrade google-cloud-bigquery
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/antrived/Dropbox/Redhat_Work/Docs/4-Important-Credentials/Bigquery-ServiceAccount1.json'



def pypi_download_count(downloads, pkg_name):
    pkg_name1 = "'" + pkg_name + "'"
    Query_text = " SELECT COUNT(*) AS num_downloads FROM `the-psf.pypi.downloads*` WHERE file.project = " + pkg_name1 + " AND _TABLE_SUFFIX BETWEEN FORMAT_DATE( '%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)) AND FORMAT_DATE('%Y%m%d', CURRENT_DATE()) "
    client = bigquery.Client()
    QUERY = (Query_text)
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    for row in rows:
        print("{val}, downloads={val1}".format(val=pkg_name, val1=row[0]))
        downloads[pkg_name] = row[0]
        
    return downloads

download_count = {}
# download_count = copy.deepcopy( pypi_download_count(download_count, 'pytorch') )
# download_count = copy.deepcopy( pypi_download_count(download_count, 'keras') )
# download_count = copy.deepcopy( pypi_download_count(download_count, 'tensorflow') )
download_count = copy.deepcopy( pypi_download_count(download_count, 'whoosh') )
download_count
