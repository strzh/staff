from app import db
from sqlalchemy import Column, Integer, String, Text
import paramiko
from flask import current_app
from io import StringIO
import os
import re
from jinja2 import Template

tomodeint = lambda a: ((a[1] == 'r')*4|(a[2]=='w')*2|(a[3]=='x')*1) *100 + ((a[4] == 'r')*4 | (a[5]=='w')*2 | (a[6]=='x')*1 )*10 + ((a[7] == 'r')*4|(a[8]=='w')*2|(a[9]=='x')*1)
flows = db.Table('flows',
        Column('flow_id', Integer, db.ForeignKey('flow.id')),
        Column('device_id', Integer, db.ForeignKey('device.id'))
)
class File(db.Model):
    __tablename__ = 'file_content'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    mode = Column(String(4))
    path = Column(String(1024))
    owner = Column(String(255))
    group = Column(String(255))
    type = Column(String(10))
    text = Column(Text)
    flow_id = Column(Integer, db.ForeignKey('flow.id'))
    device_id = Column(Integer, db.ForeignKey('device.id'))
    def writeto(self,dev):
        shell = dev.ssh.invoke_shell()
        fileContent = None
        if self.type == "Shell":
            try: 
                sin,sout,serror=ssh.exec_command(self.text)
            except Exception as d:
                current_app.logger.error("command: {}".format(d))
            return True
        if self.type == "Jinja":
            template = Template(self.text)
            fileContent = template.render(server=dev)
        if self.type == "File":
            fileContent = self.text
        try:
            sftp = dev.ssh.open_sftp()
            fd=sftp.open(self.path,mode='w')
            fd.writelines( fileContent )
            fd.close()
            sftp.chmod(self.path, int(self.mode))
            sftp.close()
        except paramiko.SSHException:
            current_app.logger.error("sftp failed")
            try:
                sin,sout,serror=dev.ssh.exec_command("cat > "+self.path+"<<EOF")
            except Exception as a:
                current_app.logger.error("command: {}".format(a))
        try:
            dev.ssh.exec_command("chown "+self.owner+":"+self.group+" "+self.path)
        except Exception as d:
            current_app.logger.error("command: {}".format(d))
        return True

class Flow(db.Model):
    __tablename__ = 'flow'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    postcmd = Column(String(1024))
    precmd = Column(String(1024))
    files = db.relationship("File", backref="flow")
    servers = db.relationship('Device',secondary=flows)
    def syncToservers(self):
        for dev in self.servers:
            dev.connect()
            if self.precmd is not None:
                dev.exec_command(self.precmd)
            for temp in self.files:
                temp.writeto(dev)
            if self.postcmd is not None:
                dev.exec_command(self.postcmd)
            dev.ssh.close()
        return True

class Device(db.Model):
    __tablename__ = "device"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    fqdn = Column(String(255))
    ipaddr = Column(String(255))
    user = Column(String(100))
    keytype = Column(String(100))
    password = Column(String(100))
    keycode = Column(String(4096))
    cmd = Column(String(1024))
    os = Column(String(255))
    arch = Column(String(255))
    flows = db.relationship('Flow',secondary=flows)
    ssh = None
    def loadkey(self):
        key=None
        try:
            key = paramiko.RSAKey(file_obj=StringIO(self.keycode))
        except Exception as e:
            try:
                key = paramiko.DSSKey(file_obj=StringIO(self.keycode))
            except Exception as e:
                current_app.logger.debug(e)
                try:
                    key = paramiko.Ed25519Key(file_obj=StringIO(self.keycode))
                except Exception as e:
                    try:
                        key = paramiko.ECDSAKey(file_obj=StringIO(self.keycode))
                    except Exception as e:
                        current_app.logger.debug("The key is None")
            
        return key
    def connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = self.loadkey()
        if key is None or self.keytype == "password":
            ssh.connect(self.ipaddr,username=self.user,password=self.password)
        else:
            ssh.connect(self.ipaddr,username=self.user,password=self.password,pkey=key)
        self.ssh=ssh
        return ssh
    def exec_command(self,cmds):
        try:
            sin,sout,serror = self.ssh.exec_command( cmds )
        except Exception as a:
            current_app.logger.error("command: {}".format(a))
        return serror is None
    def discover(self):
        ssh = self.connect()
        shell = ssh.invoke_shell()
        sin,sout,serr = ssh.exec_command("uname -n")
        self.name=sout.readline().strip()
        sin,sout,serr = ssh.exec_command("uname -m")
        self.arch=sout.readline().strip()
        sin,sout,serr = ssh.exec_command("uname -o")
        self.os=sout.readline().strip()
        ssh.close()
    def readfile(self, filename,filetype="File",fileid=None, replace=True):
        ssh = self.connect()
        shell = ssh.invoke_shell()
        rs=None
        split=""
        owner = None
        group = None
        mode = None
        try:
            sftp = ssh.open_sftp()
            current_app.logger.debug(filename)
            fd=sftp.open(filename)
            rs=split.join(fd.readlines())
            fd.close()
            sftp.close()
        except paramiko.SSHException:
            current_app.logger.error("sftp failed")
            try:
                sin,sout,serror=ssh.exec_command("cat " + filename)
                rs=split.join(sout.readlines())
            except Exception as a:
                current_app.logger.error("command: {}".format(a))
        try:        
            sin,sout,serror=ssh.exec_command("ls -l " + filename)
            ary = re.split('\s+',sout.readlines()[0])
            mode = tomodeint(ary[0])
            owner = ary[2]
            group = ary[3]
        except Exception as e:
            current_app.logger.error("command: {}".format(e))
        if replace and rs is not None:
            name = filename[filename.rindex(os.sep)+1:]
            if fileid is None:
                fi = File.query.filter_by(path=filename).filter_by(device_id=self.id).first()
            else:
                fi = File.query.filter_by(id=fileid).first()
            if fi is None:
                fi = File(device_id=self.id,text=rs,name=name,path=filename, mode=mode,type=filetype, owner=owner,group=group)
            else:
                fi.name = name
                fi.text = rs
                fi.mode = mode
                fi.owner = owner
                fi.group = group
                fi.type = filetype
            db.session.add(fi)
            db.session.commit()
        current_app.logger.debug(rs)
        return rs


