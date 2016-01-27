from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

services = ["battleship", "y", "z"]

@app.route('/bower_components/<path:path>')
def send_bower(path):
    return send_from_directory('templates/bower_components', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('templates/js', path)

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory('templates/dist', path)

@app.route('/conversations/<string:service>/<string:roundNum>')
def conversations(service, roundNum):
    if service not in services:
        return "Service not found.", 404
    return render_template("pages/conversations.html", title="{0} - Round {1}".format(service,roundNum), round=roundNum, service=service)

@app.route('/')
@app.route('/index.html')
def index():
	return render_template("pages/index.html")
if __name__ == '__main__':
    app.run(debug=True)
