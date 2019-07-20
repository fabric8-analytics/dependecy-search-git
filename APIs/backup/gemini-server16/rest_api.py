"""Definition of the routes for gemini server."""
import os
import flask
import requests
from flask import Flask, request
from flask_cors import CORS
from utils import DatabaseIngestion, scan_repo, validate_request_data, \
    retrieve_worker_result, alert_user, GREMLIN_SERVER_URL_REST, _s3_helper, \
    generate_comparison
from f8a_worker.setup_celery import init_selinon
from fabric8a_auth.auth import login_required, init_service_account_token
from data_extractor import DataExtractor
from exceptions import HTTPError
from repo_dependency_creator import RepoDependencyCreator
from notification.user_notification import UserNotification
from fabric8a_auth.errors import AuthError
import sentry_sdk
from collections import defaultdict
from collections import OrderedDict
import boto3
import json
import copy
import nltk
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import time


app = Flask(__name__)
CORS(app)

sentry_sdk.init(os.environ.get("SENTRY_DSN"))

init_selinon()

SERVICE_TOKEN = 'token'
try:
    SERVICE_TOKEN = init_service_account_token(app)
except requests.exceptions.RequestException as e:
    print('Unable to set authentication token for internal service calls. {}'
          .format(e))


""" accessing and keeping json files in memory for faster execution """
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_S3_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_S3_SECRET_ACCESS_KEY'))

""" package-keywords file """
result = s3.get_object(Bucket="antrived-nlp-search", Key="python/keywords_combined.json")
keywords_combined = json.loads(result["Body"].read().decode())
keywords_combined_temp = {}
for key in keywords_combined:
    keywords_combined_temp[key.split("/")[1]] = {}
    keywords_combined_temp[key.split("/")[1]] = copy.deepcopy(keywords_combined[key])

""" all package keywords in a list for fuzzywuzzy """
package_tags = []
for key in keywords_combined:
    package_tags.append(keywords_combined[key]['all_keywords'])

""" stopwords file """
result = s3.get_object(Bucket="antrived-nlp-search", Key="python/stopwords.json")
stopwords = json.loads(result["Body"].read().decode())
stop_words = set(stopwords['stopwords'])


@app.route('/api/v1/readiness')
def readiness():
    """Readiness probe."""
    return flask.jsonify({}), 200


@app.route('/api/v1/liveness')
def liveness():
    """Liveness probe."""
    return flask.jsonify({}), 200


@app.route('/api/v1/loadtags/<ecosystem>')
def load_keywords(ecosystem):
    """returns all packages keywords for an ecosystem"""
    result = s3.get_object(Bucket="antrived-nlp-search", Key=ecosystem + "/" + "only_keywords.json")
    only_keywords = json.loads(result["Body"].read().decode())
    return flask.jsonify(only_keywords), 200


def remove_stopwords(sentence):
    return " ".join([word.lower() for word in sentence.split()
                    if word.lower() not in stop_words and word.isalpha()])


@app.route('/api/v1/searchpython')
def fuzzy_search_python():
    """ searches and returns matching pckages based on fuzzywuzzy algorithm """
    search_result = {}
    args = request.args
    arg_list = []
    for key in args.keys():
        arg_list.append(args[key])
    user_tags = " ".join(arg_list)
    user_tags = remove_stopwords(user_tags)
    """ calculates fuzzywuzzy match score """
    ratios = process.extract(user_tags, package_tags, scorer=fuzz.token_set_ratio, limit=20)
    for txt, score in ratios:
        pck_name = txt.split()[0]
        if score >= 50 and len(txt.split()) > 5:  # to be optimized using validation strategy
            search_result[pck_name] = {}
            search_result[pck_name]['match_score'] = score
            search_result[pck_name]['pypi_link'] = "https://pypi.org/project/{val}/".format(val=pck_name)
            search_result[pck_name]['keywords'] = keywords_combined_temp[pck_name]['ref_keywords']
    search_result = json.dumps(OrderedDict(search_result))
    return search_result, 200


