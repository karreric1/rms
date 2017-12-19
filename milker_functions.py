#Copyright (c) 2017 Eric Karr
#Software is licensed under the MIT License
#complete license can be found at https://github.com/karreric1/rms/


import numpy as np
import pandas as pd
import decimal
import matplotlib.pyplot as plt

def exp_generator(samples, mean):
    '''generates a list of exponentially distributed values
    
    samples = number of generated values
    mean = mean value of distribution'''
    exp_list = []
    for i in range(0,samples):
        current = int(round(np.random.exponential(mean), 0))
        if current == 0:
            current = int(1) #Minimum time between arrivals is 1 second
        exp_list.append(current)
    return exp_list


def norm_generator(samples, mean, stdev):
    '''generates a list of normally distributed values
    
    samples = number of generated values
    mean = mean value of distribution
    stdev = standard deviation of distribution '''
    norm_list = []
    for i in range(0,samples):
        current = int(round(np.random.normal(mean, stdev), 0))
        if current == 0:
            current = int(1) #minimum time between arrivals is 1 second
        norm_list.append(current)
    return norm_list 

def time_totalizer(values):
    '''generates an additive list of times since 0 for randomly generated values
    
    values: list of randomly generated numbers'''
    time_list = [values[0],]
    current_time = values[0]
    for i in range(0, len(values[0:-1])):
        current_time += values[i+1]
        time_list.append(int(round(current_time,0)))
    return time_list
    
def parallel_milker(arrivals, service_times, breakdowns, initial_queue, servers, duration, maint_times, maint_duration):
    '''simulates milking robot in a X/X/x queue with random breakdowns and deterministic
    downtime for maintenance.  arrivals and service times can be Markovian or Generally Distributed
    
    arrivals:  list of arrival times in seconds
    service_times:  list of service times in seconds
    breakdowns: list of breakdown times in seconds
    initial_queue: integer length of initial queue in number of customers
    servers:  integer number of parallel servers
    duration:  length of model run-time in seconds
    maint_interval:  list of seconds between maintenance periods for each server
    maint_duration: length of deterministic maintenance in seconds'''
    #debug
    print(servers)
    
    #initialize lists of output data
    time_list = []  #time in seconds after simulation start
    customers_list = []  #number of customers in system at each cycle
    service_list = [] #time in seconds of each service
    server1_downtime = []
    server2_downtime = [] 
    server1_occupied = []
    server2_occupied = []
    cumulative_customers = []
    
    #initialize counting within algorithm
    arrival_index = 0 #initialize use of first arrival time from arrivals list
    service_index = 0 #initialize use of first service time from arrivals list
    time_index = 0 #initialze time counter at 0
    queue_length = 0 #initialize queue length at 0
    cum_cust_count = 0
    
    #initialize customer status - determines whether a customer is in server or not
    server1_status = 0 #0 equals unoccupied.  1 equals occupied
    server2_status = 0 #0 equals unoccupied.  1 equals occupied
    
    #initialize server up status - 1 = up, 0 = down for maintenance
    server1_available = 1
    server2_available = 1
    
    #initialize server maintenance time
    server1_maintenance_time = 0
    server2_maintenance_time = 0
    
    for i in range(0, duration):
        #keeping time in system
        time_index += 1 #increment time index by one unit
        time_list.append(time_index) #add current simulation time to time_list
        
        #bring servers down for scheduled maintenance
        if time_index % maint_times[0] == 0:# modulo of zero indicates time index is at a multiple of maint time
            server1_available = 0
            server1_maintenance_time = maint_duration # down for maintenance for maintenance_duration seconds
        if time_index % maint_times[1] == 3600: #offset by 1 hour
            server2_available = 0
            server2_maintenance_time = maint_duration #down for maintenance for 30 minutes
        
        #keep servers down until maintenance time = 0
        if server1_available == 0:
            server1_maintenance_time -= 1 #decrease server maintenance time by 1 for each cycle
            if server1_maintenance_time < 1: # if maintenance time expires, set server to available
                server1_available = 1
        if server2_available == 0:
            server2_maintenance_time -= 1
            if server2_maintenance_time < 1:
                server2_available = 1
        
        #log server uptime & downtime
        server1_downtime.append(server1_available)
        server2_downtime.append(server2_available)
        
        #add to queue as customers arrive 
        if int(arrivals[arrival_index]) == int(time_index): #if arrival time equals simulation time, increment queue by 1
            queue_length += 1
            arrival_index += 1  #increment arrival index by 1 to set next arrival time
            cum_cust_count += 1 #increment cumulative customers by 1
        
        #move a customer into server if queue is greater than 0 and unoccupied
        if queue_length > 0:  #at least one customer in queue - therefore can move into server if empty
            #run two servers in parallel
            if server1_available == 1:
                if server1_status == 0: #if server is empty:
                    server1_status = 1 #set server to full
                    queue_length -= 1 #decrease queue by 1 customer
                    service1_time_remaining = service_times[service_index] #set length of time for service
                    service_list.append([1, time_index, service_times[service_index]])# create record of this service time.  list of [server,time]
                    service_index += 1 # increment service index for next customer
    #second server is not being utilized properly
        if servers == 2: #run second server if servers = 2
            if queue_length > 0:
            #print('second server up')
                if server2_available == 1:
                    if server2_status == 0: #if server is empty:
                        server2_status = 1 #set server to full
                        queue_length -= 1 #decrease queue by 1 customer
                        service2_time_remaining = service_times[service_index] #set length of time for service
                        service_list.append([2, time_index, service_times[service_index]])# create record of this service time.  list of [server,time]
                        service_index += 1 # increment service index for next customer

        #serve customer in servers
        if server1_status == 1: #if server is full:
            service1_time_remaining -= 1 #decrease service time remaining by 1 second
            if service1_time_remaining < 1:  #current customer is about to leave server
                server1_status = 0 #set server open for next customer
        if server2_status == 1: #if server is full:
            service2_time_remaining -= 1 #decrease service time remaining by 1 second
            if service2_time_remaining < 1:  #current customer is about to leave server
                server2_status = 0 #set server open for next customer
        customers_list.append(queue_length)
        server1_occupied.append(server1_status)
        server2_occupied.append(server2_status)
        cumulative_customers.append(cum_cust_count)
    
    total_customers = arrival_index
    return time_list, total_customers, customers_list, service_list, server1_downtime, server2_downtime, server1_occupied, server2_occupied, cumulative_customers




