#!/usr/bin/python
# eMonitor rewritten using tkinter and Pillow
# Version 1

# BEGIN SETUP

# HTTP Server
port = 8080  # Port of HTTP server (http://127.0.0.1:8080/)

# Capture region
l, t = (10, 120)  # Left and top offsets from primary monitor
root_window_width, h = (701, 595)  # Width and height of capture region

# Screenshot coordinates
ssX = l
ssY = t
ssWidth = root_window_width
ssHeight = h

fn = 'shot.png'  # File name of screenshot

# END SETUP

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from PIL import ImageGrab
import threading
import tkinter as tk

def capture_screenshot():
    # Define the bounding box coordinates
    bbox = (ssX, ssY, ssX + ssWidth, ssY + ssHeight)
    # Capture the screenshot
    screenshot = ImageGrab.grab(bbox)
    # Rotate the image if needed (e.g., 90 degrees)
    # screenshot = screenshot.rotate(90, expand=True)
    # Save the screenshot
    screenshot.save(fn)

class Serv(BaseHTTPRequestHandler):

    def deliver_site(self):
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        reload_function = '''
        function() {
            document.getElementById("pic").src = "''' + fn + '''?" + (new Date()).getTime();
        }
        '''

        website = '''
        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>eMonitor</title>
        </head>
        <body style="margin:0px;">
        <img id="pic" src="''' + fn + '''" onclick="''' + reload_function + '''">
        <script type="text/javascript">
        // Reload the image when clicked
        document.getElementById("pic").onclick = ''' + reload_function + ''';
        </script>
        </body>
        </html>
        '''

        website_bytes = website.encode("utf-8")
        self.wfile.write(website_bytes)

    def do_GET(self):
        self.send_response(200)
        if self.path.startswith('/' + fn):  # Check if the request is for the image
            print("Delivering image")
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            capture_screenshot()

            with open(fn, 'rb') as f:
                self.wfile.write(f.read())

        else:
            self.deliver_site()

def main():
    try:
        print('eMonitor by Kranu (rewritten with tkinter and Pillow)')

        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Connect to an external server to get the local IP address
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()

        print('Starting HTTP server...')
        server = HTTPServer(('', port), Serv)
        print('Press Ctrl+C to stop')
        print("")
        print('On your device, visit http://' + local_ip + ':' + str(port) + '/')

        # Take initial screenshot
        capture_screenshot()

        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping...')
        server.socket.close()

if __name__ == "__main__":
    main()
