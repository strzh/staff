from flask import Flask, g, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import yaml
import gettext

#################
#  load config file
#################
cfg_file = "staff.yaml"
if os.path.isfile(cfg_file):
    path="./"
elif os.path.isfile(os.path.expanduser("~/.staff/"+cfg_file)):
    path=os.path.expanduser("~/.staff/")
else:
    print("Can not load the staff.yaml.")
    exit(0)
cfg = yaml.safe_load(open(path+cfg_file))

##################
# start flask app
###########
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.i18n')
gettext.install('lang', 'locale')
lang = cfg['server'].get('lang',['en'])
translations = gettext.translation('lang', 'locale', languages=lang)
app.jinja_env.install_gettext_translations(translations)
app.config.update(cfg)
#################
#  mysql engine
#################
if cfg.get('db') is None:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+path+'/staff.db'
elif cfg['db'].get('mysql') is not None:
    dbuser = cfg['db']['mysql'].get('user')
    dbpass = cfg['db']['mysql'].get('passwd')
    dbhost = cfg['db']['mysql'].get('host')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+dbuser+':'+dbpass+'@'+dbhost+':3306/staff?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

#################
#  flask app
#################

@app.route('/')
def mainpage():
    return render_template('main.html',dataset={})
@app.route('/entities')
def entities():
    return "Hello"
import view
app=view.registerRoute(app)
