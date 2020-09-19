from flask import render_template,current_app,request
from flask.views import MethodView,View
from db import File, Device
from app import db

class template(MethodView):
    def get(self,id,editable=True):
        editable= request.args.get('editable')
        temp = None
        if id is not None:
            temp = File.query.filter_by(id=id).first()
        if temp is None:
            ary=[]
            heads=["ID",_("Name"),_('path'),_('Flows'),'']
            templates = File.query.all()
            for i in templates:
                ary.append([i.id,"<a href='"+str(i.id)+"'>"+str(i.name)+"</a>",i.path,"<a href='/flow/"+str(i.flow_id)+"'>"+str(i.flow_id)+"</a>",i.id])
            return render_template("templates.html", data=ary,heads=heads)
        return render_template("template.html",fileobj=temp,key=id, editable='readonly')
    def delete(self,id):
        temp = File.query.filter_by(id=id).first()
        db.session.delete(temp)
        db.session.commit()
        return temp.name
    def post(self,id):
        current_app.logger.debug(request.form)
        temp = File.query.filter_by(id=id).first()
        editable = request.form.get('editable')
        if editable == 'readonly':
            if temp is None:
                temp = File()
            temp.name = request.form.get('name')
            temp.path = request.form.get('path')
            temp.owner = request.form.get('owner')
            temp.group = request.form.get('group')
            temp.mode = request.form.get('mode')
            temp.precmd = request.form.get('precmd')
            temp.postcmd = request.form.get('postcmd')
            temp.text = request.form.get('text')
            temp.type = request.form.get('type')
            db.session.add(temp)
            db.session.commit()
        else:
            if temp is None:
                temp = File()
            return render_template("template.html",fileobj=temp,editable=True)
        
        return render_template("template.html",fileobj=temp,key=id,editable=editable)
    def put(self,id):
        if id is None:
            name = request.form.get('name')
            if name is not None:
                temp = File(name=name)
                db.session.add(temp)
                db.session.commit()
                return str(temp.id)
        else:
            return "failed"
    def head(self,id):
        current_app.logger.debug(request.args)
        temp = File.query.filter_by(id=id).first()
        if temp is not None:
            temp.path = request.args.get('path')
            flow = temp.flow
            dev = flow.servers[0]
            dev.readfile(temp.path,fileid=id)
        current_app.logger.debug(dev)
        return "ok"
