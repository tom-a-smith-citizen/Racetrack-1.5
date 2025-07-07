# -*- coding: utf-8 -*-
"""
Plane Tracking Demo
Created on Wed May  8 09:00:15 2024

@author: TOSmith
"""

import requests, json, ftplib, os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class aircraft(object):
    def __init__(self, callsign):
        self.callsign = callsign
        self.tracking = False
        self.race = "airplane"
        self.kml = kml(self)
        self.kml.generate_live_load()
        self.kml.generate_point()
        self.kml.generate_update_load()
        self.session = requests.Session()
        self.retry = Retry(connect=3, backoff_factor=0.5)
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.session.mount('http://',self.adapter)
        self.session.mount('https://',self.adapter)
        
    def track(self):
        self.most_recent = {}
        while self.tracking:
            self.info = self.session.get(f"https://api.adsb.lol/v2/callsign/{self.callsign}")
            if self.info.status_code == 200:
                j = json.loads(self.info.text)
                try:
                    current = {"lat": str(j['ac'][0]['lat']),
                               "lon": str(j['ac'][0]['lon'])}
                except IndexError as e:
                    print(f"Index error: {e}")
                    break
                if current != self.most_recent:
                    self.most_recent = current
                    self.kml.update(current['lon'],current['lat'])
                    print(f"Lat: {self.most_recent['lat']}, Lon: {self.most_recent['lon']}", "\r")
            else:
                print("Couldn't connect.")
                break

class kml(object):
    def __init__(self, parent):
        self.parent = parent
        
    def generate_live_load(self):
        output = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<NetworkLink>
<name>Loads {self.parent.race}.kml</name>
<Link>
<href>http://studiosrv.woodtv.net/racetrack/{self.parent.race}Point.kml</href>
</Link>
</NetworkLink>
</kml>"""
        file = open(f"{self.parent.race}LiveTrackLoad.kml", "w")
        file.writelines(output)
        file.close()
        self.upload(f'{self.parent.race}LiveTrackLoad.kml',f'{os.getcwd()}/{self.parent.race}LiveTrackLoad.kml')
        
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
  <Icon><href>http://studiosrv.woodtv.net/racetrack/{self.parent.race}.png</href></Icon>
  </IconStyle>
  </Style>
    <Point>
      <coordinates>42.92157781377413, -85.71327426273638,0</coordinates>
    </Point>
  </Placemark>
</Document>
</kml>"""
        file = open(f"{self.parent.race}Point.kml", "w")
        file.writelines(output)
        file.close()
        self.upload(f'{self.parent.race}Point.kml',f'{os.getcwd()}/{self.parent.race}Point.kml')
        
    def generate_update_load(self):
        output = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<NetworkLink>
  <name>Update</name>
  <Link>
    <href>http://studiosrv.woodtv.net/racetrack/{self.parent.race}Update.kml</href></Link>
</NetworkLink>
</kml>"""
        file = open(f"{self.parent.race}UpdateLoad.kml", "w")
        file.writelines(output)
        file.close()
        self.upload(f"{self.parent.race}UpdateLoad.kml", f"{os.getcwd()}/{self.parent.race}UpdateLoad.kml")
        
    def update(self, long, lat):
        output = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<NetworkLinkControl>
  <Update>
    <targetHref>http://studiosrv.woodtv.net/racetrack/{self.parent.race}Point.kml</targetHref>
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
        self.upload(f"{self.parent.race}Update.kml",f"{os.getcwd()}/{self.parent.race}Update.kml")


    def upload(self, filename, filepath):
        ftp = ftplib.FTP('studiosrv.woodtv.net', 'studio', 'woodtv')
        ftp.cwd('/racetrack')
        file = open(f'{filepath}','rb')
        ftp.storbinary('STOR %s' % f'{filename}', file)     # send the file
        file.close()                                    # close file and FTP
        ftp.quit()            

if __name__ == "__main__":
    plane = aircraft("UAL2261")
    plane.tracking = True
    plane.track()
