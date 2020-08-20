from flask import current_app, g
import paramiko
import db
import socket
from io import StringIO
from lei import *

class machine():
    def __init__(self,host,user=None, keytype=None,key=None,password=None):
        try:
            self.ipaddr=socket.gethostbyname(host)
        except:
            self.ipaddr=None
        try:
            self.fqdn=socket.gethostbyaddr(host)[0]
            self.hostname=self.fqdn.split('.')[0]
        except:
            self.hostname=None
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.shell=None
        self.redis = db.connect()
        self.user=user
        self.keytype=keytype
        self.keycode=key
        self.password=password
        self.key=None
        self.sync()
    def sync(self):
        if not self.hostname is None and not self.ipaddr is None:
            self.redis.sadd("devices",self.hostname)
            self.redis.hset(self.hostname,"ipaddr",self.ipaddr)
            if not self.fqdn is None:
                self.redis.hset(self.hostname,"fqdn",self.fqdn)
            '''user'''
            if self.user is None:
                self.user=self.redis.hget(self.hostname,"admin")
            else:
                self.redis.hset(self.hostname,"admin",self.user)
            '''key type'''
            if self.keytype is None:
                self.keytype=self.redis.hget(self.hostname,"keytype")
            else:
                self.redis.hset(self.hostname,"keytype",self.keytype)
            ''''''
            if self.password is None:
                self.password = self.redis.hget(self.hostname,"password")
            else:
                self.redis.hset(self.hostname,"password",self.password)
            ''''''
            if self.keycode is None or len(self.keycode) < 10:
                self.keycode = self.redis.hget(self.hostname,"key")
                self.keycode = self.keycode.decode()
            else:
                self.redis.hset(self.hostname,"key",self.keycode)
            return True
        return False
    def connection(self):
        self.key = self.loadkey()
        if self.key is None:
             current_app.logger.debug(self.key)
             self.ssh.connect(self.ipaddr,username=self.user,password=self.password)
        else:
             self.ssh.connect(self.ipaddr,username=self.user,password=self.password,pkey=self.key)
        self.shell=self.ssh.invoke_shell()
        return self.ssh
    def loadkey(self):
        self.key=None
        try:
            self.key = paramiko.RSAKey(file_obj=StringIO(self.keycode))
        except Exception as e:
            try:
                self.key = paramiko.DSSKey(file_obj=StringIO(self.keycode))
            except Exception as e:
                current_app.logger.debug(e)
                try:
                    self.key = paramiko.Ed25519Key(file_obj=StringIO(self.keycode))
                except Exception as e:
                    try:
                        self.key = paramiko.ECDSAKey(file_obj=StringIO(self.keycode))
                    except Exception as e:
                        current_app.logger.debug("The key is None")
            
        return self.key
    def discover(self):
        if self.shell is None or self.shell.closed:
            self.connection()
        sin,sout,serr = self.ssh.exec_command("uname -m")
        self.arch=sout.readline().strip()
        self.redis.hset(self.hostname,"arch",self.arch)
        sin,sout,serr = self.ssh.exec_command("uname -o")
        self.os=sout.readline().strip()
        self.redis.hset(self.hostname,"os",self.os)
    def readfile(self,file,replace=True):
        rs=None
        split=""
        if self.shell is None or self.shell.closed:
            self.connection()
        try:
            sftp = self.ssh.open_sftp()
            fd=sftp.open(file)
            rs=split.join(fd.readlines())
            fd.close()
            sftp.close()
        except paramiko.SSHException:
            current_app.logger.error("sftp failed")
        try:
            sin,sout,serror=self.ssh.exec_command("cat " + file)
            rs=split.join(sout.readlines())
        except Exception as a:
            current_app.logger.error("command: {}".format(a))
        if replace and not rs is None:
            process = self.redis.hget(self.hostname,"process")
            tempid = None
            if process is None:
                process = self.hostname + id_generator()
                self.redis.hset(self.hostname,"process",process)
            else:
                tempid = self.redis.hget(process,file)
            if tempid is None:
                tempid = self.hostname + id_generator()
                self.redis.hset(process,file,tempid)
                self.redis.sadd("template",tempid)
            self.redis.hset(tempid,"file",rs)
            self.redis.hset(tempid,"name",file)
        return rs
    def writefile(self,tempid):
        if self.shell is None or self.shell.closed:
            self.connection()
        filedata = self.redis.hget(tempid,"file")
        filename = self.redis.hget(tempid,"name")
        try:
            sftp = self.ssh.open_sftp()
            fd=sftp.open(file,mode='w')
            fd.writelines(filedata)
            fd.close()
            sftp.close()
        except paramiko.SSHException:
            current_app.logger.error("sftp failed")


