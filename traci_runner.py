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

density=dict() # store the value of the density calculate by each vehicle
maxDistanceDict=dict() # distance between a given vehicle and the furthest vehicles 
closeVehiclesDict=dict() # number of neighbour's vehicles

def closeVehicles(speed = dict(), coor = dict(), angle = dict()):
    for key1 in coor:
        closeVehicles=0
        maxDistanceDict[key1] = 0
        maxDistanceFront=0
        maxDistanceBack=0

        for key2 in coor:
            # calculate the distance between two vehicles
            distance=math.sqrt((coor[key1][0]-coor[key2][0])**2 + (coor[key1][1]-coor[key2][1])**2)

            # calculate the angle between two vehicles
            direction=math.atan2(coor[key2][1]-coor[key2][0], coor[key1][1]-coor[key1][0])

            if distance<100 and key1!=key2: # if the vehicles are close enough

                if angle[key2]>angle[key1]-25 and angle[key2]<angle[key1]+25: #if the vehicles drive in same direction
                    closeVehicles = closeVehicles+1 # increment the number of close vehicles

                    if direction>0: # if the vehicle is in front of the given vehicle

                        if distance > maxDistanceFront: # if the distance between them is higher than the max distance in front
                            maxDistanceFront = distance

                    else: # if the vehicle is behind

                        if distance > maxDistanceBack: # if the distance between them is higher than the max distance behind
                            maxDistanceBack = distance

        maxDistanceDict[key1]=maxDistanceFront+maxDistanceBack # calculate the total distance between the two furthest vehicles
        closeVehiclesDict[key1]=closeVehicles # store the number of neighbours' vehicles
    densityCalculation(maxDistanceDict, closeVehiclesDict)


def densityCalculation(distanceMax = dict(), closeVeh = dict()):
    for key in closeVeh:
        
        if distanceMax[key] != 0: # avoid division by zero

            if key in traci.vehicle.getIDList(): # check if the vehicle is currently in the simulation
                density[key]=((closeVeh[key]/3)*1000)/(distanceMax[key]) # calculation of the density around the vehicle

                if traci.vehicle.getAllowedSpeed(key)*0.62>traci.vehicle.getSpeed(key): # if the speed of the vehicle is less than 62% of the allowed speed
                    
                    if density[key]>50: # if the density is higher than 50
                        traci.vehicle.setColor(key,[255,0,0,255])

                    if density[key]>37 and density[key]<50: # if the density is included between 37 and 50
                        traci.vehicle.setColor(key,[255,69,0,255])

                    if density[key]>29 and density[key]<37: #if the density is included between 29 and 37
                        traci.vehicle.setColor(key,[255,165,0,255])

                    if density[key]<29: # if the density is less than 29
                        traci.vehicle.setColor(key,[0,255,0,255])

# contains TraCI control loop
def run():
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0
    vehicles_array = []
    my_data = {}
    vehiclesInSimulation = list
        
