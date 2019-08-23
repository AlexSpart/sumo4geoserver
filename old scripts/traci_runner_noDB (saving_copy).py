#!/usr/bin/env python

import os
import sys
import optparse
import subprocess
import json
import requests

os.environ["SUMO_HOME"] = "/home/alex/Desktop/sumo"

#try:
#    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', "tools")) # tutorial in tests
#    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(os.path.dirname(__file__), "..", "..", "..")), "tools")) # tutorial in docs
#    from sumolib import checkBinary
#except ImportError:
#    sys.exit("please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

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




#    while traci.simulation.getMinExpectedNumber() > 0:
#        for veh_id in traci.vehicle.getIDList():
#            speed = traci.vehicle.getSpeed(veh_id)
#            position = traci.vehicle.getPosition(veh_id)
##            print(veh_id,position,speed)
#            with open("sim_results.txt", "a+") as myfile:
#                json_simresults = json.dumps([veh_id, position, speed])
#                print(json_simresults, file=myfile)
##       THE SAME AS ABOVE BUT WITH SUBSCRIPTIONS
#        for veh_id in traci.simulation.getDepartedIDList():
#            vehicles_array.append(veh_id)
##           CHOOSE FROM TRACI.CONSTANTS ATTRIBUTES WHAT WE WANT TO DISPLAY
##           traci.vehicle.subscribe(veh_id, [traci.constants.VAR_POSITIONS])
##            traci.vehicle.subscribe(vehicles_array[0], [traci.constants.VAR_POSITION]) # cant choose the second vehicle cause it hasnt departed yet. So the onyl solution is to subscribe for all the departed so far or just the first cause it instantly departs
##            traci.vehicle.subscribe(vehicles_array[0], [traci.constants.VAR_SPEED])
#            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_POSITION]) # cant choose the second vehicle cause it hasnt departed yet. So the onyl solution is to subscribe for all the departed so far or just the first cause it instantly departs
#            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_SPEED])
#        infos = traci.vehicle.getAllSubscriptionResults()
#        with open("mobility_infos.txt", "a") as f:
#            json_infos = json.dumps(infos)  # use `json.loads` to do the reverse
#            print(json_infos, file=f)
#
#        traci.simulationStep()
##        print(step)
#
#        step += 1
#
#    traci.close()
#    sys.stdout.flush()

    while traci.simulation.getMinExpectedNumber() > 0:
        for veh_id in traci.simulation.getDepartedIDList():
#            vehicles_array = []
            vehicles_array.append(veh_id)  # creating an array with the cars that have departed and so are running in the simulation
            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_POSITION]) # cant choose the second vehicle cause it hasnt departed yet. So the only solution is to subscribe for all the departed so far or just the first cause it instantly departs
            traci.vehicle.subscribe(veh_id, [traci.constants.VAR_SPEED])
        for veh_id in traci.simulation.getArrivedIDList():
            if veh_id in vehicles_array:
                vehicles_array.remove(veh_id) # deleting the cars that have arrived to the destination. We need an apdated array otherwize  it will crash
        for car in vehicles_array:
            current_position = traci.vehicle.getPosition(car)
            current_speed = traci.vehicle.getSpeed(car)
#           print(current_position,current_speed)
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

