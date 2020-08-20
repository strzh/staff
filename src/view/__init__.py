from flask import current_app
from flask.views import MethodView
from . import device,discover,template
def registerRoute(app):
    app.add_url_rule("/discover/",view_func=discover.discover.as_view('discover'))
    app.add_url_rule("/discover/new",view_func=discover.new.as_view('discover.new'))
    app.add_url_rule("/device/",view_func=device.devices.as_view('devices'))
    app.add_url_rule("/device/<id>",view_func=device.device.as_view('device'))
    app.add_url_rule("/template/<id>",view_func=template.template.as_view('template'))
    app.add_url_rule("/template/",view_func=template.templates.as_view('templates'))
    return app
        
