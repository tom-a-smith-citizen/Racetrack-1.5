# -*- coding: utf-8 -*-
"""
Racetrack 1.5
Created on Tue May  7 08:08:42 2024

@author: TOSmith
"""

import wx, requests, json, socket, threading, pynmea2, os, random, ftplib
from flask import Flask, render_template, send_file

class ui(wx.Frame):
    def __init__(self):
        super().__init__(parent=None,title="Racetrack")
        '''Initialize requried variables.'''
        self.title = "Racetrack 2.0"
        self.SetTitle(self.title)
        self.tracking_men = False
        self.tracking_women = False
        self.private_ip = self.get_private_ip()
        self.public_ip = self.get_public_ip()
        self.internal_server = server(self.private_ip, 8080)
        self.internal_server.start()
        
        '''Initialize UI'''
        self.panel_main = wx.Panel(self)
        self.sizer_main = wx.FlexGridSizer(6,2,10,10)
        
        '''Widgets'''
        self.label_public_ip = wx.StaticText(self.panel_main,label="Public IP:")
        self.label_ip_address = wx.StaticText(self.panel_main, label=self.public_ip)
        self.label_men_udp = wx.StaticText(self.panel_main, label="Men's udp Port:")
        self.field_men_udp = wx.TextCtrl(self.panel_main)
        self.field_men_udp.SetValue("9091")
        self.label_women_udp = wx.StaticText(self.panel_main, label="Women's udp Port:")
        self.field_women_udp = wx.TextCtrl(self.panel_main)
        self.field_women_udp.SetValue("32400")
        self.label_location_men = wx.StaticText(self.panel_main, label="Men's Location:")
        self.label_cords_men = wx.StaticText(self.panel_main, label="")
        self.label_location_women = wx.StaticText(self.panel_main, label="Women's Location:")
        self.label_cords_women = wx.StaticText(self.panel_main, label="")
        self.button_start_stop = wx.Button(self.panel_main, label="Start")
        self.button_start_stop.Bind(wx.EVT_BUTTON, self.start_stop)
        
        '''Building the trackers'''
        self.trackers = [tracker(self, "men", self.private_ip, int(self.field_men_udp.GetValue())),
                         tracker(self,"women",self.private_ip,int(self.field_women_udp.GetValue()))]
        
        '''Filling Sizers'''
        self.sizer_main.AddMany([(self.label_public_ip, 1, wx.ALL | wx.CENTER),
                                 (self.label_ip_address, 1, wx.ALL | wx.CENTER),
                                 (self.label_men_udp, 1, wx.ALL | wx.CENTER),
                                 (self.field_men_udp, 1, wx.ALL | wx.CENTER),
                                 (self.label_women_udp, 1, wx.ALL | wx.CENTER),
                                 (self.field_women_udp, 1, wx.ALL | wx.CENTER),
                                 (self.label_location_men, 1, wx.ALL | wx.CENTER),
                                 (self.label_cords_men, 1, wx.ALL | wx.CENTER),
                                 (self.label_location_women, 1, wx.ALL | wx.CENTER),
                                 (self.label_cords_women, 1, wx.ALL | wx.CENTER),
                                 (self.button_start_stop, 1, wx.ALL | wx.CENTER)])
        
        '''Launching UI'''
        self.panel_main.SetSizerAndFit(self.sizer_main)
        self.SetInitialSize(size=self.panel_main.GetEffectiveMinSize())
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Layout()
        self.Show()
    
    def on_close(self, event):
        for tracker in self.trackers:
            tracker.flag = False
        self.Destroy()
    
    def get_private_ip(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    
    def get_public_ip(self):
        try:
            r = requests.get("http://jsonip.com")
            if r.status_code == 200:
                j = json.loads(r.text)
                ip = j["ip"]
                return ip
            else:
                return ""
        except Exception as e:
            return e
        
    def start_stop(self, event):
        obj = event.GetEventObject()
        label = obj.GetLabel()
        if label == "Start":
            obj.SetLabel("Stop")
            self.tracking_men = True
            self.tracking_women = True
            for tracking in self.trackers:
                tracking.flag = True
                threading.Thread(target=tracking.track, daemon=True).start()
        elif label == "Stop":
            obj.SetLabel("Start")
            self.tracking_men = False
            self.tracking_women = False
            for tracking in self.trackers:
                tracking.flag = False
            self.label_cords_men.SetLabel("")
            self.label_cords_women.SetLabel("")
            
class tracker(object):
    def __init__(self, parent, race, ip, udp):
        self.parent = parent
        self.race = race
        self.ip = ip
        self.udp = udp
        self.flag = False
        self.label = getattr(self.parent, f'label_cords_{self.race}')
        self.kml = kml(self, "http://10.10.1.29:8080/")
        self.kml.generate_live_load()
        self.kml.generate_point()
        self.kml.generate_update_load()
        
    def track(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.parent.private_ip, self.udp))
        # Set a timeout for the socket
        self.sock.settimeout(1)  # Set a timeout of 1 second
        print(f"Listening for {self.race} GPS position at {self.parent.private_ip}:{self.udp}")
        while self.flag:
            try:
                self.data = self.sock.recvfrom(1024)
                if not self.data:
                    break
                try:
                    print(self.data)
                    location = self.decode(self.data[0])
                    self.label.SetLabel(f"{location[0]},{location[1]}")
                    self.kml.update(f"{location[0]}", f"{location[1]}")
                except pynmea2.ParseError as e:
                    print(e)
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Exception: {e}")
        # Close the socket outside the loop when flag is False
        self.sock.close()
        print("Socket closed")
        
        
    
    def stop(self):
        self.flag = False
        data = hasattr(self, "data")
        if data:
            self.sock.shutdown(1)
            self.sock.close()
    
    def decode(self, data):
        incoming = data.decode('latin-1)')
        print(incoming)
        #Builds an nmeaobj to parse data from that string
        nmeaobj = pynmea2.parse(incoming)
        #Converting from $GPGGA to more usable decimal notation
        lat = str(nmeaobj.latitude)
        long = str(nmeaobj.longitude)
        return (long, lat)

