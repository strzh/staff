from flask import render_template,current_app
from flask.views import MethodView,View
import db

class template(MethodView):
    def get(self,id):
        redis = db.connect()
        temp = redis.hgetall(id)
        return render_template("template.html",redis=redis,key=id, editable=True)
    def post(self,id):
        return render_template("main.html")
class templates(View):
    def dispatch_request(self):
        redis = db.connect()
        ary=[]
        heads=['id',"filename"]
        templates = redis.smembers("template")
        for i in templates:
            ary.append(["<a href='"+i.decode()+"'>"+i.decode()+"</a>",redis.hget(i,"name")])
        return render_template("templates.html", data=ary,heads=heads)
