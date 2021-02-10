#!/usr/bin/env python3
# coding: utf-8
# Copyright 2021 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Jialin Xie
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        self.parsed_url = urllib.parse.urlparse(url)
        host = self.parsed_url.hostname
        port = self.parsed_url.port

        if not port:
            if self.parsed_url.scheme == "http":
                port = 80
            else:
                port = 443

        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])
            

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]


    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def get_GET_request(self, host):
        request = ""
        http = "HTTP/1.1"
        path = self.parsed_url.path
        if not path:
            path = "/"
        request += "GET {} {}\r\n".format(path, http)
        request += "Host: {}\r\n".format(host)
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n"
        request += "\r\n"
        return request

    def GET(self, url, args=None):
        #print("url: ", url)
        host, port = self.get_host_port(url)
        request = self.get_GET_request(host)
        #print("request: ", request)
        self.connect(host, port)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        print("GET response:\n{}\nEnd of GET response\n".format(response))
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def get_POST_request(self, host, args):
        request = ""
        http = "HTTP/1.1"
        path = self.parsed_url.path
        if not path:
            path = "/"
        request += "POST {} {}\r\n".format(path, http)
        request += "Host: {}\r\n".format(host)
        request += "Accept: */*\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        content = ""
        if args:
            content = urllib.parse.urlencode(args)
        length = len(content)
        request += "Content-Length: {}\r\n".format(length)
        request += "Connection: close\r\n"
        request += "\r\n"
        if content:
            request += content
            request += "\r\n"

        return request

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        request = self.get_POST_request(host, args)

        self.connect(host, port)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        print("POST response:\n{}\nEnd of POST response\n".format(response))
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