@app.route('/api/v1/searchpythontime')
def fuzzy_search_time():
    """ to check time taken by '/api/v1/searchpython' """
    start_time = time.time()

    search_result = {}
    args = request.args
    arg_list = []
    for key in args.keys():
        arg_list.append(args[key])
    user_tags = " ".join(arg_list)
    user_tags = remove_stopwords(user_tags)
    """ calculates fuzzywuzzy match score """
    ratios = process.extract(user_tags, package_tags, scorer=fuzz.token_set_ratio, limit=20)
    for txt, score in ratios:
        pck_name = txt.split()[0]
        if score >= 50 and len(txt.split()) > 5:  # to be optimized using validation strategy
            search_result[pck_name] = {}
            search_result[pck_name]['match_score'] = score
            search_result[pck_name]['pypi_link'] = "https://pypi.org/project/{val}/".format(val=pck_name)
            search_result[pck_name]['keywords'] = keywords_combined_temp[pck_name]['ref_keywords']
    search_result = json.dumps(OrderedDict(search_result))

    elapsed_time = time.time() - start_time
    elapsed_time = str(elapsed_time)
    return elapsed_time 


@app.route('/api/v1/register', methods=['POST'])
@login_required
def register():
    """
    Endpoint for registering a new repository.

    Registers new information and
    updates existing repo information.
    """
    resp_dict = {
        "success": True,
        "summary": ""
    }
    input_json = request.get_json()
    if request.content_type != 'application/json':
        resp_dict["success"] = False
        resp_dict["summary"] = "Set content type to application/json"
        return flask.jsonify(resp_dict), 400

    validated_data = validate_request_data(input_json)
    if not validated_data[0]:
        resp_dict["success"] = False
        resp_dict["summary"] = validated_data[1]
        return flask.jsonify(resp_dict), 404

    try:
        repo_info = DatabaseIngestion.get_info(input_json.get('git-url'))
        if repo_info.get('is_valid'):
            data = repo_info.get('data')
            # Update the record to reflect new git_sha if any.
            DatabaseIngestion.update_data(input_json)
        else:
            try:
                # First time ingestion
                DatabaseIngestion.store_record(input_json)
                status = scan_repo(input_json)
                if status is not True:
                    resp_dict["success"] = False
                    resp_dict["summary"] = "New Repo Scan Initialization Failure"
                    return flask.jsonify(resp_dict), 500

                resp_dict["summary"] = "Repository {} with commit-hash {} " \
                                       "has been successfully registered. " \
                                       "Please check back for report after some time." \
                    .format(input_json.get('git-url'),
                            input_json.get('git-sha'))

                return flask.jsonify(resp_dict), 200
            except Exception as e:
                resp_dict["success"] = False
                resp_dict["summary"] = "Database Ingestion Failure due to: {}" \
                    .format(e)
                return flask.jsonify(resp_dict), 500
    except Exception as e:
        resp_dict["success"] = False
        resp_dict["summary"] = "Cannot get information about repository {} " \
                               "due to {}" \
            .format(input_json.get('git-url'), e)
        return flask.jsonify(resp_dict), 500

    # Scan the repository irrespective of report is available or not.
    status = scan_repo(input_json)
    if status is not True:
        resp_dict["success"] = False
        resp_dict["summary"] = "New Repo Scan Initialization Failure"
        return flask.jsonify(resp_dict), 500

    resp_dict.update({
        "summary": "Repository {} was already registered, but no report for "
                   "commit-hash {} was found. Please check back later."
                   .format(input_json.get('git-url'), input_json.get('git-sha')),
        "last_scanned_at": data['last_scanned_at'],
        "last_scan_report": None
    })

    return flask.jsonify(resp_dict), 200


@app.route('/api/v1/report')
@login_required
def report():
    """Endpoint for fetching generated scan report."""
    repo = request.args.get('git-url')
    sha = request.args.get('git-sha')
    response = dict()
    result = retrieve_worker_result(sha, "ReportGenerationTask")
    if result:
        task_result = result.get('task_result')
        if task_result:
            response.update({
                "git_url": repo,
                "git_sha": sha,
                "scanned_at": task_result.get("scanned_at"),
                "dependencies": task_result.get("dependencies")
            })

            if task_result.get('lock_file_absent'):
                response.update({
                    "lock_file_absent": task_result.get("lock_file_absent"),
                    "message": task_result.get("message")
                })
                return flask.jsonify(response), 400

            return flask.jsonify(response), 200
        else:
            response.update({
                "status": "failure",
                "message": "Failed to retrieve scan report"
            })
            return flask.jsonify(response), 500
    else:
        response.update({
            "status": "failure",
            "message": "No report found for this repository"
        })
        return flask.jsonify(response), 404


