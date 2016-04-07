#Network Programming Project 1
##Coded by Brandon Thorne, Erica Braunschweig, Rob Russo

import os.path
#===============================================================================
#Finds longest prefix match to find the closest routing address 

def lcp(*s):
    return os.path.commonprefix(s)
    
#===============================================================================
#Function to covert a ipv4 address to binary

def to_bin(ipv4) :
    
    number_list = ipv4.split(".")
    binary_number = ""
    for i in range(0,len(number_list)):
        next_sect = "{0:b}".format(int(number_list[i]))
        prec_zeros = (8 - len(next_sect)) * "0"
        binary_number += (prec_zeros + next_sect)
        
    return binary_number
            

#===============================================================================
#Function to parse routes.txt and insert values into routes dictionary

def routesParser() :
    with open("routes.txt", "r") as f:
        for line in f:
            line_list = line.split()
            
            #convert prefix ip to binary
            prefix_list = (line_list[0]).split("/")
            prefix_addr = to_bin(prefix_list[0])
                
            
            #convert gateway ip to binary
            binary_gateway = to_bin(line_list[1])
            
            
            routes_table[prefix_addr] = [ prefix_list[1] , binary_gateway, line_list[1], line_list[2] ]
        print routes_table
            
#===============================================================================

#Function to parse routes.txt and insert values into routes dictionary
def arpParser() :
    with open("arp.txt", "r") as f:
        for line in f:
            line_list = line.split()
            arp_table[line_list[0]] = line_list[1]
            
#===============================================================================   
#Main

routes_table = {}
arp_table = {}


routesParser()
arpParser()

#print arp_table

#read PDUs from command line
s = ""
print "Enter the PDU into the console:"
while s != "exit":
    s = raw_input()
    s_list = s.split()
    
    # 0 = PDU arrival interface, 1 = source IPv4 address, 2 = destination IPv4 address
    # 3 = IPv4 protocol num (float), 4 = time to live (int), 5 = source port num
    # 6 destination port num
    
    if len(s_list) != 7:
        print "incorrect number of arguments"
        continue
    else:
        result_len = 0
        result_addr = ""
        
        #Get IPv4 prefix from routing table (most specific prefix)
        for key in routes_table.keys():
            dest_addr = to_bin(s_list[2])
            result = lcp(dest_addr, key) 
            
            if len(result) > result_len:
                result_len = len(result)
                result_addr = key
            
        #no route case
        route_info = []
        if len(result) == 0:
            print "No route"
            print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " discarded (destination unreachable)"
            
        else:
            route_info = routes_table[result_addr]
            print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " via " + route_info[2]
    
