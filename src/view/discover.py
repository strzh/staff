from flask import render_template,current_app,request
from flask.views import MethodView
import socket
from app import db
from db import Device
class template(MethodView):
    def get(self):
        dev_id = request.args.get('serverid')
        if dev_id is None:
            return render_template("discover.html")
        else:
            dev = Device.query.filter_by(id=dev_id).first()
            return render_template("discover.html",host=dev.ipaddr)
    def post(self):
        data=''
        current_app.logger.debug(request.form)
        host=request.form.get("ips")
        filename=request.form.get("filename")
        ipaddr = socket.gethostbyname(host)
        machine = Device.query.filter_by(ipaddr=ipaddr).first()
        if machine is not None:
             data = machine.readfile(filename)
        return render_template("discover.html",host=host,filename=filename,data=data)
class device(MethodView):
    def get(self, id):
        if id is not None:
            machine = Device.query.filter_by(id=id).first()
            if machine is None:
                return "failed"
            else:
                machine.discover()
                db.session.add(machine)
                db.session.commit()
            return "ok"
        else:
            return render_template("discover_new.html", data=id)
    def post(self,id):
        current_app.logger.debug(request.form)
        host=request.form.get("ips")
        admin=request.form.get("user")
        keystr=request.form.get("sshkey")
        password=request.form.get("password")
        keytype=request.form.get("keytype")
        ipaddr = socket.gethostbyname(host)
        fqdn = socket.getfqdn(ipaddr)
        hostname = fqdn.split('.')[0]
        machine = Device.query.filter_by(ipaddr=ipaddr).first()
        if machine is None:
            machine = Device(ipaddr=ipaddr,fqdn=fqdn,name=hostname,user=admin,keycode=keystr,password=password,keytype=keytype)
        else:
            machine.user=admin
            machine.keycode=keystr if keystr != '' else None
            machine.password=password if password != '' else None
            machine.keytype=keytype 
            machine.fqdn = fqdn
            machine.name = hostname
        machine.discover()
        db.session.add(machine)
        db.session.commit()
        return render_template("discover_new.html", host=machine.ipaddr,user=admin,data=keystr)
