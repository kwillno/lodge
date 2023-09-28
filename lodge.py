from flask import Flask, request
from jakt import jakt, timeslot, JaktReport, JaktError, JaktActiveError, JaktNotActiveError

app = Flask(__name__)

jkt = jakt()

@app.route("/")
def index():
    return "<p>This is lodge index</p>"

@app.route("/status")
@app.route("/status/")
def status():
    try:
        response = jkt.status()
        return response
    except JaktNotActiveError:
        return "No running timers"


@app.route("/stop")
@app.route("/stop/")
def stop():
    try:
        response = jkt.stop()
        return response
    except JaktNotActiveError:
        return "No running timers"

@app.route("/ls")
@app.route("/ls/")
def ls():
    timeslots = jkt.getTimeslots()

    timeslots.reverse()

    s = ""

    for ts in timeslots:
        s += f"<p>{ts.toHR(clickDisable = True)}</p>"

    return s

@app.route("/report")
@app.route("/report/")
def report():
    rpt = jkt.report()

    project_report = rpt.getProjectReport()

    return project_report


## API
@app.route("/api")
@app.route("/api/")
def api_index():

    response = {
        "http": "400",
        "http_msg": "Bad request"
    }

    return response

@app.route('/api/start/<project>')
@app.route('/api/start/<project>/')
@app.route('/api/start/<project>/<tags>')
@app.route('/api/start/<project>/<tags>/')
def api_start(project = None, tags = None):
    """
    API for starting timeslot
    project - The project name for the timeslot
    tags    - tags seperated by "&"
    """

    if not project:
        return {"error": 1, "msg":"Project must be given in start"}

    if tags:
        tags=tags.split("&")
    else:
        tags = ['<no tags>']

    try:
        response = jkt.start(project=project, tags=tags).toDict()
    except JaktActiveError:
        response = jkt.status()

    return response


@app.route("/api/status")
@app.route("/api/status/")
def api_status():
    try:
        response = jkt.status()
    except JaktNotActiveError:
        response = {
            'id': None,
            'start': None,
            'end': None,
            'project': None,
            'tags': None,
        }
    return response


@app.route("/api/stop")
@app.route("/api/stop/")
def api_stop():
    try:
        response = jkt.stop().toDict()
    except JaktNotActiveError:
        response = {
            'id': None,
            'start': None,
            'end': None,
            'project': None,
            'tags': None,
        }
    return response

@app.route("/api/add", methods=["PUT", "POST"])
@app.route("/api/add/", methods=["PUT", "POST"])
def api_add():

    try:
        ts = timeslot.from_json(request.json)
        response = jkt.add(ts)
        return response
    except KeyError as e:
        return {"error": 1, "msg": f"Invalid timeslot format on key {e}"}


@app.route("/api/edit/<id>", methods=["PUT", "POST"])
@app.route("/api/edit/<id>/", methods=["PUT", "POST"])
def api_edit(id):
    """
    API endpoint for editing an already existing timeslot.
    id  - id of the timeslot to change
    """
    ts = timeslot.from_json(request.json)
    response = jkt.editTimeslot(queryId = id, ts = ts).toDict()
    return response

@app.route("/api/ls")
@app.route("/api/ls/")
def api_ls():
    timeslots = jkt.getTimeslots()

    timeslots.reverse()

    for i in range(len(timeslots)):
        timeslots[i] = timeslots[i].toDict()

    return timeslots

@app.route("/api/ls/<id>")
@app.route("/api/ls/<id>/")
def api_ls_index(id):
    timeslots = jkt.getTimeslots()

    for i in range(len(timeslots)):
        if timeslots[i].id == id:
            return timeslots[i].toDict()

    return {}

@app.route("/api/report")
@app.route("/api/report/")
@app.route("/api/report/<project>")
@app.route("/api/report/<project>/")
@app.route("/api/report/<project>/<tags>")
@app.route("/api/report/<project>/<tags>/")
def api_report(project = None, tags = None):

    if project:
        rpt = jkt.report()
        project_report = rpt.getProjectReport(project=project)[0]

        tag_report = rpt.getTagReport(project=project)

        project_report["tags"] = tag_report

        return project_report

    else:
        rpt = jkt.report()

        project_report = rpt.getProjectReport()
        for i in range(len(project_report)):
            project_report[i]["tags"] = rpt.getTagReport(project=project_report[i]["project"])

        return project_report
