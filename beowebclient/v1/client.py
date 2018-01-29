# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2013 Penguin Computing, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import os
import logging
import cookielib

import requests
try:
    import simplejson as json
except ImportError:
    import json

from beowebclient.common.client import HTTPClient
from beowebclient.common import exceptions as beowebexc

LOG = logging.getLogger(__name__)


class BeowebClient(HTTPClient):
    """Class that implements the Beoweb API

    Create an instance with the Beoweb connection details::

        >>> client = BeowebClient(UNAME, HOSTNAME)

    Then login to gain a session ID and call methods

        >>> client.password_login(PASSWORD)
        >>> client.get_jobs()
    """

    def __init__(self, user, beoweb_host, ssl=True, port=None, cjfile=None):
        super(BeowebClient, self).__init__(user, beoweb_host, ssl=ssl,
                                           port=port)
        self.client.params.update({'format': "json"})

        self.cjfile = None
        if cjfile:
            self.cjfile = cjfile
            self.cj = cookielib.LWPCookieJar(self.cjfile)
            if os.path.isfile(self.cjfile):
                try:
                    self.cj.load(self.cjfile)
                except cookielib.LoadError as e:
                    LOG.error(("Problem occured loading CookieJar file: %s, "
                               "error: %s"), self.cjfile, e)
                    LOG.error("Attempting to destroy and recreate file")
                    os.remove(self.cjfile)
            self.client.cookies = self.cj

    def close(self):
        """finalize any connections with Beoweb"""
        if self.cjfile:
            self.cj.save(filename=self.cjfile)
        self.client.close()

    def password_login(self, password):
        """Attempt to gain a session ID from beoweb using username/password

        Requires the "crypt" library, which is only found on *nix OS's

        Returns beoweb results if no error is found. Beoweb sets the session
        ID in a cookie, so the session ID returned may not be needed depending
        on configuration

        :param password: plaintext string containing password to send
        :returns: Beoweb JSON data

        """

        try:
            from crypt import crypt
        except ImportError, e:
            LOG.critical("Unable to use crypt library.")
            raise beowebexc.BeowebAuthError(
                "Unable to use crypt library. Password auth not supported")

        params = {"user": self.user}
        try:
            resp = self.request("auth/request_public_keys", "GET",
                                params=params)
        except requests.exceptions.HTTPError:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")

        keys = json.loads(resp.text)
        mode = keys['data']['mode']
        ts = keys['data']['tempSalt']
        ps = keys['data']['permSalt']
        #Basically, turn your plaintext pass into the shadow-crypted pass,
        #then crypt that with the temp salt.

        passcode = crypt(password, "$" + str(mode) + "$" + ps)
        passcode = passcode.split("$")[3]
        passcode = crypt(passcode, "$" + str(mode) + "$" + ts)
        passcode = passcode.split("$")[3]

        data = {"user": self.user, "password": passcode}
        try:
            resp = self.request("auth/login", "POST", data=data)
        except requests.exceptions.HTTPError:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")

        results = json.loads(resp.text)
        if not results['success']:
            raise beowebexc.BeowebAuthError(results['error'])
        return results

    def cloudauth_login(self, auth_url, key, secret):
        """Attempt to gain a session ID from beoweb using CloudAuth Tokens

        Requires the cloudauthclient library

        Use the user's CloudAuth API key and secret to get a token
        from the given CloudAuth server, then provide the system username
        and token to beoweb

        Returns beoweb results if no error is found. Beoweb sets the session
        ID in a cookie, so the session ID returned may not be needed depending
        on configuration

        :param auth_url: https URL for CloudAuth server
        :param key: API Key
        :param secret: API Secret
        :returns: Beoweb JSON data

        """

        try:
            from cloudauthclient.v1.client import Client
            from cloudauthclient import exceptions as authexc
        except ImportError as e:
            LOG.critical("Unable to import CloudAuth library")
            raise beowebexc.BeowebAuthError(
                "Unable to import CloudAuth library.")

        # Get token from cloudauth
        try:
            authclient = Client(auth_url, key, secret)
            authclient.authenticate()
        except authexc.AuthenticationError as e:
            raise beowebexc.BeowebAuthError(
                "Unable to get CloudAuth Token")

        # log in to beoweb with token
        LOG.debug("Successfully aquired token from cloudauth: %s",
                  authclient.token)
        data = {"beoweb_user": self.user,
                "auth_token": authclient.token}
        try:
            resp = self.request("cloud_auth/login", "POST", data=data)
        except requests.exceptions.HTTPError as e:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")

        results = json.loads(resp.text)

        if not results['success']:
            raise beowebexc.BeowebAuthError(results['error'])
        return results

    def sshkey_login(self, auth_host, auth_port):
        """Attempt to gain a session ID from beoweb using SSH public key

        Requires the paramiko library

        Connects to the given beoweb auth host/port and sends the system
        username and any found SSH public keys.

        Return the Session ID upon success -- this auth method will not
        result in beoweb setting the Session ID in a cookie, so the Session ID
        is automatically added to the param string of all subsequent reqeusts
        to Beoweb

        :param auth_host: hostname of SSH server to connect to
        :param auth_port: TCP port of SSH server to connect to
        :returns: new session ID from Beoweb

        """
        try:
            from paramiko import SSHClient, AutoAddPolicy
            from paramiko import AuthenticationException
        except ImportError:
            LOG.critical("Unable to import Paramiko library")
            raise beowebexc.BeowebAuthError(
                "Unable to import Paramiko library.")

        try:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            LOG.debug("SSH Auth connecting to %s:%s, user: %s",
                      auth_host, auth_port, self.user)
            client.connect(auth_host,
                           port=auth_port,
                           username=self.user)
            msg = client.get_transport().global_request("session_id",
                                                        wait=True)
            client.close()
            if msg:
                sid = msg.get_string()
                self.client.params.update({'session_id': sid})
            else:
                LOG.critical(("Authentication was successful, "
                              "but no session ID returned"))
                raise beowebexc.BeowebAuthError(
                    "Unable to get session ID from beoweb")
            return sid
        except AuthenticationException:
            raise beowebexc.BeowebAuthError(
                "SSH Key authentication failed")
        finally:
            try:
                client.close()
            except:
                pass

    def logout(self, session_id=None):
        """Logs out of beoweb, invalidating the session

        :param session_id: optional explicit session_id to, for use if
            session is not already in a cookie.

        """

        params = {}
        if session_id:
            params = {"session_id": session_id}
        try:
            self.request("auth/logout", "GET", params=params)
        except requests.exceptions.HTTPError as e:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")

    def delete_jobs(self, jobs):
        """Deletes each of the jobs found in jobs

        :param jobs: list of job ids to delete
        :returns: JSON data structure from Beoweb

        Example:

            >>> beoclient.delete_jobs(["123.pod"])

        """

        job_list = ",".join(jobs)
        data = {"job_ids": job_list}
        try:
            resp = self.request("scheduler/delete_job", "POST", data=data)
        except requests.exceptions.HTTPError as e:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")

        results = json.loads(resp.text)
        if results['success'] != "true":
            raise beowebexc.BeowebJobDeleteError(results['error'])

    def release_job(self, job):
        """Release scheduler hold on given job

        :param job: Job id to release
        :returns: JSON data structure from Beoweb

        Example:

            >>> beoclient.release_job("123.pod")

        """

        data = {"jobid": job, "pod_user": self.user}
        try:
            resp = self.request("pod/release", "POST", data=data)
        except requests.exceptions.HTTPError as e:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")

        results = json.loads(resp.text)
        if not results['success']:
            raise beowebexc.BeowebJobReleaseError(
                "" if "msg" not in results else results['msg'])

    def get_jobs(self, job_id=None, group=None):
        """Get job details from the scheduler

        :param job_id: optional job id to request single job status
        :param group: optional Unix group name to request all jobs from group
            members
        :returns: JSON data from Beoweb

        Example:
            >>> beoclient.get_jobs()
            >>> beoclient.get_jobs(job_id="123.pod")

        """

        data = {"pod_user": self.user}
        data.update({"jobid": "ALL" if not job_id else job_id})
        if group:
            data.update({"group": group})
        try:
            resp = self.request("pod/status", "POST", data=data)
        except requests.exceptions.HTTPError as e:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")

        results = json.loads(resp.text)
        if not results['success']:
            raise beowebexc.BeowebJobGetError(
                "" if "msg" not in results else results['msg'])

        return results

    def submit_job(self, jobscript,
                   scheduler=None, overwrite=True, hold=False,
                   **kwargs):
        """Submit a new job to the scheduler

        :param jobscript: dictionary of {name: fileobject}
        :param scheduler: scheduler to use. One of ["TRQ","SGE"].
            "TRQ" is default if not given
        :param overwrite: boolean flag to overwrite an existing script
        :param hold: boolean flag whether to submit job with a scheduler hold
        :returns: JSON data from Beoweb

        Example:

            >>> beoclient.submit_job({'test.sub':
                                      open('/root/test.sub', 'rb')})

        """

        data = {"pod_user": self.user,
                "scheduler": "TRQ" if not scheduler else scheduler}
        # Beoweb just looks for the presence of overwrite and hold, not value
        if overwrite:
            data.update({"overwrite": "True"})
        if hold:
            data.update({"hold": "True"})

        if "data" in kwargs:
            data.update(kwargs["data"])
        if "hash_algo" not in data:
            data.update({"hash_algo": "md5"})
        files = {'jobscript': jobscript.items()[0]}
        try:
            resp = self.request("pod/submit", "POST", data=data, files=files)
        except requests.exceptions.HTTPError as e:
            LOG.error("HTTP Error from beoweb: %s", e)
            raise beowebexc.BeowebAPIError(
                "HTTP Error received from Beoweb host")
        except beowebexc.BeowebSessionError:
            # rewind the file if we will be retrying after authentication
            files['jobscript'][1].seek(0)
            raise

        results = json.loads(resp.text)
        if not results['success']:
            raise beowebexc.BeowebJobSubmitError(
                "" if "msg" not in results else results['msg'])

        return results
