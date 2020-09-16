from flask import render_template,current_app,request
from flask.views import MethodView,View
import json
from db import Device, Flow, File
from app import db
class flow(MethodView):
    def get(self, id):
        if id is None:
            name = request.args.get("name")
            current_app.logger.debug(request.args)
            if name is None:
                ary=[]
                steps = Flow.query.all()
                heads=["ID","flowname",'servers','templates','']
                for i in steps:
                    ary.append([i.id,i.name,'',i.files,''])
                return render_template("flows.html",data=ary,heads=heads)
        else:
            step = Flow.query.get(id)
            ss = step.servers
            ss = step.files
            servers = Device.query.all()
            templates = File.query.all()
            return render_template("flow.html",data=step,servers=servers,templates=templates,editable='readonly')
    def post(self,id):
        if id is None:
            name = request.args.get("name")
            if name is None:
                return render_template("flows.html")
            else:
                step = Flow.query.filter_by(name=name).first()
                if step is None:
                    step = Flow(name=name)
                    db.session.add(step)
                    db.session.commit()
                    return str(step.id)
                else:
                     return str(step.id)
        else:
            current_app.logger.debug(request.form)
            step = Flow.query.filter_by(id=id).first()
            editable = request.form.get('editable')
            if editable == 'readonly':
                step.name = request.form.get('name')
                step.precmd = request.form.get('precmd')
                step.postcmd = request.form.get('postcmd')
                templates = request.form.getlist('templates')
                servers = request.form.getlist('servers')
                step.servers.clear()
                step.files.clear()
                for i in servers:
                    server = Device.query.filter_by(id=i).first()
                    step.servers.append(server)
                for i in templates:
                    temp = File.query.filter_by(id=i).first()
                    step.files.append(temp)
                db.session.add(step)
                db.session.commit()
            ss = step.servers
            ss = step.files
        editable = request.form.get("editable")
        servers = Device.query.all()
        templates = File.query.all()
        return render_template("flow.html",data=step,servers=servers,templates=templates,editable=editable)
    def delete(self, id):
        step = Flow.query.filter_by(id=id).first()
        temp = File.query.filter_by(step_id=id).first()
        if temp is None:
            db.session.delete(step)
            db.session.commit()
            return step.name
        else:
            return "failed"
