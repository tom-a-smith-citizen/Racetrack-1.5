# -*- coding: utf-8 -*-
"""
Created on Wed May 15 07:27:23 2024

@author: TOSmith
"""

import geojson
from geojson import Feature, Point, FeatureCollection

#my_point = geojson.Point((42.96047, -85.65618))
#dump = geojson.dumps(my_point, sort_keys=True)

men_race = Feature(geometry=Point((42.96047, -85.65618)),properties={"name": "men"})
women_race = Feature(geometry=Point((42.96047, -85.65618)))
feature_collection = FeatureCollection([men_race, women_race])
dump = geojson.dumps(feature_collection)