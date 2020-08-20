from flask import render_template,current_app,request
from flask.views import MethodView
from comm import machine
class discover(MethodView):
    def get(self):
        return render_template("discover.html")
    def post(self):
        current_app.logger.debug(request.form)
        host=request.form.get("ips")
        filename=request.form.get("filename")
        data = machine(host).readfile(filename)
        return render_template("discover.html",host=host,filename=filename,data=data)
class new(MethodView):
    def get(self):
        return render_template("discover_new.html")
    def post(self):
        current_app.logger.debug(request.form)
        host=request.form.get("ips")
        admin=request.form.get("user")
        keystr=request.form.get("sshkey")
        password=request.form.get("password")
        keytype=request.form.get("keytype")
        mac=machine(host,user=admin,key=keystr,password=password,keytype=keytype)
        mac.sync()
        mac.discover()
        return render_template("discover_new.html")
