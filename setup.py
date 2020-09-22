from setuptools import setup, find_packages

PACKAGES = find_packages(exclude=["tests", "tests.*"])

REQUIRES = [
   "Flask",
   "redis",
   'paramiko',
   "flask_sqlalchemy",
   "PyYAML",
]
setup(name='managementtool',
      version="0.2",
      description="An template modifying tools",
      author="lei.zhang@sap.com",
      author_email="lei.zhang@sap.com",
      packages=PACKAGES,
      include_package_data=True,
      install_requires=REQUIRES,
#      package_data = {"cmdb":["templates/*.html","static"]}
)
