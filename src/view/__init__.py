""" view """
# from flask import current_app, request
# from flask.views import MethodView
from view.flow import FlowView
from view.template import TemplateView
from view.device import DeviceView
from view import discover


def registerRoute(app):
    """ register Route"""
    app.add_url_rule("/discover/", view_func=discover.NewTemplate.as_view("discover"))
    app.add_url_rule(
        "/discover/dev",
        defaults={"d_id": None},
        view_func=discover.NewDevice.as_view("discover.device.new"),
    )
    app.add_url_rule(
        "/discover/dev/<d_id>", view_func=discover.NewDevice.as_view("discover.device")
    )
    app.add_url_rule(
        "/device/", defaults={"d_id": None}, view_func=DeviceView.as_view("devices")
    )
    app.add_url_rule("/device/<d_id>", view_func=DeviceView.as_view("device"))
    app.add_url_rule("/template/<t_id>", view_func=TemplateView.as_view("template"))
    app.add_url_rule(
        "/template/",
        defaults={"t_id": None},
        view_func=TemplateView.as_view("templates"),
    )
    app.add_url_rule(
        "/flow/", defaults={"f_id": None}, view_func=FlowView.as_view("flows")
    )
    app.add_url_rule("/flow/<f_id>", view_func=FlowView.as_view("flow"))
    return app