@app.route('/api/v1/user-repo/scan', methods=['POST'])
@login_required
def user_repo_scan():
    """Experimental endpoint."""
    # TODO: please refactor this method is it would be possible to test it properly
    # json data and files cannot be a part of same request. Hence, we need to use form data here.
    validate_string = "{} cannot be empty"
    resp_dict = {
        "status": "success",
        "summary": ""
    }
    git_url = request.headers.get("git-url")

    if not git_url:
        validate_string = validate_string.format("git-url")
        resp_dict["status"] = 'failure'
        resp_dict["summary"] = validate_string
        return flask.jsonify(resp_dict), 400

    req_json = request.json
    set_direct = set()
    set_transitive = set()
    if req_json is None:
        validate_string = validate_string.format("input json")
        resp_dict["status"] = 'failure'
        resp_dict["summary"] = validate_string
        return flask.jsonify(resp_dict), 400

    result_ = req_json.get("result", None)
    if result_ is None:
        validate_string = validate_string.format("Result dictionary")
        resp_dict["status"] = 'failure'
        resp_dict["summary"] = validate_string
        return flask.jsonify(resp_dict), 400

    for res_ in result_:
        details_ = res_.get("details", None)
        set_direct, set_transitive = DataExtractor.get_details_from_results(details_)

    dependencies = {
        'direct': list(set_direct),
        'transitive': list(set_transitive)
    }

    try:
        repo_cves = RepoDependencyCreator.create_repo_node_and_get_cve(
            github_repo=git_url, deps_list=dependencies)

        # We get a list of reports here since the functionality is meant to be
        # re-used for '/notify' call as well.
        repo_reports = RepoDependencyCreator.generate_report(repo_cves=repo_cves,
                                                             deps_list=dependencies)
        for repo_report in repo_reports:
            notification = UserNotification.generate_notification(report=repo_report)
            UserNotification.send_notification(notification=notification,
                                               token=SERVICE_TOKEN)
    except Exception as ex:
        return flask.jsonify({
            "error": ex.__str__()
        }), 500

    resp_dict.update({
        "summary": "Report for {} is being generated in the background. You will "
                   "be notified via your preferred openshift.io notification mechanism "
                   "on its completion.".format(git_url)
    })

    return flask.jsonify(resp_dict), 200


@app.route('/api/v1/user-repo/scan/experimental', methods=['POST'])
@login_required
def user_repo_scan_experimental():  # pragma: no cover
    """
    Endpoint for scanning an OSIO user's repository.

    Runs a scan to find out security vulnerability in a user's repository
    """
    resp_dict = {
        "status": "success",
        "summary": ""
    }

    if request.content_type != 'application/json':
        resp_dict["status"] = "failure"
        resp_dict["summary"] = "Set content type to application/json"
        return flask.jsonify(resp_dict), 400

    input_json = request.get_json()

    validate_string = "{} cannot be empty"
    if 'git-url' not in input_json:
        validate_string = validate_string.format("git-url")
        resp_dict["status"] = 'failure'
        resp_dict["summary"] = validate_string
        return flask.jsonify(resp_dict), 400

    url = input_json['git-url'].replace('git@github.com:', 'https://github.com/')
    input_json['git-url'] = url

    # Call the worker flow to run a user repository scan asynchronously
    status = alert_user(input_json, SERVICE_TOKEN)
    if status is not True:
        resp_dict["status"] = "failure"
        resp_dict["summary"] = "Scan initialization failure"
        return flask.jsonify(resp_dict), 500

    resp_dict.update({
        "summary": "Report for {} is being generated in the background. You will "
                   "be notified via your preferred openshift.io notification mechanism "
                   "on its completion.".format(input_json.get('git-url')),
    })

    return flask.jsonify(resp_dict), 200


