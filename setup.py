import sys

from setuptools import setup, find_packages

requires = [
    'requests',
    'python-cloud-auth-client == 0.1.1'
]

pyversion = sys.version_info[:2]
if pyversion < (2, 6):
    requires.append('simplejson')

setup(
    name="python-beoweb-client",
    version="0.1.2",
    description="Client library for Scyld Beoweb API",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent"
    ],
    author="Penguin Computing, Inc.",
    maintainer="Penguin Computing, Inc.",
    maintainer_email="support@penguincomputing.com",
    url="http://www.penguincomputing.com",
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=requires,
    dependency_links=['https://github.com/PenguinComputing/python-cloud-auth-client/archive/v0.1.1.tar.gz#egg=python_cloud_auth_client-0.1.1']
)
