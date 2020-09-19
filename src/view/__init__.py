from flask import current_app,request
from flask.views import MethodView
from . import device,discover,template,flow
def registerRoute(app):
    app.add_url_rule("/discover/",view_func=discover.template.as_view('discover'))
    app.add_url_rule("/discover/dev",defaults={'id':None},view_func=discover.device.as_view('discover.device.new'))
    app.add_url_rule("/discover/dev/<id>",view_func=discover.device.as_view('discover.device'))
    app.add_url_rule("/device/",defaults={'id':None},view_func=device.device.as_view('devices'))
    app.add_url_rule("/device/<id>",view_func=device.device.as_view('device'))
    app.add_url_rule("/template/<id>",view_func=template.template.as_view('template'))
    app.add_url_rule("/template/",defaults={'id':None},view_func=template.template.as_view('templates'))
    app.add_url_rule("/flow/", defaults={'id':None}, view_func=flow.flow.as_view('flows'))
    app.add_url_rule("/flow/<id>", view_func=flow.flow.as_view('flow'))
    return app
        
