# SUMO4geoserver

SUMO4geoserver is a SUMO client to generate realistic vehicular traffic forwarding the traffic data to the EURECOM Geoserver through v2xmanager.


## Requirements
Install the [SUMO](https://github.com/eclipse/sumo) developement version from source.

Install this version of [v2xmanager](https://gitlab.eurecom.fr/a-team/geoserverbackend/tree/master/5gcroco/V2xManager) from source.

## Usage

#### Setup SUMO traffic scenario:

1) Download a map from [OpenStreetMap]((https://openstreetmap.org). Name it map.osm and save it in /data directory
 
2) Generate the scenario
```bash 
sh mapPrimer.sh
```
3) Create custom traffic in /scneario/map.rou.xml


#### Send CAM/DENM messages through SUMO client: 

1) Run v2xmanager as client in admin mode.
```bash 
sudo v2xmanager --interface=enp0s3 --gpsd-host=localhost --gpsd-port 2947 --cam-interval 6000 --client-port-number 446 --client-address 193.55.113.48 --server-port-number 3000 --client-role 1
```

 2) Run SUMO client in admin mode (use python 2.7)
```bash
sudo python cam_send.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)