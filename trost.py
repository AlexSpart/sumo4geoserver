#!/usr/bin/env python

import os
import sys
import optparse
import subprocess
import json
import socket
import random
import math
from geopy.distance import geodesic

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
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Categorize vehicles according Vclass to separate lists ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        passenger_array = []
        bus_array = [] 
        truck_array = []
        list_of_random_items =[]
        for carID in vehicles_array:   
            if vehicles_array:  
                vehicle_class = traci.vehicle.getVehicleClass(carID)   
                if (vehicle_class) == "passenger":
                    passenger_array.append(carID);
                    #print("Inserted item in passenger_array");
                elif (vehicle_class) == "bus":
                    bus_array.append(carID);
                    #print("Inserted item in bus_array");
                elif (vehicle_class) == "truck":
                    truck_array.append(carID);
                    #print("Inserted item in truck_array");
                else : 
                    print("not available Vclass option");
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        #print(len(vehicles_array))
        #print(len(bus_array))
        #print(len(truck_array))
   
       
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
         # ***************************************************** Iterate through all types of vehicles in simulation **********************************************
        group_of_items = vehicles_array               
        if len(passenger_array) != 0:   # if vehicles of this class has been inserted in the simulation
           num_to_select = (len(passenger_array))*0.4      # pick a percentage of the vehicles inserted
           num_to_select = int(math.ceil(num_to_select))   # round it up to catch error 
           print("Picked {} out of {} vehicles" .format(num_to_select,len(passenger_array)))
           list_of_random_items = random.sample(group_of_items, num_to_select)
        else: 
           print("array is still zero. It means that vehicles have not yes inserted in the simulation")
        for ID in list_of_random_items: 
           #print (ID)
           if vehicles_array:
               time = traci.simulation.getTime()
               #carID = vehicles_array[0]
               laneID = traci.vehicle.getLaneID(carID)
               laneINDEX = traci.vehicle.getLaneIndex(carID)
               vehicle_class = traci.vehicle.getVehicleClass(carID)
               current_speed = traci.vehicle.getSpeed(carID)
               current_acceleration = traci.vehicle.getAcceleration(carID)
               current_angle = traci.vehicle.getAngle(carID)
               current_position = traci.vehicle.getPosition(carID)
               x, y = traci.vehicle.getPosition(carID)
               lon, lat = traci.simulation.convertGeo(x, y)
               #lon, lat = self.net.convertXY2LonLat(x, y)
               #print(time,carID,vehicle_class,current_position,current_speed,current_acceleration,laneID)
               #print(lon,lat)
               #print(lon)
               #print(lat)
       
               
               mydata = {
                       "time": time,
                       "carID": carID,
                       "Vclass": vehicle_class,
                       "speed": current_speed,
                       "acceleration": current_acceleration,
                       "angle": current_angle,
                       "laneID": laneID,
                       "longitude": lon,
                       "latitude": lat
                       }
               mydata = {
                       "_id":ID,
                       "Timestamp":time,
                       "StationID":"0x3364",
                       "StationType":"5",
                       "Latitude":lat,
                       "Longitude":lon,
                       "DetectionTime":time,
                       "ReferenceTime":time,
                       "eventType":"3",
                       "Vclass": vehicle_class,
                       "speed": current_speed,
                       "acceleration": current_acceleration,
                       "angle": current_angle,
                       "laneID": laneID
                       }
               data_json = json.dumps(mydata)
               print(data_json)
               #data_json = json.dumps({step:mydata})
               #data_json = json.dumps({"MYDATA":[mydata]})  #with tag MYDATA         

               # print("Connecting...")
               server_address = "/tmp/INVM_SAP"
               #server_address = "/tmp/python_unix_sockets_example"
               print('connecting to {}'.format(server_address))
               print('Sending data for TIME_STEP: {}'.format(time))

               if os.path.exists(server_address):
                   client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                   client.connect(server_address)
               client.send(data_json)
               del data_json
                   #print("Ready.")
                   #print("Ctrl-C to quit.")
                   #print("Sending 'DONE' shuts down the server and quits.")
                   #while True:
                       #try:
                           #x = input("> ")
                           #if "" != x:
                               #print("SEND:", x)
                               #client.send(x.encode('utf-8'))
                               #if "DONE" == x:
                                   #print("Shutting down.")
                                   #break
                       #except KeyboardInterrupt as k:
                           #print("Shutting down.")
                           #client.close()
                           #break
                   #else:
                       #print("Couldn't Connect!")
                   #print("Done")
        # ******************************************************************************************************************************************  """

    # ********************************************************* Iterate through All vehicles and detect close vehicles  *************************************************************
        for ID_1 in vehicles_array: 
            roadID_1 = traci.vehicle.getRoadID(ID_1)
            #print(roadID_1)
            current_position1 = traci.vehicle.getPosition(ID_1) 
            x, y = traci.vehicle.getPosition(ID_1)
            lon, lat = traci.simulation.convertGeo(x, y)
            current_position1 = (lat,lon)
            #print("first loop", current_position1)
            for ID_2 in vehicles_array: 
                if (ID_1 != ID_2): 
                    roadID_2 = traci.vehicle.getRoadID(ID_2)
                    #print(roadID_2)
                    current_position2 = traci.vehicle.getPosition(ID_2) 
                    x, y = traci.vehicle.getPosition(ID_2)
                    lon, lat = traci.simulation.convertGeo(x, y)
                    current_position2 = (lat,lon)
                    #print("second loop",current_position2)
                    distance_between_vehicles = geodesic(current_position1, current_position2).m
                    if (distance_between_vehicles < 30 and roadID_1 == roadID_2):   #distance in which we detect close vehicle is set to 30m. Vehicles have to be moving on the same road so same direction.
                                                                                    #this should change as we WANT to detect cars positioned in different roads. But also it doesn't make sense to detect a
                                                                                    #a car coming from the opposite road in a highway. 
                        #print("~*~*~*~*~*~*~*~ NOW printing the distances < 30 ~**~*~*~*~*~*~*")
                        print("Distance between {} and {} is : {}".format(ID_1,ID_2,distance_between_vehicles)) 

    # ********************************************************************************************************************************************************
        
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

