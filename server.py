#  coding: utf-8 
import socketserver
from pathlib import Path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        end = False
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # print ("Got request: %s\n" % self.data)
        

        self.data_lst = self.data.split(bytearray('\r\n','utf-8'))

        handle_dic = {}
        for val in self.data_lst:
            val = val.split(bytearray(': ','utf-8'))
            if len(val) == 1:
                handle_dic["Command"] = val[0]
            else:
                handle_dic[val[0].decode("utf-8")] = val[1]

        parse_cmnd = handle_dic["Command"].split()

        if (parse_cmnd[0] == bytearray('GET','utf-8')):
            page = ""
            if parse_cmnd != []:
                page = parse_cmnd[1].decode("utf-8")
                if page == "/":
                    page = "/index.html"
                elif page.endswith("/"):
                    print (page)
                    check_dir = Path('www'+page)
                    # check_dir = page[page[:-1].rfind('/'):].strip("/")
                    if check_dir.is_dir():
                        page += "index.html"
                    else:
                        print("here")
                        to_send = 'HTTP/1.1 404 Not Found\r\n\r\n<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')
                        self.request.sendall(to_send)
                        end = True

            if not end:
                myfile = 'www' + page
                myfile2 = 'www' + page +'/index.html'
                my_path = Path(myfile)
                my_path2 = Path(myfile2)
                file_to_display = page + '/'

                if my_path.is_file():
                    
                    html_css = True
                    if page.endswith(".html"):
                        mimetype = 'text/html'
                    elif page.endswith(".css"):
                        mimetype = 'text/css'
                    else:
                        html_css = False
                        to_send = 'HTTP/1.1 404 Not HTML or CSS\r\n\r\n'.encode('utf-8')
                        self.request.sendall(to_send)
                        
                    if html_css:
                        file = open(myfile,'rb')
                        response = file.read()
                        file.close()

                        header = "HTTP/1.1 200 OK\r\n"
                        header += 'Content-Type: '+str(mimetype)+'\r\n\r\n'

                        final_response = header.encode('utf-8')
                        final_response += response
                        self.request.sendall(final_response)
                else:
                    if my_path2.is_file():
                        to_send = ('HTTP/1.1 301 Permanently moved to {}\r\n\r\n<html><body><center><h3>Error 301 Permanently moved to {}</h3><p>Python HTTP Server</p></center></body></html>'.format(file_to_display, file_to_display)).encode('utf-8')
                    else:
                        to_send = 'HTTP/1.1 404 Not Found\r\n\r\n<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')
                    self.request.sendall(to_send)
        else:
            to_send = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'.encode('utf-8')
            self.request.sendall(to_send)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        # Create the server, binding to localhost on port 8080
        server = socketserver.TCPServer((HOST, PORT), MyWebServer)
        print ('Started httpserver on port ', PORT)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

    except KeyboardInterrupt:
        print ('\n^C received, shutting down the web server')
        server.socket.close()
