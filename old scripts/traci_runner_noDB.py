#!/usr/bin/env python

import os
import sys
import optparse
import subprocess
import json
import requests

os.environ["SUMO_HOME"] = "/home/alex/Desktop/sumo"


# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
     tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
     sys.path.append(tools)
    # tools = os.path.join(os.environ['HOME'], 'Desktop', 'sumo', 'tools')
    # sys.path.append(tools)
    # print(tools)

else:
    
      sys.exit("please declare environment variable 'SUMO_HOME'")
    
#     sys.path.append(os.path.join(os.path.dirname(__file__), "/Users/alex/Desktop/sumo/tools"))
     # print(sys.path)
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci

PORT = 9999




# contains TraCI control loop
def run():
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0
    vehicles_array = []
#    CLEAR THE FILE FROM PREVIOUS INPUTS
    open("mobility_infos.txt", "w").close()
    open("mobility_data.txt", "w").close()


    while traci.simulation.getMinExpectedNumber() > 0:
        for veh_id in traci.simulation.getDepartedIDList():
#            vehicles_array = []
            vehicles_array.append(veh_id)  # creating an array with the cars that have departed and so are running in the simulation
            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_POSITION]) # cant choose the second vehicle cause it hasnt departed yet. So the only solution is to subscribe for all the departed so far or just the first cause it instantly departs
            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_SPEED])
        for veh_id in traci.simulation.getArrivedIDList():
            if veh_id in vehicles_array:
                vehicles_array.remove(veh_id) # deleting the cars that have arrived to the destination. We need an apdated array otherwize  it will crash
        for car in vehicles_array:     #uncomment to retrieve the values of all vehicles in the simulation
	    time = traci.simulation.getTime()
	    laneID = traci.vehicle.getLaneID(car)
	    laneINDEX = traci.vehicle.getLaneIndex(car)
	    vehicle_class = traci.vehicle.getVehicleClass(car)
            current_position = traci.vehicle.getPosition(car)
            current_speed = traci.vehicle.getSpeed(car)
	    current_acceleration = traci.vehicle.getAcceleration(car)
            print(time)
            data = {
                    "step": step,
                    "ID": car,
                    "position": current_position,
                    "speed": current_speed
                    }
            data_json = json.dumps(data)
#            payload = {'json_payload': data_json, 'apikey': 'YOUR_API_KEY_HERE'}
#            r = requests.get('http://myserver/emoncms2/api/post', data=payload)

            with open("mobility_data.txt", "a") as output_file:
                # print(data_json, file=output_file) #python 3.x
                print >>output_file, data_json         #python 2.7


        infos = traci.vehicle.getAllSubscriptionResults()
        with open("mobility_infos.txt", "a") as f:
            json_infos = json.dumps(infos)  # use `json.loads` to do the reverse
#            print(json_infos, file=f)
            print >>f, json_infos         #python 2.7

        traci.simulationStep()
        step += 1
    traci.close()
    sys.stdout.flush()




def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true", default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
#    traci.start([sumoBinary, "-c", "scenario/map.sumocfg",
#                             "--tripinfo-output", "tripinfo.xml"])

#   this is the normal way of using traci. sumo is started as a
#   subprocess and then the python script connects and runs
    sumoProcess = subprocess.Popen([sumoBinary, "-c", "scenario/map.sumocfg", "--tripinfo-output", "tripinfo.xml"], stdout=sys.stdout, stderr=sys.stderr)
    run()
    sumoProcess.wait()

