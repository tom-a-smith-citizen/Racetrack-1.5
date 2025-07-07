# -*- coding: utf-8 -*-
"""
Created on Tue May 14 11:44:45 2024

@author: TOSmith
"""
import folium, os
from folium import plugins
from folium import JsCode
import requests, threading
from flask import Flask, render_template, send_file
from flask_cors import CORS
import geojson
from geojson import Feature, Point, FeatureCollection

class server(threading.Thread):
    def __init__(self, private_ip: str, port: int):
        super().__init__()
        self.private_ip = private_ip
        self.port = port
        self.daemon = True
        
    def run(self):
        app = Flask(__name__)
        CORS(app)

        @app.route('/test', methods=['GET'])
        def test():
            return "Racetrack server is active."
        
        @app.route('/livegeojson', methods=['GET'])
        def livegeojson():
            return send_file(f"{os.getcwd()}\\livegeojson.geojson")
        
        app.run(host=self.private_ip, port=self.port, debug=True, use_reloader=False)

class race(object):
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

class geojson_handler(object):
    def __init__(self, races: list):
        self.races = races
        
    def build_markers(self):
        pass
              
    def write_file(self):
        features = []
        for race in self.races:
            features.append(Feature(geometry=Point((race.lat, race.lon)),properties={"name": f"{race.name}"}))
        feature_collection = FeatureCollection(features)
        output = geojson.dumps(feature_collection)
        file = open("livegeojson.geojson", "w")
        file.writelines(output)
        file.close()

class tracker(threading.Thread):
    def __init__(self, active: bool):
        super().__init__()
        self.active = active
        
    def start(self):
        pass
            

internal_server = server("localhost", 8080)
internal_server.start()


# Create a Folium map
m = folium.Map(location=[42.96047, -85.65618], zoom_start=12)


m = folium.Map(location=[40.73, -73.94], zoom_start=12)
rt = folium.plugins.Realtime(
    "http://localhost:8080/livegeojson",
    get_feature_id=JsCode("(f) => { return f.properties.objectid; }"),
    interval=10000,
)
rt.add_to(m)

# Save the map to an HTML file
m.save('realtime_map.html')