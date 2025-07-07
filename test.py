# -*- coding: utf-8 -*-
"""
Created on Wed May  8 07:42:32 2024

@author: TOSmith
"""

import threading
import socket
import os
from flask import Flask, send_file

class ServerThread(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def run(self):
        app = Flask(__name__)

        @app.route('/test', methods=['GET'])
        def test():
            return "Hello, world!"
        
        @app.route('/livetest:', methods=['GET'])
        def livetrackload():
            return send_file(f"{os.getcwd()}\\menLiveTrackLoad.kml")
        app.run(host=self.host, port=self.port, debug=True, use_reloader=False)
        
        

def get_private_ip():
    ip = socket.gethostbyname(socket.gethostname())
    return ip

if __name__ == "__main__":
    private_ip = get_private_ip()
    test_server = ServerThread(private_ip, 8080)
    test_server.start()