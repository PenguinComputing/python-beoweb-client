# Python bindings to the Scyld Beoweb API

This is a client for the Scyld Beoweb API.  Scyld Beoweb is created and maintained by [Penguin Computing, Inc.](http://www.penguincomputing.com).

## Quickstart

```python
>>> from beowebclient.v1.client import BeowebClient
>>> beoclient = BeowebClient(<USERNAME>, <BEOWEBURL>)
>>> beoclient.cloudauth_login(<CLOUDAUTHURL>, <CLOUDAUTHKEY>, <CLOUDAUTHSECRET>)
{u'data': {u'sessionID': u'KkqHTifxjt0yu8dUrjU6'}, u'success': True}
>>> beoclient.get_jobs()
{u'data': {u'22482.pod': {u'job_state': u'C', u'uploadstat': u'NONE', u'stageoutstat': u'FINISHED', u'sched_status': None, u'stageoutlist': {u'/home/travis/podsh_jobs/travis_test.o22482': [None, None, u'/root/github/python-beoweb-client', u'FINISHED']}}, u'22709.pod': {u'job_state': u'C', u'uploadstat': u'NONE', u'stageoutstat': u'NONE', u'sched_status': None}, }, u'success': True}
>>> beoclient.submit_job({'test.sub': open('/root/test.sub', 'rb')})
{u'success': True, u'jobid': u'22783.pod'}
>>> beoclient.get_jobs(job_id="22783.pod")
{u'data': {u'22783.pod': {u'job_state': u'', u'uploadstat': u'NONE', u'stageoutstat': u'NONE', u'sched_status': {u'Resource_List': {u'nodes': u'1:ppn=1'}, u'job_radix': u'0', u'job_id': u'22783.pod', u'Mail_Points': u'a', u'job_state': u'Q', u'qtime': 1380747929, u'server': u'pod', u'queue': u'FREE', u'Join_Path': u'oe', u'Output_Path': u'beoweb.novalocal:/home/travis/podsh_jobs/travis_test.o22783', u'Error_Path': u'beoweb.novalocal:/home/travis/podsh_jobs/travis_test.e22783', u'Job_Owner': u'travis@beoweb.novalocal', u'Hold_Types': u'n', u'Job_Name': u'travis_test', u'Variable_List': u'PBS_O_QUEUE=FREE,PBS_O_HOME=/home/travis,PBS_O_LOGNAME=travis,PBS_O_PATH=/opt/scyld/scyld/python/bin:/opt/scyld/scyld/python/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/travis/bin,PBS_O_MAIL=/var/spool/mail/travis,PBS_O_SHELL=/bin/bash,PBS_O_LANG=en_US.UTF-8,PBS_O_INITDIR=/home/travis/podsh_jobs,PBS_O_WORKDIR=/home/travis/podsh_jobs,PBS_O_HOST=beoweb.novalocal,PBS_O_SERVER=pod', u'submit_args': u'-d /home/travis/podsh_jobs /home/travis/podsh_jobs/test.sub'}}}, u'success': True}
>>> beoclient.close()
>>> 
```
