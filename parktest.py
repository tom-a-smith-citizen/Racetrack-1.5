# -*- coding: utf-8 -*-
"""
Created on Mon May 13 09:47:25 2024

@author: TOSmith
"""

import requests, json
from datetime import datetime

class ride(object):
    def __init__(self, ident: int, land: str, name: str, is_open: bool, wait_time: int, last_updated: str):
        self.ident = ident
        self.land = land
        self.name = name
        self.is_open = is_open
        self.wait_time = wait_time
        self.last_updated = last_updated
        
    def __eq__(self, other):
        if (self.ident, self.land, self.name) == (other.ident, other.land, other.name):
            return True
        return False

class park(object):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.session = requests.session()
        self.tracking = True
        self.rides = []
        self.last_scrape = None
        
    def get_rides(self, data):
        if data.status_code == 200:
            data = json.loads(data.text)
            for lands in data['lands']:
                land = lands['name']
                for rides in lands['rides']:
                    setattr(self, f'{rides["id"]}', ride(rides['id'], land, rides['name'], rides['is_open'], rides['wait_time'], rides['last_updated']))
                    appendable = getattr(self, f'{rides["id"]}')
                    if appendable not in self.rides:
                        self.rides.append(ride(rides['id'], land, rides['name'], rides['is_open'], rides['wait_time'], rides['last_updated']))
                    else:
                        appendable.ident = rides['id']
                        appendable.land = land
                        appendable.name = rides['name']
                        appendable.is_open = rides['is_open']
                        appendable.wait_time = rides['wait_time']
                        appendable.last_updated = rides['last_updated']

    def pretty_print_rides(self):
        for ride in self.rides:
            if ride.is_open:
                status = "Open"
            else:
                status = "Closed"
            print(f"{ride.name}: {status} - {ride.wait_time} Minutes")
        
    def scrape_loop(self):
        self.last_scrape = self.session.get(self.url)
        while self.tracking:
            try:
                data = self.session.get("http://queue-times.com/parks/16/queue_times.json")
                if data != self.last_scrape:
                    self.last_scrape = data
                    self.get_rides(data)
                    self.pretty_print_rides()
            except Exception as e:
                print(e)
                break
                
                
                
                
        
        
        
if __name__ == "__main__":
    disneyland = park("Disneyland","http://queue-times.com/parks/16/queue_times.json")
    disneyland.scrape_loop()