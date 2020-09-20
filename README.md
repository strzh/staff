# Configuration backup and restore tool

This tool can help us backup the configuration of linux type system. These systems should have ssh admmin users.

## This configuration file is staff.yaml, like below:

```yaml
server:
  port: 8888
  debug: true
  lang:
    - en
```
If you want to store the password or key in your own mysql db, it should like this
```yaml
server:
  port: 8888
  debug: true
  lang:
    - zh_CN
  db:
    mysql:
    host: xxx
    user: xxx
    passwd: xxx
```
currently the package is not implemented.
please goto dir src execute, you need flask installed:
```
./__main__.py
```

This tool support 2 English and Chinese.

if you like it and please raise the bugs or new features. 
