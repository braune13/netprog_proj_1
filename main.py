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
		self.gateway = None
		self.interface = None
		
#===============================================================================
#Tree Class

class Tree:
	#Initialize Value
	def __init__(self):
		self.root = Node("root")
	
	#Get Root Node
	def getRoot(self):
		return self.root
	
	#Add Address
	# Takes binary or regular ip address
	# Stores address in tree
	def addAddr(self, addr):
		if(len(addr) < 32):
			addr = to_bin(addr)
		node = self.root
		if int(routes_table[addr][0]) == 0:
			self.root.gateway = routes_table[addr][2]
			self.root.interface = routes_table[addr][3]
		for i in range(len(addr)):
			if i == int(routes_table[addr][0]) - 1:
				node.gateway = routes_table[addr][2]
				node.interface = routes_table[addr][3]
			x = int(addr[i])
			if x == 0:
				if node.left == None:
					node.left = Node(x)
				elif node.left.val != 0:
					print "Error!"
				node = node.left
			if x == 1:
				if node.right == None:
					node.right = Node(x)
				elif node.right.val != 1:
					print "Error!"
				node = node.right
	
	#Find Address
	# Takes binary or regular ip address
	# Retrive interface/gateway for address in Tree
	# Returns a tuple in the form (gateway, interface)
	# Prints 'Lost!' if an address can't be found
	def findAddr(self, addr):
		if(len(addr) < 32):
			addr = to_bin(addr)
		node = self.root
		if int(routes_table[addr][0]) == 0:
			return (node.gateway, node.interface)
		for i in range(len(addr)):
			if i == int(routes_table[addr][0]) - 1:
				return (node.gateway, node.interface)
			x = int(addr[i])
			if x == 0:
				if node.left.val == 0:
					node = node.left
				else:
					print "Lost!"
			if x == 1:
				if node.right.val == 1:
					node = node.right
				else:
					print "Lost!"

	#Print Tree
	def __str__(self):
		if(self.root != None):
			return self._printTree(self.root)
		else:
			return "Empty Tree"

	#Private Print Tree
	def _printTree(self, node):
		if(node != None):
			return self._printTree(node.left) + str(node.val) + ' '  + self._printTree(node.right)
		return ""

	#Delete Tree
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
#Function to covert 32 bit binary to an ip address

def bin_to_ipv4(bin) :
	
	ipv4 = str(int(bin[0:8] , 2)) + "."
	ipv4 += str(int(bin[8:16], 2)) + "."
	ipv4 += str(int(bin[16:24], 2)) + "."
	ipv4 += str(int(bin[24:32], 2))
	
	return ipv4
				
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
			# key - prefix address, 0 - prefix length, 1 - gateway address in binary, 2 - regualr gateway address, 3 - interface 
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
		tree.addAddr(key)
	
	#Read PDUs from command line
	s = ""
	print "Enter the PDU into the console: "
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
			
			print "result_addr: " + bin_to_ipv4(result_addr)
			
			#Decrement the TTL by 1
			TTL_expired = False
			try:
				s_list[4] = int(s_list[4]) - 1
				if s_list[4] < 1:
					TTL_expired = True
			except:
				print "TTL is invalid"
			
				
			# key - prefix address, 0 - prefix length, 1 - gateway address in binary,
			#2 - regular gateway address, 3 - interface 
			route_info = routes_table[result_addr]
			
			next_hop_result_addr = ""
			next_hop_result_len = 0 
			#Look up next hop address in routing table, to see if 
			#the interface is point-to-point
			for key in routes_table.keys():
				next_hop_result = lcp(route_info[1], key) 
				
				if len(next_hop_result) > next_hop_result_len:
					next_hop_result_len = len(next_hop_result)
					next_hop_result_addr = key
			#check to see if the interface is point-to-point
			print "next_hop_result_addr" + bin_to_ipv4(next_hop_result_addr)
			print "routes_table[next_hop_result_addr][2] :" + routes_table[next_hop_result_addr][2]
			
			
			#bool to save need to do a arp lookup or not. True = lookup, False = no lookup
			arp_lookup = True
			
			if (routes_table[next_hop_result_addr][1] == ("0" * 32)):
				
				#in this case, we do not do an arp lookup
				arp_lookup = False
				
			
			if TTL_expired:
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " discarded (TTL expired)"
			
			elif not arp_lookup:
				
				local = routes_table[ routes_table[next_hop_result_addr][1] ]
				
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " via " + local[2] + " (" + local[3] + ")" + " ttl " + str(s_list[4]) 
			
			elif len(result) == 0:
				print "No route"
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " discarded (destination unreachable)"
			
			else:
				
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " via " + route_info[2] + " ttl " + str(s_list[4]) 
	
if __name__ == "__main__":
	main()