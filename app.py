#!/usr/bin/env python

from flask import Flask, jsonify, make_response
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
app = Flask(__name__)


project_list = [{
    "id": 1,
    "name": "Project 1"
},
{
    "id": 2,
    "name": "Project 2"
}]


@app.get("/projects")
def projects():
    app.logger.info({"event": "All Projects Listed"})
    return jsonify(project_list)


@app.get("/projects/<int:project_id>")
def project(project_id):
    app.logger.info({"event": f"Project {project_id} listed"})
    for item in range(len(project_list)):
        if project_list[item]["id"] == project_id:
            return jsonify(project_list[item])
    res = make_response("", 204)
    return res