@app.route('/api/v1/user-repo/notify', methods=['POST'])
@login_required
def notify_user():
    """
    Endpoint for notifying security vulnerability in a repository.

    Runs a scan to find out security vulnerability in a user's repository
    """
    resp_dict = {
        "status": "success",
        "summary": ""
    }

    if request.content_type != 'application/json':
        resp_dict["status"] = "failure"
        resp_dict["summary"] = "Set content type to application/json"
        return flask.jsonify(resp_dict), 400

    input_json = request.get_json()

    validate_string = "{} cannot be empty"
    if 'epv_list' not in input_json:
        resp_dict["status"] = "failure"
        resp_dict["summary"] = validate_string.format('epv_list')
        return flask.jsonify(resp_dict), 400

    # Call the worker flow to run a user repository scan asynchronously
    status = alert_user(input_json, SERVICE_TOKEN, epv_list=input_json['epv_list'])
    if status is not True:
        resp_dict["status"] = "failure"
        resp_dict["summary"] = "Scan initialization failure"
        return flask.jsonify(resp_dict), 500

    resp_dict.update({
        "summary": "Report for {} is being generated in the background. You will "
                   "be notified via your preferred openshift.io notification mechanism "
                   "on its completion.".format(input_json.get('git-url')),
    })

    return flask.jsonify(resp_dict), 200


@app.route('/api/v1/user-repo/drop', methods=['POST'])
@login_required
def drop():  # pragma: no cover
    """
    Endpoint to stop monitoring OSIO users' repository.

    Runs a scan to find out security vulnerability in a user's repository
    """
    resp_dict = {
        "status": "success",
        "summary": ""
    }

    if request.content_type != 'application/json':
        resp_dict["status"] = "failure"
        resp_dict["summary"] = "Set content type to application/json"
        return flask.jsonify(resp_dict), 400

    input_json = request.get_json()

    validate_string = "{} cannot be empty"

    if 'git-url' not in input_json:
        resp_dict["status"] = "failure"
        resp_dict["summary"] = validate_string.format('git-url')
        return flask.jsonify(resp_dict), 400

    gremlin_query = "g.V().has('repo_url', '{git_url}').outE().drop().iterate()" \
                    .format(git_url=input_json.get('git-url'))
    payload = {
        "gremlin": gremlin_query
    }

    raw_response = requests.post(url=GREMLIN_SERVER_URL_REST, json=payload)

    if raw_response.status_code != 200:
        # This raises an HTTPError which will be handled by `handle_error()`.
        raw_response.raise_for_status()

    resp_dict['summary'] = 'Repository scan unsubscribed'
    return flask.jsonify(resp_dict), 200


@app.route('/api/v1/stacks-report/list/<frequency>', methods=['GET'])
def list_stacks_reports(frequency='weekly'):
    """
    Endpoint to fetch the list of generated stacks reports.

    The list is fetched based on the frequency which is either weekly or monthly.
    """
    return flask.jsonify(_s3_helper.list_objects(frequency))


@app.route('/api/v1/stacks-report/report/<path:report>', methods=['GET'])
def get_stacks_report(report):
    """
    Endpoint to retrieve a generated stacks report.

    A report matching with the filename retrieved using the /stacks-report/list/{frequency}
    will be returned.
    """
    return flask.jsonify(_s3_helper.get_object_content(report))


@app.route('/api/v1/stacks-report/compare', methods=['GET'])
def compare_stacks_report():
    """
    Endpoint to compare generated stacks reports for past days.

    Maximum number of days 7.
    """
    comparison_days = int(request.args.get('days'))
    if comparison_days < 2 and comparison_days > 7:
        # Return bad request
        return flask.jsonify(error='Invalid number of days provided to compare reports.'
                                   'Range is 2-7'), 400

    return flask.jsonify(generate_comparison(comparison_days))


@app.errorhandler(HTTPError)
def handle_error(e):  # pragma: no cover
    """Handle http error response."""
    return flask.jsonify({
        "error": e.error
    }), e.status_code


@app.errorhandler(AuthError)
def api_401_handler(err):
    """Handle AuthError exceptions."""
    return flask.jsonify(error=err.error), err.status_code


if __name__ == "__main__":  # pragma: no cover
    app.run()
