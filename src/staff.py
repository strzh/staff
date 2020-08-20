from flask import Flask,render_template,g
app = Flask(__name__)
@app.route('/')
def mainpage():
    return render_template('main.html',dataset={})
@app.route('/entities')
def entities():
    return "Hello"
import view
app=view.registerRoute(app)
