#!/usr/bin/env python

from flask import Flask, jsonify, make_response

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
    return jsonify(project_list)


@app.get("/projects/<int:project_id>")
def project(project_id):
    for item in range(len(project_list)):
        print(type(project_list[item]))
        print(project_list[item])
        if project_list[item]["id"] == project_id:
            return jsonify(project_list[item])
    res = make_response("", 204)
    return res
