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

import logging

import requests

from beowebclient.common import exceptions as beowebexc

LOG = logging.getLogger(__name__)


class HTTPClient(object):
    """Client to handle HTTP traffic to Beoweb"""

    USER_AGENT = "python-beoweb-client"

    def __init__(self, user, beoweb_host, ssl=True, port=None):
        self.client = requests.Session()
        self.client.headers.update({'User-Agent': "python-beowebclient"})
        self.user = user
        self.endpoint = "%s://%s" % ("https" if ssl else "http", beoweb_host)
        if port is not None:
            self.endpoint += ":%s" % port

    def request(self, url, method, **kwargs):
        """Send HTTP request to endpoint"""

        fullurl = "%s/%s" % (self.endpoint, url)
        try:
            if kwargs.get('debug', False):
                for param in kwargs:
                    LOG.debug("DEBUG %s, %s=%s", method, param, kwargs[param])
                del kwargs['debug']
            resp = self.client.request(method, fullurl, verify=False, **kwargs)
        except requests.exceptions.ConnectionError:
            LOG.error("Unable to connect to %s", self.endpoint, exc_info=True)
            raise beowebexc.BeowebConnectError(
                "Unable to connect to Beoweb host")
        if resp.status_code != requests.codes.ok:
            if resp.status_code == requests.codes.unauthorized:
                raise beowebexc.BeowebSessionError(
                    "Invalid Session ID")
            else:
                resp.raise_for_status()
        return resp

    def close(self):
        """finalize any connections with Beoweb"""
        self.client.close()
