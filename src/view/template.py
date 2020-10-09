""" Template module """
from flask import render_template, current_app, request
from flask.views import MethodView
from db import File
from app import db


class TemplateView(MethodView):
    """ Template view class """
    @staticmethod
    def get(t_id):
        """ get template  """
        editable = request.args.get('editable')
        if editable is None:
            editable = 'readonly'
        temp = None
        if t_id is not None:
            temp = File.query.filter_by(id=t_id).first()
        if temp is None:
            ary = []
            heads = ["ID", "Name", 'path', 'Flows', '']
            templates = File.query.all()
            for i in templates:
                ary.append([i.id, "<a href='"+str(i.id)+"'>"+str(i.name)+"</a>", i.path, "<a href='/flow/"+str(i.flow_id)+"'>"+str(i.flow_id)+"</a>", i.id])
            return render_template("templates.html", data=ary, heads=heads)
        return render_template("template.html", fileobj=temp, key=t_id, editable=editable)

    @staticmethod
    def delete(t_id):
        """ remove a template """
        temp = File.query.filter_by(id=t_id).first()
        db.session.delete(temp)
        db.session.commit()
        return temp.name

    @staticmethod
    def post(t_id):
        """ update a template"""
        temp = File.query.filter_by(id=t_id).first()
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
            return render_template("template.html", fileobj=temp, editable=True)

        return render_template("template.html", fileobj=temp, key=t_id, editable=editable)

    @staticmethod
    def put(t_id):
        """ add new template """
        if t_id is None:
            name = request.form.get('name')
            if name is not None:
                temp = File(name=name)
                db.session.add(temp)
                db.session.commit()
                return str(temp.id)
        return "failed"

    @staticmethod
    def head(t_id):
        """ read template file """
        current_app.logger.debug(request.args)
        temp = File.query.filter_by(id=t_id).first()
        if temp is not None:
            temp.path = request.args.get('path')
            flow = temp.flow
            dev = flow.servers[0]
            dev.readfile(temp.path, fileid=t_id)
        current_app.logger.debug(dev)
        return "ok"
