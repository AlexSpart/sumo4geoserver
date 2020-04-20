#!/usr/bin/env python

import os
import sys
import optparse
import subprocess
import json
import socket
import random
import math
import numpy
from geopy.distance import geodesic

os.environ["SUMO_HOME"] = "/home/drone/applications/sumo-dev"
# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
     tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
     sys.path.append(tools)
else:
      sys.exit("please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
PORT = 9999

density=dict() # store the value of the density calculate by each vehicle
maxDistanceDict=dict() # distance between a given vehicle and the furthest vehicles
closeVehiclesDict=dict() # number of neighbour's vehicles
my_data = {}
vehiclesInSimulation = list
vehicles_array = []
passenger_array = []
bus_array = []
truck_array = []
list_of_random_items =[]  

# contains TraCI control loop
def run():
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0
    my_data = {}
    vehiclesInSimulation = list
 

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
	categorizeVehicles()
	iteratePassenger()
    	trafficJamDetector()

        #    CLEAR THE FILE FROM PREVIOUS INPUTS
        #open("close_vehicles.txt", "w").close()
	#detectCloseVehicles()
        traci.simulationStep()
        step += 1
    traci.close()
    sys.stdout.flush()


   # ********************************************************* Categorize vehicles according Vclass to separate lists ***********************************************************
def categorizeVehicles():
        passenger_array_local = []
        bus_array_local = []
        truck_array_local = []
        for carID in vehicles_array:
            if vehicles_array:
                vehicle_class = traci.vehicle.getVehicleClass(carID)
                if (vehicle_class) == "passenger":
                    passenger_array_local.append(carID);
                    #print("Inserted item in passenger_array");
                elif (vehicle_class) == "bus":
                    bus_array_local.append(carID);
                    #print("Inserted item in bus_array");
                elif (vehicle_class) == "truck":
                    truck_array_local.append(carID);
                    #print("Inserted item in truck_array");
                else :
                    print("not available Vclass option");
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	global passenger_array,bus_array,truck_array
	passenger_array = passenger_array_local
	bus_array = bus_array_local
	truck_array = truck_array_local

   # ********************************************************* Iterate through Vclass:passenger only  ***********************************************************
def iteratePassenger():
        print("passenger_array is of length: ", len(passenger_array))
        group_of_items = passenger_array
        if len(passenger_array) != 0:   # if vehicles of this class has been inserted in the simulation
            num_to_select = (len(passenger_array))*1      # pick a percentage of the vehicles inserted
            num_to_select = int(math.ceil(num_to_select))   # round it up to catch error
            print("Picked {} out of {} vehicles" .format(num_to_select,len(passenger_array)))
            list_of_random_items = random.sample(group_of_items, num_to_select)
            for ID in list_of_random_items:
            	timestep = traci.simulation.getTime()
                #carID = vehicles_array[0]
                laneID = traci.vehicle.getLaneID(ID)
                laneINDEX = traci.vehicle.getLaneIndex(ID)
                vehicle_class = traci.vehicle.getVehicleClass(ID)
                vehicle_length = traci.vehicle.getLength(ID)
                vehicle_width = traci.vehicle.getWidth(ID)
                current_speed = traci.vehicle.getSpeed(ID)
	        #print("THe current SPEED from SUMO is: ",current_speed)
		current_speed = current_speed*100
	        current_speed = numpy.round(current_speed)
	        current_speed = int(current_speed)
               # print("THe current SPEED from SUMO after MULTIPLYING Is : ",current_speed)
                current_acceleration = traci.vehicle.getAcceleration(ID)
                current_angle = traci.vehicle.getAngle(ID)
		#print("THe current ANGLE from SUMO is: ",current_angle)
		current_angle = current_angle*10
		current_angle = numpy.round(current_angle)
	        current_angle = int(current_angle)
               # print("THe current ANGLE from SUMO after MULTIPLYING Is : ",current_angle)
	       # print("the current speed ------> ",  current_angle)
                current_position = traci.vehicle.getPosition(ID)
                x, y = traci.vehicle.getPosition(ID)
                lon, lat = traci.simulation.convertGeo(x, y)
	        lat = numpy.around(lat,7)*10000000
	        lon = numpy.around(lon,7)*10000000
	        lat = int(lat)
	        lon = int(lon)
	        # print ("computed latitude",type(lat),lat)
	        # print ("computed longitude",type(lon),lon)
                current_position3D = traci.vehicle.getPosition3D(ID)
              
	        CAM_message = {
			"type": "cam",
                        "origin": "self",
                        "version": "1.0.0",
                        "source_uuid": "sumo_client_1",
                        "timestamp": timestep,
                        "message": {
                            	"protocol_version": 1,
                            	"station_id": long(float(ID)),
                            	"generation_delta_time": 3,
                            	"basic_container": {
                                	"station_type": 5,
                                	"reference_position": {
                                    		"latitude": lat ,
                                    		"longitude": lon,
                                    		"altitude": 20000},
                                	"confidence": {
                                		"position_confidence_ellipse": {
                                    			"semi_major_confidence": 100,
                                    			"semi_minor_confidence": 50,
                                    			"semi_major_orientation": 180},
                                		"altitude": 3}},
                        		"high_frequency_container": {
                        			"heading": current_angle,
                        			"speed": current_speed,
                        			"drive_direction": 0,
                        			"vehicle_length": 40,
                        			"vehicle_width": 20,
                        			"confidence": {
                            				"heading": 2,
                            				"speed": 3,
                            				"vehicle_length": 0}
						}
                			}
            		      }
	        json_data = json.dumps(CAM_message)
                print(json_data)
	        # print("THE SIZE OF WHAT I SEND IS:",sys.getsizeof(json_data))
                server_address = "/tmp/CAVM_SAP"
                print('connecting to {}'.format(server_address))
                print('Sending data for PASSENGER TIME_STEP: {}'.format(timestep))
                if os.path.exists(server_address):
                    client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                    client.connect(server_address)
                    client.send(json_data)
		    client.close()
                del json_data
            else:
                print("array is still zero. It means that vehicles have not yes inserted in the simulation")

   # ********************************************************* Iterate through Vclass:bus only  *************************************************************
	"""
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
            .
            .
            .
	"""
   # ********************************************************* Iterate through Vclass:truck only  ***********************************************************
	"""        
	for carID in truck_array:  #implement any type of vehicle accordingly...
            print(carID)
	"""
   # ***************************************************** Iterate through all types of vehicles in simulation **********************************************
        """
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
                .
                .
                .              
        """
   # ******************************************************************************************************************************************  

def trafficJamDetector():
    vehiclesSpeed = dict()
    vehiclesCoor = dict()
    vehiclesAngle = dict()

     #put speeds and positions in dictionaries
    vehiclesInSimulation = traci.vehicle.getIDList()
    for i in vehiclesInSimulation:
        vehiclesSpeed[i]=traci.vehicle.getSpeed(i)
        print("speed------->", vehiclesSpeed[i])
        vehiclesAngle[i]=traci.vehicle.getAngle(i)
        print("Angle------->", vehiclesAngle[i])
        #vehiclesCoor[i]=traci.vehicle.getPosition(i) #not GPS coordinates but distance from the lane beginning
        #current_position = traci.vehicle.getPosition(i)
        x, y = traci.vehicle.getPosition(i)
        lon, lat = traci.simulation.convertGeo(x, y)
        vehiclesCoor[i] = (lat, lon)
        print("coords------->", vehiclesCoor[i])
    closeVehicles(vehiclesSpeed, vehiclesCoor, vehiclesAngle)

def closeVehicles(speed = dict(), coor = dict(), angle = dict()):
    for key1 in coor:
        closeVehicles=0
        maxDistanceDict[key1] = 0
        maxDistanceFront=0
        maxDistanceBack=0

        for key2 in coor:
            # calculate the distance between two vehicles
            distance = geodesic(coor[key1], coor[key2]).m  #this method is used for coordinates (lat,lon) as input
            #distance=math.sqrt((coor[key1][0]-coor[key2][0])**2 + (coor[key1][1]-coor[key2][1])**2) #THis method is used when the input of coor is SUMO position reference system

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
                #print("THe density of the vehiccle that I examine is: ------->",density)
                print("TO DENSITY EINAI--------> ", density[key])
                if traci.vehicle.getAllowedSpeed(key)*0.62>traci.vehicle.getSpeed(key): # if the speed of the vehicle is less than 62% of the allowed speed

                    if density[key]>50: # if the density is higher than 50
                        traci.vehicle.setColor(key,[255,0,0,255])

                    if density[key]>37 and density[key]<50: # if the density is included between 37 and 50
                        traci.vehicle.setColor(key,[255,69,0,255])

                    if density[key]>29 and density[key]<37: #if the density is included between 29 and 37
                        traci.vehicle.setColor(key,[255,165,0,255])

                    if density[key]<29: # if the density is less than 29
                        traci.vehicle.setColor(key,[0,255,0,255])

def detectCloseVehicles():

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

                    #print("~*~*~*~*~*~*~*~ NOW printing the distances < 30 ~**~*~*~*~*~*~*")
                    #print("Distance between {} and {} is : {}".format(ID_1,ID_2,distance_between_vehicles))
                    json_input = "Timestep %f: Distance between %s and %s is : %f" % (timestep,ID_1, ID_2, distance_between_vehicles)
                    #print (json_input)
                    with open("close_vehicles.txt", "a") as close_vehicles:
                        json_close_vehicles_list = json.dumps(json_input)  # use `json.loads` to do the reverse
                            #print(json_infos, file=f)
                        print >>close_vehicles, json_close_vehicles_list         #python 2.7


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
