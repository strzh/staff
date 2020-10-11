""" FLow control"""
from flask import render_template, current_app, request
from flask.views import MethodView
from db import Device, Flow, File
from app import db


class FlowView(MethodView):
    """ FLow View class """

    @staticmethod
    def get(f_id):
        """ get method """
        step = None
        if f_id is not None:
            step = Flow.query.get(f_id)
        if step is None:
            name = request.args.get("name")
            current_app.logger.debug(request.args)
            if name is None:
                ary = []
                steps = Flow.query.all()
                heads = ["ID", "flowname", "servers", "templates", ""]
                for i in steps:
                    files = ""
                    devs = ""
                    for j in i.files:
                        files = (
                            files
                            + '<a href="/template/'
                            + str(j.id)
                            + '">'
                            + j.name
                            + "</a>&nbsp;"
                        )
                    for k in i.servers:
                        devs = (
                            devs
                            + '<a href="/device/'
                            + str(k.id)
                            + '">'
                            + k.name
                            + "</a>&nbsp;"
                        )
                    ary.append(
                        [
                            i.id,
                            "<a href='/flow/" + str(i.id) + "' >" + i.name + "</a>",
                            devs,
                            files,
                            "",
                        ]
                    )
                return render_template("flows.html", data=ary, heads=heads)
            return name
        x = step.servers
        x = step.files
        servers = Device.query.all()
        templates = File.query.all()
        return render_template(
            "flow.html",
            data=step,
            servers=servers,
            templates=templates,
            editable="readonly",
        )

    @staticmethod
    def post(f_id):
        """ post method """
        if f_id is not None:
            current_app.logger.debug(request.form)
            step = Flow.query.filter_by(id=f_id).first()
            editable = request.form.get("editable")
            if editable == "readonly":
                step.name = request.form.get("name")
                step.precmd = request.form.get("precmd")
                step.postcmd = request.form.get("postcmd")
                templates = request.form.getlist("templates")
                servers = request.form.getlist("servers")
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
            x = step.servers
            x = step.files
        editable = request.form.get("editable")
        servers = Device.query.all()
        templates = File.query.all()
        return render_template(
            "flow.html",
            data=step,
            servers=servers,
            templates=templates,
            editable=editable,
        )

    @staticmethod
    def put(f_id):
        """ new Flow """
        if f_id is None:
            name = request.form.get("name")
            if name is None:
                return render_template("flows.html")
            step = Flow.query.filter_by(name=name).first()
            if step is None:
                step = Flow(name=name)
                db.session.add(step)
                db.session.commit()
                return str(step.id)
            return str(step.id)
        return "failed"

    @staticmethod
    def delete(f_id):
        """ remove flow """
        step = Flow.query.filter_by(id=f_id).first()
        temp = step.files
        if not temp:
            db.session.delete(step)
            db.session.commit()
            return step.name
        return "failed"

    @staticmethod
    def head(f_id):
        """ write to server """
        step = Flow.query.filter_by(id=f_id).first()
        if step is not None:
            rs = step.sync_servers()
        return "ok"