#    CLEAR THE FILE FROM PREVIOUS INPUTS
    open("mobility_infos.txt", "w").close()
    open("close_vehicles.txt", "w").close()

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
    # ********************************************************* Iterate through Vclass:passenger only  ***********************************************************
        print("passnger_array is of length: ", len(passenger_array))
        group_of_items = passenger_array               
        if len(passenger_array) != 0:   # if vehicles of this class has been inserted in the simulation
            num_to_select = (len(passenger_array))*0.4      # pick a percentage of the vehicles inserted
            num_to_select = int(math.ceil(num_to_select))   # round it up to catch error 
            print("Picked {} out of {} vehicles" .format(num_to_select,len(passenger_array)))
            list_of_random_items = random.sample(group_of_items, num_to_select)
        else: 
            print("array is still zero. It means that vehicles have not yes inserted in the simulation")
        for ID in list_of_random_items:
            print(ID)
            timestep = traci.simulation.getTime()
            #carID = vehicles_array[0]
            laneID = traci.vehicle.getLaneID(ID)
            laneINDEX = traci.vehicle.getLaneIndex(ID)
            vehicle_class = traci.vehicle.getVehicleClass(ID)
            vehicle_length = traci.vehicle.getLength(ID)
            vehicle_width = traci.vehicle.getWidth(ID)
            current_speed = traci.vehicle.getSpeed(ID)
            current_acceleration = traci.vehicle.getAcceleration(ID)
            current_angle = traci.vehicle.getAngle(ID)
            current_position = traci.vehicle.getPosition(ID)
            x, y = traci.vehicle.getPosition(ID)
            lon, lat = traci.simulation.convertGeo(x, y)
            current_position3D = traci.vehicle.getPosition3D(ID)
            mydata = {
                        "_id":ID,
                        "Timestamp":timestep,
                        "StationID":"0x3364",
                        "StationType":"5",
                        "Latitude":lat,
                        "Longitude":lon,
                        "Position3D":current_position3D,
                        "DetectionTime":timestep,
                        "ReferenceTime":timestep,
                        "eventType":"3",
                        "Vclass": vehicle_class,
                        "Vlength": vehicle_length,
                        "Vwidth": vehicle_width,
                        "speed": current_speed,
                        "acceleration": current_acceleration,
                        "angle": current_angle,
                        "laneID": laneID
                        }
            data_json = json.dumps(mydata)
            #print(data_json)
            server_address = "/tmp/CAVM_SAP"
            print('connecting to {}'.format(server_address))
            print('Sending data for PASSENGER TIME_STEP: {}'.format(timestep))
            if os.path.exists(server_address):
                client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                client.connect(server_address)
                client.send(data_json)
            del data_json

    # ********************************************************************************************************************************************************
    # ********************************************************* Iterate through Vclass:bus only  *************************************************************
        print("bus_array is of length: ", len(bus_array))
        group_of_items = bus_array               
        if len(passenger_array) != 0:   # if vehicles of this class has been inserted in the simulation
            num_to_select = (len(passenger_array))*0.4      # pick a percentage of the vehicles inserted
            num_to_select = int(math.ceil(num_to_select))   # round it up to catch error 
            print("Picked {} out of {} vehicles" .format(num_to_select,len(passenger_array)))
            list_of_random_items = random.sample(group_of_items, num_to_select)
        else: 
            print("array is still zero. It means that vehicles have not yes inserted in the simulation")

        for ID in list_of_random_items:
            print(ID)
            timestep = traci.simulation.getTime()
            #carID = vehicles_array[0]
            laneID = traci.vehicle.getLaneID(ID)
            laneINDEX = traci.vehicle.getLaneIndex(ID)
            vehicle_class = traci.vehicle.getVehicleClass(ID)
            vehicle_length = traci.vehicle.getLength(ID)
            vehicle_width = traci.vehicle.getWidth(ID)
            current_speed = traci.vehicle.getSpeed(ID)
            current_acceleration = traci.vehicle.getAcceleration(ID)
            current_angle = traci.vehicle.getAngle(ID)
            current_position = traci.vehicle.getPosition(ID)
            x, y = traci.vehicle.getPosition(ID)
            lon, lat = traci.simulation.convertGeo(x, y)
            current_position3D = traci.vehicle.getPosition3D(ID)
            mydata = {
                        "_id":ID,
                        "Timestamp":timestep,
                        "StationID":"0x3364",
                        "StationType":"5",
                        "Latitude":lat,
                        "Longitude":lon,
                        "Position3D":current_position3D,
                        "DetectionTime":timestep,
                        "ReferenceTime":timestep,
                        "eventType":"3",
                        "Vclass": vehicle_class,
                        "Vlength": vehicle_length,
                        "Vwidth": vehicle_width,
                        "speed": current_speed,
                        "acceleration": current_acceleration,
                        "angle": current_angle,
                        "laneID": laneID
                        }
            data_json = json.dumps(mydata)
            #print(data_json)
            server_address = "/tmp/CAVM_SAP"
            print('connecting to {}'.format(server_address))
            print('Sending data for BUS TIME_STEP: {}'.format(timestep))
            if os.path.exists(server_address):
                client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                client.connect(server_address)
                client.send(data_json)
            del data_json

    # ********************************************************************************************************************************************************
    # ********************************************************* Iterate through Vclass:truck only  ***********************************************************
        for carID in truck_array:  #implement any type of vehicle accordingly...
            print(carID) 
    # ********************************************************************************************************************************************************      
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
        """ # ***************************************************** Iterate through all types of vehicles in simulation **********************************************
         group_of_items = vehicles_array               
         if len(passenger_array) != 0:   # if vehicles of this class has been inserted in the simulation
            num_to_select = (len(passenger_array))*0.4      # pick a percentage of the vehicles inserted
            num_to_select = int(math.ceil(num_to_select))   # round it up to catch error 
            print("Picked {} out of {} vehicles" .format(num_to_select,len(passenger_array)))
            list_of_random_items = random.sample(group_of_items, num_to_select)
         else: 
            print("array is still zero. It means that vehicles have not yes inserted in the simulation")
         for carID in list_of_random_items: 
            #print (carID)
            if vehicles_array:
                timestep = traci.simulation.getTime()
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
                #print(timestep,carID,vehicle_class,current_position,current_speed,current_acceleration,laneID)
                #print(lon,lat)
                #print(lon)
                #print(lat)
        
                if vehicle_class == "truck" :
                    mydata = {
                        "time": timestep,
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
                        "Timestamp":timestep,
                        "StationID":"0x3364",
                        "StationType":"5",
                        "Latitude":lat,
                        "Longitude":lon,
                        "DetectionTime":timestep,
                        "ReferenceTime":timestep,
                        "eventType":"3",
                        "Vclass": vehicle_class,
                        "Vlength": vehicle_length,
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
                    server_address = "/tmp/CAVM_SAP"
                    #server_address = "/tmp/python_unix_sockets_example"
                    print('connecting to {}'.format(server_address))
                    print('Sending data for TIME_STEP: {}'.format(timestep))

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
            timestep = traci.simulation.getTime()
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
                        #print("Distance between {} and {} is : {}".format(ID_1,ID_2,distance_between_vehicles)) 
                        json_input = "Timestep %f: Distance between %s and %s is : %f" % (timestep,ID_1, ID_2, distance_between_vehicles)
                        print (json_input)
                        with open("close_vehicles.txt", "a") as close_vehicles:
                            json_close_vehicles_list = json.dumps(json_input)  # use `json.loads` to do the reverse
                                #print(json_infos, file=f)
                            print >>close_vehicles, json_close_vehicles_list         #python 2.7
    # ********************************************************************************************************************************************************
        
        infos = traci.vehicle.getAllSubscriptionResults()
        with open("mobility_infos.txt", "a") as f:
            json_infos = json.dumps(infos)  # use `json.loads` to do the reverse
	#            print(json_infos, file=f)
            print >>f, json_infos         #python 2.7

        vehiclesSpeed = dict()
        vehiclesCoor = dict()
        vehiclesAngle = dict()

        if step%30==0:
            #put speeds and positions in dictionaries
            vehiclesInSimulation = traci.vehicle.getIDList()
            for i in vehiclesInSimulation:
                vehiclesSpeed[i]=traci.vehicle.getSpeed(i)
                vehiclesAngle[i]=traci.vehicle.getAngle(i)
                #vehiclesCoor[i]=traci.vehicle.getPosition(i) #not GPS coordinates but distance from the lane beginning
                #current_position = traci.vehicle.getPosition(i)
                x, y = traci.vehicle.getPosition(i)
                vehiclesCoor[i] = traci.simulation.convertGeo(x, y)
            print(vehiclesSpeed)
            print(vehiclesCoor)
            closeVehicles(vehiclesSpeed, vehiclesCoor, vehiclesAngle)
        
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
    sumoProcess = subprocess.Popen([sumoBinary, "-c", "scenario/map.sumocfg"], stdout=sys.stdout, stderr=sys.stderr)
    run()
    sumoProcess.wait()

