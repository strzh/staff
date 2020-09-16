from flask import render_template,current_app,request
from flask.views import MethodView,View
import json
from db import Device, File
from app import db
class devices(View):
    def dispatch_request(self):
        heads = ["ID","name","OS","ARCH","IP",""]
        ary = []
        devices = Device.query.all()
        for i in devices:
            ary.append([i.id,"<a href='"+str(i.id)+"'>"+i.name+"</a>",i.os,i.arch,i.ipaddr,i.id])
        return render_template("main.html",dataset=ary,heads=heads)
class device(MethodView):
    def get(self, id):
        device = Device.query.filter_by(id=id).first()
        flows = device.flows
        current_app.logger.debug(flows)
        del(device.password)
        del(device.keycode)
        return render_template("device.html",data=device)
    def post(self):
        return render_template("main.html")
    def delete(self, id):
        device = Device.query.filter_by(id=id).first()
        temp = Flow.query.filter_by(machine_id=id).first()
        if temp is None:
            db.session.delete(device)
            db.session.commit()
            return device.name
        else:
            return "failed"
