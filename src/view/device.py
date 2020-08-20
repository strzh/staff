from flask import render_template,current_app,request
from flask.views import MethodView,View
import db
import json
class devices(View):
    def dispatch_request(self):
        redis = db.connect()
        heads = ["name","OS","ARCH","IP"]
        ary = []
        devices = redis.smembers("devices")
        for i in devices:
            ary.append(["<a href='"+i.decode()+"'>"+i.decode()+"</a>",redis.hget(i,"os"),redis.hget(i,"arch"),redis.hget(i,"ipaddr")])
        return render_template("main.html",dataset=ary,heads=heads)
class device(MethodView):
    def get(self, id):
        redis = db.connect()
        device = redis.hgetall(id)
        del(device[b"password"])
        del(device[b"key"])
        ts = redis.hvals(device[b'process'])
        current_app.logger.debug(ts)
        device[b'process'] = b" ".join( b"<a href='/template/"+i+b"'>"+i+b"</a>" for i in ts)
        return render_template("device.html",data=device)
    def post(self):
        return render_template("main.html")
