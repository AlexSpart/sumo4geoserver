To setup the traffic scenario:
 1)Download a map from openstreetmap.org - name it map.osm - put it in /data directory
 2)Run mapPrimer.sh to generate the scenario
 3)Create custom traffic in /scneario/map.rou.xml


To send CAM/DENM messages through SUMO platform: 
 1)sudo v2xmanager --interface=enp0s3 --gpsd-host=localhost --gpsd-port 2947 --cam-interval 6000 --client-port-number 446 --client-address 193.55.113.48 --server-port-number 3000 --client-role 1
 2)sudo python cam_send.py  (python 2.7)

