from flask import Flask
from jakt import jakt, timeslot, JaktReport, JaktError, JaktActiveError, JaktNotActiveError

app = Flask(__name__)

jkt = jakt()

@app.route("/")
def index():
    return "<p>This is lodge index</p>"

@app.route("/status")
def status():
    try:
        response = jkt.status()
        return response
    except JaktNotActiveError:
        return "No running timers"


@app.route("/stop")
def stop():
    try:
        response = jkt.stop()
        return response
    except JaktNotActiveError:
        return "No running timers"

@app.route("/ls")
def ls():
    timeslots = jkt.getTimeslots()

    timeslots.reverse()

    s = ""

    for ts in timeslots:
        s += f"<p>{ts.toHR()}</p>"

    return s

@app.route("/report")
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

@app.route('/api/start/<project>/<tags>/')
def api_start(project, tags):
    """
    API for starting timeslot
    project - The project name for the timeslot
    tags    - tags seperated by "&"
    """

    tags=tags.split("&")

    if tags == ['']:
        tags = ['<no tags>']

    try:
        response = jkt.start(project=project, tags=tags).toDict()
    except JaktActiveError:
        response = jkt.status()

    return response


@app.route("/api/status")
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

@app.route("/api/ls")
def api_ls():
    timeslots = jkt.getTimeslots()

    timeslots.reverse()

    for i in range(len(timeslots)):
        timeslots[i] = timeslots[i].toDict()

    return timeslots

@app.route("/api/report")
def api_report():
    rpt = jkt.report()

    project_report = rpt.getProjectReport()

    return project_report
