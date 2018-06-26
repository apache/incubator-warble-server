#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the session library for Apache Warble.
It handles setting/getting cookies and user prefs
"""


# Main imports
import cgi
import re
import sys
import traceback
import http.cookies
import uuid
import time
import plugins.registry

class WarbleSession(object):

    def logout(self):
        """Log out user and wipe cookie"""
        if self.user and self.cookie:
            cookies = http.cookies.SimpleCookie()
            cookies['warble_session'] = "null"
            self.headers.append(('Set-Cookie', cookies['warble_session'].OutputString()))
            try:
                if self.DB.dbtype == 'sqlite':
                    c = self.DB.sqlite.open('sessions.db')
                    cur = c.cursor()
                    cur.execute("DELETE FROM `sessions` WHERE `cookie` = ? LIMIT 1", (self.cookie,))
                    c.commit()
                    c.close()
                elif self.DB.dbtype == 'elasticsearch':
                    self.DB.ES.delete(index=self.DB.dbname, doc_type='uisession', id = self.cookie)
                    
                self.cookie = None
                self.user = None
            except:
                pass
    def newCookie(self):
        cookie = uuid.uuid4()
        cookies = http.cookies.SimpleCookie()
        cookies['warble_session'] = cookie
        cookies['warble_session']['expires'] = 86400 * 365 # Expire one year from now
        self.headers.append(('Set-Cookie', cookies['warble_session'].OutputString()))
        return str(cookie)
        
    def __init__(self, DB, environ, config):
        """
        Loads the current user session or initiates a new session if
        none was found.
        """
        self.config = config
        self.user = None
        self.client = None
        self.DB = DB
        self.headers = [('Content-Type', 'application/json')]
        self.cookie = None

        # Construct the URL we're visiting
        self.url = "%s://%s" % (environ['wsgi.url_scheme'], environ.get('HTTP_HOST', environ.get('SERVER_NAME')))
        self.url += environ.get('SCRIPT_NAME', '/')

        # Get Warble cookie
        cookie = None
        cookies = None
        
        if 'HTTP_COOKIE' in environ:
            cookies = http.cookies.SimpleCookie(environ['HTTP_COOKIE'])
        if cookies and 'warble_session' in cookies:
            cookie = cookies['warble_session'].value
            try:
                if re.match(r"^[-a-f0-9]+$", cookie): # Validate cookie, must follow UUID4 specs
                    doc = None
                    if self.DB.dbtype == 'sqlite':
                        session_conn = self.DB.sqlite.open('sessions.db')
                        account_conn = self.DB.sqlite.open('accounts.db')
                        sc = session_conn.cursor()
                        ac = account_conn.cursor()
                        sc.execute("SELECT * FROM `sessions` WHERE `cookie` = ?", (cookie,))
                        sdoc = sc.fetchone()
                        if sdoc:
                            userid = sdoc['userid']
                            if userid:
                                ac.execute("SELECT * FROM `accounts` WHERE `userid` = ?", (userid,))
                                doc = ac.fetchone()
                        if doc:
                            # Make sure this cookie has been used in the past 7 days, else nullify it.
                            # Further more, run an update of the session if >1 hour ago since last update.
                            age = time.time() - sdoc['timestamp']
                            if age > (7*86400):
                                sc.execute("DELETE FROM `sessions` WHERE `cookie` = ? LIMIT 1", (self.cookie,))
                                sdoc = None # Wipe it!
                                doc = None
                            elif age > 3600:
                                st = int(time.time()) # Update timestamp in session DB
                                sc.execute("UPDATE `sessions` SET `timestamp` = ? WHERE `cookie` = ? LIMIT 1", (st, cookie,))
                            if doc:
                                self.user = {k:doc[k] for k in doc.keys()}
                                self.user['userlevel'] = 'superuser' if doc['superuser'] else 'normal'
                        session_conn.commit()
                        session_conn.close()
                        account_conn.close()

                    if self.DB.dbtype == 'elasticsearch':
                        sdoc = self.DB.ES.get(index=self.DB.dbname, doc_type='uisession', id = cookie)
                        if sdoc and 'cid' in sdoc['_source']:
                            doc = self.DB.ES.get(index=self.DB.dbname, doc_type='useraccount', id = sdoc['_source']['cid'])
                        if doc and '_source' in doc:
                            # Make sure this cookie has been used in the past 7 days, else nullify it.
                            # Further more, run an update of the session if >1 hour ago since last update.
                            age = time.time() - sdoc['_source']['timestamp']
                            if age > (7*86400):
                                self.DB.ES.delete(index=self.DB.dbname, doc_type='uisession', id = cookie)
                                sdoc['_source'] = None # Wipe it!
                                doc = None
                            elif age > 3600:
                                sdoc['_source']['timestamp'] = int(time.time()) # Update timestamp in session DB
                                self.DB.ES.update(index=self.DB.dbname, doc_type='uisession', id = cookie, body = {'doc':sdoc['_source']})
                            if doc:
                                self.user = doc['_source']
                else:
                    cookie = None
            except Exception as err:
                print(err)
        # Non-human (node/agent) API Key auth
        elif 'HTTP_APIKEY' in environ:
            cookie = environ['HTTP_APIKEY']
            if re.match(r"^[-a-f0-9]+$", cookie): # Validate cookie, must follow UUID4 specs
                try:
                    self.client = plugins.registry.node(self, cookie)
                except:
                    pass
        if not cookie:
            cookie = self.newCookie()
        self.cookie = cookie
