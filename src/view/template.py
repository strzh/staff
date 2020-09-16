from flask import render_template,current_app,request
from flask.views import MethodView,View
from db import File, Device
from app import db

class template(MethodView):
    def get(self,id,editable=True):
        editable= request.args.get('editable')
        temp = File.query.filter_by(id=id).first()
        machine = Device.query.filter_by(id=temp.machine_id).first()
        temp.hostname = machine.name
        return render_template("template.html",fileobj=temp,key=id, editable=editable)
    def delete(self,id):
        temp = File.query.filter_by(id=id).first()
        db.session.delete(temp)
        db.session.commit()
        return temp.name
    def post(self,id):
        temp = File.query.filter_by(id=id).first()
        current_app.logger.debug(request.form)
        temp.path = request.form.get('path')
        temp.owner = request.form.get('owner')
        temp.group = request.form.get('group')
        temp.mode = request.form.get('mode')
        temp.precmd = request.form.get('precmd')
        temp.postcmd = request.form.get('postcmd')
        temp.text = request.form.get('text')
        db.session.add(temp)
        db.session.commit()
        return render_template("template.html",fileobj=temp,key=id,editable=False)
class templates(View):
    def dispatch_request(self):
        ary=[]
        heads=["ID","filename",'path','server','']
        templates = File.query.all()
        for i in templates:
            ary.append([i.id,"<a href='"+str(i.id)+"'>"+str(i.name)+"</a>",i.path,"<a href='/device/"+str(i.device_id)+"'>"+str(i.device_id)+"</a>",i.id])
        return render_template("templates.html", data=ary,heads=heads)