class kml(object):
    def __init__(self, parent, directory):
        self.parent = parent
        self.directory = directory
        
    def generate_live_load(self):
        output = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<NetworkLink>
<name>Loads {self.parent.race}.kml</name>
<Link>
<href>{self.directory}{self.parent.race}Point</href>
</Link>
</NetworkLink>
</kml>"""
        file = open(f"{self.parent.race}LiveTrackLoad.kml", "w")
        file.writelines(output)
        file.close()
        #self.upload(f'{self.parent.race}LiveTrackLoad.kml',f'{os.getcwd()}/{self.parent.race}LiveTrackLoad.kml')
        
    def generate_point(self):
        output = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <Placemark id="{self.parent.race}123">
  <Style>
  <IconStyle>
  <colorMode>normal</colorMode>
  <scale>3</scale>
  <heading>0</heading>
  <Icon><href>{self.directory}{self.parent.race}</href></Icon>
  </IconStyle>
  </Style>
    <Point>
      <coordinates>-85.71327426273638,42.92157781377413,0</coordinates>
    </Point>
  </Placemark>
</Document>
</kml>"""
        file = open(f"{self.parent.race}Point.kml", "w")
        file.writelines(output)
        file.close()
        #self.upload(f'{self.parent.race}Point.kml',f'{os.getcwd()}/{self.parent.race}Point.kml')
        
    def generate_update_load(self):
        output = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<NetworkLink>
  <name>Update</name>
  <Link>
    <href>{self.directory}{self.parent.race}Update</href></Link>
</NetworkLink>
</kml>"""
        file = open(f"{self.parent.race}UpdateLoad.kml", "w")
        file.writelines(output)
        file.close()
        #self.upload(f"{self.parent.race}UpdateLoad.kml", f"{os.getcwd()}/{self.parent.race}UpdateLoad.kml")
        
    def update(self, long, lat):
        output = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<NetworkLinkControl>
  <Update>
    <targetHref>{self.directory}{self.parent.race}Point</targetHref>
    <Change>
      <Placemark targetId="{self.parent.race}123">
        <Point>
        <coordinates>{long},{lat},0</coordinates>
        </Point>
      </Placemark>
    </Change>
  </Update>
</NetworkLinkControl>
</kml>"""
        file = open(f"{self.parent.race}Update.kml", "w")
        file.writelines(output)
        file.close()
        #self.upload(f"{self.parent.race}Update.kml",f"{os.getcwd()}/{self.parent.race}Update.kml")


    def upload(self, filename, filepath):
        try:
            ftp = ftplib.FTP('studiosrv.woodtv.net', 'studio', 'woodtv')
            ftp.cwd('/racetrack')
            file = open(f'{filepath}','rb')
            ftp.storbinary('STOR %s' % f'{filename}', file)     # send the file
            file.close()                                    # close file and FTP
            ftp.quit()
        except Exception as e:
            print(e)

class server(threading.Thread):
    def __init__(self, private_ip: str, port: int):
        super().__init__()
        self.private_ip = private_ip
        self.port = port
        self.daemon = True
        
    def run(self):
        app = Flask(__name__)

        @app.route('/test', methods=['GET'])
        def test():
            return "Racetrack server is active."
        
        @app.route('/menLiveTrackLoad', methods=['GET'])
        def menlivetrackload():
            return send_file(f"{os.getcwd()}\\menLiveTrackLoad.kml")
        
        @app.route('/womenLiveTrackLoad', methods=['GET'])
        def womenlivetrackload():
            return send_file(f"{os.getcwd()}\\womenLiveTrackLoad.kml")
        
        @app.route('/menPoint', methods=['GET'])
        def menpoint():
            return send_file(f"{os.getcwd()}\\menPoint.kml")
        
        @app.route('/womenPoint', methods=['GET'])
        def womenpoint():
            return send_file(f"{os.getcwd()}\\womenPoint.kml")
        
        @app.route('/menUpdateLoad', methods=['GET'])
        def menupdateload():
            return send_file(f"{os.getcwd()}\\menUpdateLoad.kml")
        
        @app.route('/womenUpdateLoad', methods=['GET'])
        def womenupdateload():
            return send_file(f"{os.getcwd()}\\womenUpdateLoad.kml")
        
        @app.route('/menUpdate', methods=['GET'])
        def menupdate():
            return send_file(f"{os.getcwd()}\\menUpdate.kml")
        
        @app.route('/womenUpdate', methods=['GET'])
        def womenupdate():
            return send_file(f"{os.getcwd()}\\womenUpdate.kml")
        
        @app.route('/men', methods=['GET'])
        def menpng():
            return send_file(f"{os.getcwd()}\\men.png")
        
        @app.route('/women', methods=['GET'])
        def womenpng():
            return send_file(f"{os.getcwd()}\\women.png")
        
        
        app.run(host=self.private_ip, port=self.port, debug=True, use_reloader=False)
        
def main():
    app=[]; app = wx.App(None)
    frame = ui()
    app.MainLoop()        

        
if __name__ == "__main__":
    main()