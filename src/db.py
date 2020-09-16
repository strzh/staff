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
class Flow(db.Model):
    __tablename__ = 'flow'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    postcmd = Column(String(1024))
    precmd = Column(String(1024))
    files = db.relationship("File", backref="flow")
    servers = db.relationship('Device',secondary=flows)

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
        return ssh
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
    def readfile(self, filename, replace=True):
        ssh = self.connect()
        shell = ssh.invoke_shell()
        rs=None
        split=""
        owner = None
        group = None
        mode = None
        try:
            sftp = ssh.open_sftp()
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
        if replace and not rs is None:
            name = filename[filename.rindex(os.sep)+1:]
            fi = File.query.filter_by(path=filename).filter_by(device_id=self.id).first()
            if fi is None:
                fi = File(device_id=self.id,text=rs,name=name,path=filename, mode=mode,type="Jinja", owner=owner,group=group)
            else:
                fi.name = name
                fi.text = rs
                fi.mode = mode
                fi.owner = owner
                fi.group = group
                fi.type = 'File'
            db.session.add(fi)
            db.session.commit()
        return rs
    def writefile(self,fileid):
        ssh = self.connect()
        shell = ssh.invoke_shell()
        fileContent = None
        
        temp = File.query.filter_by(id=fileid).first()
        dev = Device.query.filter_by(id=temp.machine_id).first()
        if temp.type == "Jinja":
            template = Template(temp.text)
            fileContent = template.render(server=dev)
        if temp.type == "file":
            fileContent = temp.text
        if temp.precmd is not None:
            ssh.exec_command( temp.precmd )
        try:
            sftp = self.ssh.open_sftp()
            fd=sftp.open(temp.path,mode='w')
            fd.writelines( fileContent )
            fd.close()
            sftp.chmod(temp.path, int(temp.mode))
            sftp.close()
        except paramiko.SSHException:
            current_app.logger.error("sftp failed")
            try:
                sin,sout,serror=ssh.exec_command("cat > "+temp.path+"<<EOF")
            except Exception as a:
                current_app.logger.error("command: {}".format(a))
        try:
            ssh.exec_command("chown "+temp.owner+":"+temp.group+" "+temp.path)
            ssh.exec_command( temp.postcmd)
        except Exception as d:
            current_app.logger.error("command: {}".format(d))


