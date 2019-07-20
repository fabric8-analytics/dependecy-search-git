from collections import defaultdict

import flask
from flask import request


def abc():
    dict_tags = defaultdict(list)
    dict_tags['name'].append("editdistance-fast-implementation")
    dict_tags['name'].append("time-series")
    dict_tags['name'].append("jupyterhub")
    return dict_tags, 200


def xyz(tag1=None, tag2=None, tag3=None):

    dict_pcks = defaultdict(list)

    # tag1 = request.args.get('tag1')
    # tag2 = request.args.get('tag2')
    # tag3 = request.args.get('tag3')

    tag1 = ("" if tag1 is None else tag1)
    tag2 = ("" if tag2 is None else tag2)
    tag3 = ("" if tag3 is None else tag3)

    tags = (" ".join((tag1 + " " + tag2 + " " + tag3).split())).strip()

    if tags == "editdistance-fast-implementation":
        dict_pcks['packages'].append("package1")
        dict_pcks['packages'].append("package2")
    if tags == "time-series":
        dict_pcks['packages'].append("package1")
        dict_pcks['packages'].append("package3-x")
    if tags == "jupyterhub":
        dict_pcks['packages'].append("package4")
        dict_pcks['packages'].append("package5-x")

    if tags == "editdistance-fast-implementation time-series" or tags == "time-series editdistance-fast-implementation":
        dict_pcks['packages'].append("package5")
        dict_pcks['packages'].append("package7")
        dict_pcks['packages'].append("package8")
    if tags == "editdistance-fast-implementation jupyterhub" or tags == "jupyterhub editdistance-fast-implementation":
        dict_pcks['packages'].append("package11")
        dict_pcks['packages'].append("package9")
    if tags == "time-series jupyterhub" or tags == "jupyterhub time-series":
        dict_pcks['packages'] = "package1 package5-x"
        dict_pcks['packages'].append("package1")
        dict_pcks['packages'].append("package5-x")

    if tags == "editdistance-fast-implementation time-series jupyterhub" or \
            tags == "editdistance-fast-implementation jupyterhub time-series" or \
            tags == "time-series editdistance-fast-implementation jupyterhub" or \
            tags == "time-series jupyterhub editdistance-fast-implementation" or \
            tags == "jupyterhub editdistance-fast-implementation time-series" or \
            tags == "jupyterhub time-series editdistance-fast-implementation":
        dict_pcks['packages'].append("package1")
        dict_pcks['packages'].append("package3-x")
        dict_pcks['packages'].append("package5")
        dict_pcks['packages'].append("package7-x")

    return dict_pcks, 200


X = abc()
print(X[0])

tag1 = "jupyterhub"
tag2 = "time-series"
tag3 = "editdistance-fast-implementation"
Y = xyz(tag1, tag2, tag3)
print(Y[0])