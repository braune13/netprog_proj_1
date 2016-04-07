#Network Programming Project 1
##Coded by Brandon Thorne, Erica Braunschweig, Rob Russo

import os.path

#===============================================================================
#Global Variables

routes_table = {}
arp_table = {}

#===============================================================================
#Node Class
class Node:
	def __init__(self, val):
		self.right = None
		self.left = None
		self.val = val
#===============================================================================
#Tree Class
class Tree:
    #Initialize Value
	def __init__(self):
		self.root = Node("root")
    
    #Get Root Node
	def getRoot(self):
		return self.root

    #Add Node
	def add(self, val):
		if(val > 0):
			self._add(val, self.root.left)
		if(val < 1):
		    self._add(val, self.root.right)
		else:
			self._add(val, self.root)
			
    #Private add node
	def _add(self, val, node):
		if(val < node.val):
			if(node.left == None):
				node.left = Node(val)
			else:
				self._add(val, node.left)
		elif(val == node.val):
		    if(val == 0):
		        if(node.left == None):
		            node.left = Node(val)
		        else:
		            self._add(val, node.left)
		    if(val == 1):
		        if(node.right == None):
		            node.right = Node(val)
		        else:
		            self._add(val, node.right)
		else:
			if(node.right == None):
				node.right = Node(val)
			else:
				self._add(val, node.right)
				
    #Find Node
	def find(self, val):
		if(self.root != None):
			return self._find(self.root, val)
		else:
			return None
			
    #Private Find Node
	def _find(self, node, val):
		if(node.val == val):
			return node
		if(node.val > val and node.left != None):
			self._find(node.left, val)
		if(node.val < val and node.right != None):
			self._find(node.right, val)

	def __str__(self):
		if(self.root != None):
			return self._printTree(self.root)
		else:
			return "Empty Tree"

	def _printTree(self, node):
		if(node != None):
			return self._printTree(node.left) + str(node.val) + ' '  + self._printTree(node.right)
		return ""

	def delete(self):
		self.root = None

#===============================================================================
#Finds longest prefix match to find the closest routing address 

def lcp(*s):
    return os.path.commonprefix(s)
    
#===============================================================================
#Function to covert an ipv4 address to binary

def to_bin(ipv4) :
    
    number_list = ipv4.split(".")
    binary_number = ""
    for i in range(0,len(number_list)):
        next_sect = "{0:b}".format(int(number_list[i]))
        prec_zeros = (8 - len(next_sect)) * "0"
        binary_number += (prec_zeros + next_sect)
        
    return binary_number

#===============================================================================
#Function to build 32 bit tree
def buildTree(node, depth, addr):
    if(depth < 32 and depth < len(addr)):
        val = addr[depth]
        depth += 1
        if(int(val) == 0):
            if(node.left == None):
                node.left = Node(int(val))  
            buildTree(node.left, depth, addr)
        if(int(val) == 1):
            if(node.right == None):
                node.right = Node(int(val))
            buildTree(node.right, depth, addr)
                
        
        
        

#===============================================================================
#Function to parse routes.txt and insert values into routes dictionary

def routesParser() :
    with open("input/best/routes.txt", "r") as f:
        for line in f:
            line_list = line.split()
            
            #Convert prefix ip to binary
            prefix_list = (line_list[0]).split("/")
            prefix_addr = to_bin(prefix_list[0])
                
            #Convert gateway ip to binary
            binary_gateway = to_bin(line_list[1])
            
            #Add to routing table
            routes_table[prefix_addr] = [ prefix_list[1] , binary_gateway, line_list[1], line_list[2] ]
        
            
#===============================================================================

#Function to parse routes.txt and insert values into routes dictionary
def arpParser() :
    with open("input/best/arp.txt", "r") as f:
        for line in f:
            line_list = line.split()
            arp_table[line_list[0]] = line_list[1]
            
#===============================================================================   
#Main
def main():
    #Create Tables
    routesParser()
    arpParser()
    tree = Tree()
    
    # Build Tree
    for key in routes_table:
        buildTree(tree.getRoot(), 0, key)
    
    #Print tables
    print(tree)
    print routes_table
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
    
if __name__ == "__main__":
    main()