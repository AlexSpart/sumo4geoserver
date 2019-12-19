#!/bin/bash

# exit on error
set -e

export SUMO_HOME="/home/alex/Desktop/sumo"
export SUMO_BINS="$SUMO_HOME/bin"
export SUMO_TOOLS="$SUMO_HOME/tools"

ROOT="."
DATA="$ROOT/data"
SCRIPTS="$ROOT/scripts"
SCENARIO="$ROOT/scenario"

TAZ="$SCENARIO/taz"

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SCENARIO GENERATION - TOPOLOGY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

echo "Creating the network..."
$SUMO_BINS/netconvert -c $SCENARIO/map.netccfg
netconvert --osm-files $DATA/map.osm --lefthand --output.street-names -o $SCENARIO/map.net.xml
#polyconvert --xml-validation --net-file map.net.xml --osm-files map.osm --type-file typemap.xml -o map.poly.xml
echo "Extracting the polygons..."
$SUMO_BINS/polyconvert -c $SCENARIO/map.polycfg
#
#echo "Convert osm & net to Pickle..."
#python3 $SCRIPTS/xml2pickle.py -i $DATA/sophia.osm -o $SCENARIO/osm.pkl
#python3 $SCRIPTS/xml2pickle.py -i $SCENARIO/sophia.net.xml -o $SCENARIO/net.pkl
#
#echo "Creating Parking Lots..."
#python3 $SCRIPTS/parkings.osm2sumo.py --osm $SCENARIO/osm.pkl --net $SCENARIO/net.pkl -o $SCENARIO/sophia.
#
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SCENARIO GENERATION - TAZ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
#
### Create poly file for TAZ and save it as $TAZ/sophia.complete.poly.xml
### $SUMO_BINS/netedit -s $SCENARIO/sophia.net.xml
### Convert by hand the poly file to a taz file called $TAZ/sophia.shape.taz.xml
### Fill the taz file using the script
#python $SUMO_TOOLS/edgesInDistricts.py -n $SCENARIO/sophia.net.xml -t $TAZ/sophia.shape.taz.xml \
#    -o $TAZ/sophia.complete.taz.xml
#python3 $SCRIPTS/weigths_from_taz.py -i $TAZ/sophia.complete.taz.xml -o $TAZ/sophia.complete.taz.weight.csv
#
#echo "Filtering the TAZs: pedestrians..."
#python $SUMO_TOOLS/district/filterDistricts.py -n $SCENARIO/sophia.net.xml \
#    -t $TAZ/sophia.complete.taz.xml --vclass=pedestrian -o $TAZ/sophia.pedestrian.taz.xml
##echo "Filtering the TAZs: bicycles..."
##python $SUMO_TOOLS/district/filterDistricts.py -n $SCENARIO/sophia.net.xml \
##    -t $TAZ/sophia.complete.taz.xml --vclass=bicycle -o $TAZ/sophia.bicycle.taz.xml
#echo "Filtering the TAZs: 2wheelers..."
#python $SUMO_TOOLS/district/filterDistricts.py -n $SCENARIO/sophia.net.xml \
#    -t $TAZ/sophia.complete.taz.xml --vclass=motorcycle -o $TAZ/sophia.2wheeler.taz.xml
#echo "Filtering the TAZs: passengers..."
#python $SUMO_TOOLS/district/filterDistricts.py -n $SCENARIO/sophia.net.xml \
#    -t $TAZ/sophia.complete.taz.xml --vclass=passenger -o $TAZ/sophia.passenger.taz.xml
#
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SCENARIO GENERATION - PUBLIC TRANSPORTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
#
#echo "Generate PT trips..."
#python $SUMO_TOOLS/ptlines2flows.py -n $SCENARIO/sophia.net.xml -b 0 -e 43200 -p 600 \
#    --random-begin --seed 42 --no-vtypes \
#    --ptstops $SCENARIO/sophia.ptstops.add.xml --ptlines $SCENARIO/sophia.ptlines.xml \
#    -o $SCENARIO/sophia.pt.flows.xml
#
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SCENARIO GENERATION - ACTIVITY GENERATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
#
#echo "Generating symplified activity-based mobility..."
#python3 $SCRIPTS/mobilitygen.trips.py -c $SCENARIO/mobilitygen.trips.json
#
#echo "Fix the routes from the activity-based generated trips for all vTypes..."
#$SUMO_BINS/duarouter -c $SCENARIO/routes.person.duacfg  --output-file $SCENARIO/sophia.dua.pedestrian.rou.xml
#
##$SUMO_BINS/duarouter -c $SCENARIO/routes.vehicle.duacfg --route-files $SCENARIO/sophia.bicycle.trips.xml \
##    --output-file $SCENARIO/sophia.dua.bicycle.rou.xml
#$SUMO_BINS/duarouter -c $SCENARIO/routes.vehicle.duacfg --route-files $SCENARIO/sophia.2wheeler.trips.xml \
#    --output-file $SCENARIO/sophia.dua.2wheeler.rou.xml
#
#$SUMO_BINS/duarouter -c $SCENARIO/routes.vehicle.duacfg --route-files $SCENARIO/sophia.passenger.trips.xml \
#    --output-file $SCENARIO/sophia.dua.passenger.rou.xml
##$SUMO_BINS/duarouter -c $SCENARIO/routes.vehicle.duacfg --route-files $SCENARIO/sophia.evehicle.trips.xml \
##    --output-file $SCENARIO/sophia.dua.evehicle.rou.xml
##$SUMO_BINS/duarouter -c $SCENARIO/routes.vehicle.duacfg --route-files $SCENARIO/sophia.other.trips.xml \
##    --output-file $SCENARIO/sophia.dua.other.rou.xml
#
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GENERATING RANDOM TRIPS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
#python $SUMO_TOOLS/randomtrips.py -n $SCENARIO/map.net.xml -e 100 -l
#python $SUMO_TOOLS/randomtrips.py -n $SCENARIO/map.net.xml -r $SCENARIO/map.rou.xml e 100 -l
#python $SUMO_TOOLS/randomtrips.py -n $SCENARIO/map.net.xml -e 10000 -o $SCENARIO/map.rou.xml
#python $SUMO_TOOLS/randomtrips.py -n $SCENARIO/map.net.xml -r map.rou.xml e 100 -l
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SUMO SIMULATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
#
#echo "Running SUMO..."
#$SUMO_BINS/sumo-gui -c $SCENARIO/map.sumocfg
