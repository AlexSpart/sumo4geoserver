#!/usr/bin/env python

import os
import sys
import optparse
import subprocess
import json
import requests


mydata = {
    "step": "dummy_step",
    "ID": "dummy_car",
    "position": [2035.1401606271986, 1367.1587873743863],
    "speed": "dummy_speed"
    }

headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}

data_json = json.dumps({"mydata":mydata})
print(data_json)
resp = requests.post("https://geoserver.eurecom.fr/sumo", data = data_json, headers = headers)



if resp:
    print('Success!')
else:
    print('An error has occurred.')
