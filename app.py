#!/usr/bin/env python
import json

from flask import Flask, jsonify, make_response, request
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
    """List all projects"""
    app.logger.info({"event": "All Projects Listed"})
    return jsonify(project_list)


@app.get("/projects/<int:project_id>")
def project(project_id):
    """Get a specified project, by project id"""
    app.logger.info({"event": f"Project {project_id} listed"})
    for item in range(len(project_list)):
        if project_list[item]["id"] == project_id:
            return jsonify(project_list[item])
    res = make_response("", 204)
    return res


@app.post("/projects")
def create_project():
    """"Create a new project"""
    app.logger.info({"request": request.form.get('project_name')})
    if request.form['project_name']:
        project_name = json.loads(request.form.get('project_name'))
        project_list.append({"id": 3, "name": project_name})
        return jsonify(project_list)
    else:
        res = make_response("Project Name cannot be empty", 400)
        return res


@app.put("/projects/<int:project_id>")
def update_project(project_id):
    """Update a project, specified by project id"""
    app.logger.info({"request": request.form.get('project_name')})
    if request.form['project_name']:
        project_name = json.loads(request.form.get('project_name'))
        for item in range(len(project_list)):
            if project_list[item]["id"] == project_id:
                project_list[item]['name'] = project_name
                return jsonify(project_list)
        res = make_response("Project ID is incorrect", 400)
        return res
    else:
        res = make_response("Project Name cannot be empty", 400)
        return res
