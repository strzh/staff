from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from app import db
import paramiko
from flask import current_app
from io import StringIO
import os
import re

tomodeint = lambda a: ((a[1] == 'r')*4|(a[2]=='w')*2|(a[3]=='x')*1) *100 + ((a[4] == 'r')*4 | (a[5]=='w')*2 | (a[6]=='x')*1 )*10 + ((a[7] == 'r')*4|(a[8]=='w')*2|(a[9]=='x')*1)
class File(db.Model):
    __tablename__ = 'file_content'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    mode = Column(String(4))
    path = Column(String(1024))
    owner = Column(String(255))
    group = Column(String(255))
    postcmd = Column(String(1024))
    precmd = Column(String(1024))
    type = Column(String(10))
    text = Column(Text)
    machine_id = Column(Integer, ForeignKey('machine.id'))
class Device(db.Model):
    __tablename__ = "machine"
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
    files = db.relationship("File")
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
            stat = sftp.stat(filename)
            mode = stat.st_mode
            owner = stat.st_uid
            group = stat.st_gid
            sftp.close()
        except paramiko.SSHException:
            current_app.logger.error("sftp failed")
            try:
                sin,sout,serror=ssh.exec_command("cat " + filename)
                rs=split.join(sout.readlines())
                sin,sout,serror=ssh.exec_command("ls -l " + filename)
                ary = re.split('\s+',sout.readlines()[0])
                mode = tomodeint(ary[0])
                owner = ary[2]
                group = ary[3]
            except Exception as a:
                current_app.logger.error("command: {}".format(a))
        if replace and not rs is None:
            name = filename[filename.rindex(os.sep)+1:]
            fi = File.query.filter_by(path=filename).filter_by(machine_id=self.id).first()
            if fi is None:
                fi = File(machine_id=self.id,text=rs,name=name,path=filename, mode=mode,type="Jinja", owner=owner,group=group)
            else:
                fi.name = name
                fi.text = rs
                fi.mode = mode
                fi.owner = owner
                fi.group = group
                fi.type = 'Jinja'
            db.session.add(fi)
            db.session.commit()
        return rs
    def writefile(self,fileid):
        ssh = self.connect()
        shell = ssh.invoke_shell()
        
        temp = File.query.filter_by(id=fileid).first()
        if temp.precmd is not None:
            ssh.exec_command( temp.precmd )
        try:
            sftp = self.ssh.open_sftp()
            fd=sftp.open(temp.path,mode='w')
            fd.writelines(temp.text)
            fd.close()
            sftp.chmod(temp.path, int(temp.mode))
            sftp.close()
        except paramiko.SSHException:
            current_app.logger.error("sftp failed")
            sin,sout,serror=ssh.exec_command("cat > "+temp.path+"<<EOF")

