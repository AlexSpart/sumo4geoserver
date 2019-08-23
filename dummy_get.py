#!/usr/bin/env python
#!/usr/bin/python3


import os
import sys
import optparse
import subprocess
import json
import requests

resp = requests.get("https://geoserver.eurecom.fr/sumodatabasedump")
print(resp.text)
#print(resp.json)
#print(resp.content)
#print(resp.status_code)
#print(resp.history)
#print(resp.url)

if resp:
    print('Success!')
else:
    print('An error has occurred.')




