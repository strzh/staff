"""  discover module """
import socket
from flask import render_template, current_app, request
from flask.views import MethodView
import paramiko
from app import db
from db import Device


class NewTemplate(MethodView):
    """ class for new template"""

    @staticmethod
    def get():
        """  default """
        dev_id = request.args.get("serverid")
        if dev_id is None:
            return render_template("discover.html")
        dev = Device.query.filter_by(id=dev_id).first()
        return render_template("discover.html", host=dev.ipaddr)

    @staticmethod
    def post():
        """  post """
        data = ""
        current_app.logger.debug(request.form)
        host = request.form.get("ips")
        filename = request.form.get("filename")
        ipaddr = socket.gethostbyname(host)
        machine = Device.query.filter_by(ipaddr=ipaddr).first()
        try:
            if machine is not None:
                data = machine.readfile(filename)
        except paramiko.SSHException as e:
            render_template(
                "discover.html", host=host, filename=filename, data=data, errmsg=e
            )
        return render_template("discover.html", host=host, filename=filename, data=data)


class NewDevice(MethodView):
    """  new server """

    @staticmethod
    def get(d_id):
        """  default """
        if d_id is not None:
            machine = Device.query.filter_by(id=d_id).first()
            if machine is None:
                return "failed"
            machine.discover()
            db.session.add(machine)
            db.session.commit()
            return "ok"
        return render_template("discover_new.html", data=d_id)

    @staticmethod
    def post():
        """  get new  """
        current_app.logger.debug(request.form)
        host = request.form.get("ips")
        admin = request.form.get("user")
        keystr = request.form.get("sshkey")
        password = request.form.get("password")
        keytype = request.form.get("keytype")
        ipaddr = socket.gethostbyname(host)
        fqdn = socket.getfqdn(ipaddr)
        hostname = fqdn.split(".")[0]
        machine = Device.query.filter_by(ipaddr=ipaddr).first()
        if machine is None:
            machine = Device(
                ipaddr=ipaddr,
                fqdn=fqdn,
                name=hostname,
                user=admin,
                keycode=keystr,
                password=password,
                keytype=keytype,
            )
        else:
            machine.user = admin
            machine.keycode = keystr if keystr != "" else None
            machine.password = password if password != "" else None
            machine.keytype = keytype
            machine.fqdn = fqdn
            machine.name = hostname
        try:
            machine.discover()
            db.session.add(machine)
            db.session.commit()
        except paramiko.SSHException as e:
            return render_template(
                "discover_new.html",
                host=machine.ipaddr,
                user=admin,
                data=keystr,
                errmsg=e,
            )
        return render_template(
            "discover_new.html", host=machine.ipaddr, user=admin, data=keystr
        )
