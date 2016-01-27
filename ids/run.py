from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/bower_components/<path:path>')
def send_bower(path):
    return send_from_directory('templates/bower_components', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('templates/js', path)

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory('templates/dist', path)

@app.route('/')
def index():
    return render_template("pages/index.html", title="Asdf")

if __name__ == '__main__':
    app.run(debug=True)
