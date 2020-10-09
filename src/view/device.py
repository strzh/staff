""" device module """
from flask import render_template, current_app
from flask.views import MethodView
from db import Device
from app import db


class DeviceView(MethodView):
    """ device class """

    @staticmethod
    def get(d_id):
        """ get method """
        device = None
        if id is not None:
            device = Device.query.filter_by(id=d_id).first()
        if device is None:
            heads = ["ID", "Name", "OS", "ARCH", "IP", ""]
            ary = []
            devices = Device.query.all()
            for i in devices:
                ary.append([i.id, "<a href='"+str(i.id)+"'>"+i.name+"</a>", i.os, i.arch, i.ipaddr, i.id])
            return render_template("devices.html", dataset=ary, heads=heads)
        flows = device.flows
        current_app.logger.debug(flows)
        del(device.password)
        del(device.keycode)
        return render_template("device.html", data=device)

    @staticmethod
    def post():
        """ post method """
        return render_template("main.html")

    @staticmethod
    def delete(d_id):
        """ delete methoed """
        device = Device.query.filter_by(id=d_id).first()
        temp = device.flows
        if not temp:
            db.session.delete(device)
            db.session.commit()
            return device.name
        return "failed"
