#!/usr/bin/env python

import os
import sys
import optparse
import subprocess
import json
import socket

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
    my_data = {}
#    CLEAR THE FILE FROM PREVIOUS INPUTS
    open("mobility_infos.txt", "w").close()
    open("mobility_data.txt", "w").close()

    while traci.simulation.getMinExpectedNumber() > 0:
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dynamic vehicles_array list ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for veh_id in traci.simulation.getDepartedIDList():
            vehicles_array.append(veh_id)  # creating an array with the cars that have departed and so are running in the simulation
            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_POSITION]) # cant choose the second vehicle cause it hasnt departed yet. So the only solution is to subscribe for all the departed so far or just the first cause it instantly departs
            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_SPEED])
        for veh_id in traci.simulation.getArrivedIDList():
            if veh_id in vehicles_array:
                vehicles_array.remove(veh_id) # deleting the cars that have arrived to the destination. We need an apdated array otherwize  it will crash
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            

        if vehicles_array:
            time = traci.simulation.getTime()
            carID = vehicles_array[0]
            laneID = traci.vehicle.getLaneID(carID)
            laneINDEX = traci.vehicle.getLaneIndex(carID)
            vehicle_class = traci.vehicle.getVehicleClass(carID)
            current_position = traci.vehicle.getPosition(carID)
            current_speed = traci.vehicle.getSpeed(carID)
            current_acceleration = traci.vehicle.getAcceleration(carID)
            current_angle = traci.vehicle.getAngle(carID)
            #print(time,carID,vehicle_class,current_position,current_speed,current_acceleration,laneID)
        
            mydata = {
                    "time": time,
                    "carID": carID,
                    "Vclass": vehicle_class,
                    "position": current_position,
                    "speed": current_speed,
                    "acceleration": current_acceleration,
                    "angle": current_angle,
                    "laneID": laneID
                    }
            data_json = json.dumps({step:mydata})
            
           # print("Connecting...")
            server_address = "/tmp/python_unix_sockets_example"
            print('connecting to {}'.format(server_address))
            print('Sending data for STEP: {}'.format(step))

            if os.path.exists("/tmp/python_unix_sockets_example"):
                client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                client.connect("/tmp/python_unix_sockets_example")
            client.send(data_json)
            
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

