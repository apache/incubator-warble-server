#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
 #the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the CLI testing script for Apache Warble (incubating)
"""
_VERSION = '0.1.0'

# Basic imports
import os
import sys
import stat
import time
import ruamel.yaml
import requests
import datetime
import argparse
import socket
import base64

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description = "Run-time configuration options for Apache Warble (incubating)")
    parser.add_argument('--version', action = 'store_true', help = 'Print node version and exit')
    parser.add_argument('--test', action = 'store_true', help = 'Run debug unit tests')
    parser.add_argument('--wait', action = 'store_true', help = 'Wait for node to be fully registered on server before continuing')
    parser.add_argument('--config', type = str, help = 'Load a specific configuration file')
    args = parser.parse_args()
    
    user = input("Enter super user name: ").strip()
    pw = input("Enter super user password: ").strip()
    
    rv = requests.put('http://localhost:8000/api/session', json = {
        'username': user,
        'password': pw
    })
    if rv.status_code == 200:
        print("Logged in successfully!")
        cookie = rv.headers['set-cookie']
        
        while True:
            cmd = input("?> ").strip()
            if cmd == 'exit':
                print("bye bye!")
                sys.exit(0)
            if cmd == 'nodes':
                rv = requests.get('http://localhost:8000/api/node/list',  headers = {
                    'Cookie': cookie
                    })
                nodes = rv.json()['nodes']
                
                print("Nodes in registry:")
                print("[ id ]  [          hostname        ]  [ enabled ]  [ verified ]  [        fingerprint         ]")
                for node in nodes:
                    print("  %3u    %-28s     %s            %s          %s" %  (node['id'], node['hostname'][:27], node['enabled'] and '✓' or 'x', node['verified'] and '✓' or 'x', node['fingerprint'][:28]))
                
            if 'unverify' in cmd:
                nodeid = int(cmd.replace('unverify ', ''))
                print("Unverifying node no. %u" % nodeid)
                rv = requests.post('http://localhost:8000/api/node/modify',  headers = {
                    'Cookie': cookie
                    },
                    json = {
                        'id': nodeid,
                        'verified': False
                    }
                    )
                if rv.status_code == 200:
                    print("Node successfully unverified!")
                else:
                    print(rv.text)
            elif 'verify' in cmd:
                nodeid = int(cmd.replace('verify ', ''))
                print("Verifying node no. %u" % nodeid)
                rv = requests.post('http://localhost:8000/api/node/modify',  headers = {
                    'Cookie': cookie
                    },
                    json = {
                        'id': nodeid,
                        'verified': True
                    }
                    )
                if rv.status_code == 200:
                    print("Node successfully verified!")
                else:
                    print(rv.text)
            
            if 'enable' in cmd:
                nodeid = int(cmd.replace('enable ', ''))
                print("Enabling node no. %u" % nodeid)
                rv = requests.post('http://localhost:8000/api/node/modify',  headers = {
                    'Cookie': cookie
                    },
                    json = {
                        'id': nodeid,
                        'enabled': True
                    }
                    )
                if rv.status_code == 200:
                    print("Node successfully enabled!")
                else:
                    print(rv.text)
            
            if 'disable' in cmd:
                nodeid = int(cmd.replace('disable ', ''))
                print("Disabling node no. %u" % nodeid)
                rv = requests.post('http://localhost:8000/api/node/modify',  headers = {
                    'Cookie': cookie
                    },
                    json = {
                        'id': nodeid,
                        'enabled': False
                    }
                    )
                if rv.status_code == 200:
                    print("Node successfully disabled!")
                else:
                    print(rv.text)
    else:
        print("log in failed!")