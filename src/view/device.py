import gettext
from flask import render_template,current_app,request
from flask.views import MethodView,View
import json
from db import Device, File
from app import db
class device(MethodView):
    def get(self, id):
        device = None
        if id is not None:
             device = Device.query.filter_by(id=id).first()
        if device is None:
            heads = ["ID","Name","OS","ARCH","IP",""]
            ary = []
            devices = Device.query.all()
            for i in devices:
                ary.append([i.id,"<a href='"+str(i.id)+"'>"+i.name+"</a>",i.os,i.arch,i.ipaddr,i.id])
            return render_template("devices.html",dataset=ary,heads=heads)
        else:
            flows = device.flows
            current_app.logger.debug(flows)
            del(device.password)
            del(device.keycode)
            return render_template("device.html",data=device)
    def post(self):
        return render_template("main.html")
    def delete(self, id):
        device = Device.query.filter_by(id=id).first()
        temp = device.flows
        if not temp :
            db.session.delete(device)
            db.session.commit()
            return device.name
        else:
            return "failed"
