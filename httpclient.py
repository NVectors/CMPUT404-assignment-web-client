#!/usr/bin/env python3
# coding: utf-8

# Copyright 2023 Victor Nguyen, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Every line in the response/request ends with a \r\n
        # The start line or message line is always the first header
        # The status code is always after the HTTP method in the start line
        start_line = data.split("\r\n")[0]
        status = start_line.split(" ")[1]
        return int(status)

    def get_headers(self,data):
        # Every line in the response/request ends with a \r\n
        # There is also a bank line \r\n between the headers and the body
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        # Every line in the response/request ends with a \r\n
        # There is also a bank line \r\n between the headers and the body
        body = data.split("\r\n\r\n")[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # Read everything from the socket
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

    # Parse the given url to get host, port, path
    def check_parsed_url(self, parsed_url):
        # Check if port is specified in the url
        host = parsed_url.netloc
        if (":" in host):
            # Remove port from network location
            host = host.split(":")[0]

        # Set port to the default for HTTP
        port = parsed_url.port
        if (port is None):
            port = 80

        # Check if the path is specified in the url
        path = parsed_url.path
        if (path == ''):
            path="/"

        # Check if the path has parameters
        if parsed_url.query is not None:
            path += ('?' + parsed_url.query)

        return host, port, path

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)

        # Check for the "HTTP" in the url
        scheme = parsed_url.scheme
        if (scheme != "http"):
            # Return 404 Not Found
            return HTTPResponse(404, "")

        host,port,path = self.check_parsed_url(parsed_url)

        # Connect to socket
        self.connect(host,port)

        # Send a HTTP GET request to the web server
        request = ("GET {} HTTP/1.1\r\nHost: {}:{}\r\nConnection: close\r\n\r\n").format(path, host, port)
        self.sendall(request)

        # Get HTTP Response decoded as a string
        response = self.recvall(self.socket)

        # Parse string to get status code (as a int) and the message body
        code = self.get_code(response)
        body = self.get_body(response)

        # Close socket connection
        self.close()

        # As a user print result to sdout
        print(response)

        # As a developer return result
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)

        # Check for "HTTP" in the url
        scheme = parsed_url.scheme
        if (scheme != "http"):
            # Return 404 Not Found
            return HTTPResponse(404, "")

        host,port,path = self.check_parsed_url(parsed_url)

        # Connect to socket
        self.connect(host,port)

        # Check for HTTP Post argument
        if (args is not None):
            body = urllib.parse.urlencode(args)

            # SEND a HTTP POST request to the web server with message body
            content_type = "application/x-www-form-urlencoded"
            request = ("POST {} HTTP/1.1\r\nHost: {}:{}\r\n").format(path, host, port)
            request += ("Content-Type: {}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}\r\n").format(content_type, str(len(body)), body)
            self.sendall(request)
        else:
            # Send a HTTP GET request to the web server
            request = ("POST {} HTTP/1.1\r\nHost: {}:{}\r\n").format(path, host, port)
            request += ("Content-Length: 0\r\nConnection: close\r\n\r\n")
            self.sendall(request)

        # Get HTTP Response decoded as a string
        response = self.recvall(self.socket)

        # Parse string to get status code (as a int) and the message body
        code = self.get_code(response)
        body = self.get_body(response)

        # Close socket connection
        self.close()

        # As a user print result to sdout
        print(response)

        # As a developer return result
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
