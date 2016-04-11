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
		self.networkBits = None
		
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
			self.root.networkBits = routes_table[addr][0]
			#print "self.root.networkBits: " + routes_table[addr][0]
		for i in range(len(addr)):
			if i == int(routes_table[addr][0]) - 1:
				node.gateway = routes_table[addr][2]
				node.interface = routes_table[addr][3]
				node.networkBits = routes_table[addr][0]
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
	# Returns a tuple in the form (gateway, interface, networkBits)
	# Prints 'Lost!' if an address can't be found
	def findAddr(self, addr):
		if(len(addr) < 32):
			addr = to_bin(addr)
		node = self.root
		answer = ()
		
		num_matched = 0
		networkBits = 0
		
		for i in range(len(addr)):
			if node.gateway != None and node.interface != None:
				networkBits = node.networkBits
				answer = (node.gateway, node.interface, networkBits)
			x = int(addr[i])
			if x == 0:
				if node.left != None and node.left.val == 0:
					node = node.left
				else:
					break
			if x == 1:
				if node.right != None and node.right.val == 1:
					node = node.right
				else:
					break
			num_matched = num_matched + 1
		
		#print str(num_matched) + " < " + str(networkBits)
		if int(num_matched) < int(networkBits):
			
			#0.0.0.0/0 case
			zero = "00000000000000000000000000000000" 
			if zero in routes_table.keys():
				return (routes_table[zero][2], routes_table[zero][3], networkBits) 
			
			return ("Lost!")
		return answer

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
			try:
				first_lookup = tree.findAddr(s_list[2])
			except:
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " discarded (destination unreachable)"
				continue
			
			result = first_lookup[0]
			
			
			interface = first_lookup[1]
			
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
			#route_info = routes_table[result_addr]
			
			next_hop_result_addr = ""
			next_hop_result_len = 0 
			#Look up next hop address in routing table, to see if 
			
			try:
				next_hop_result = tree.findAddr(result)
			except:
				#could not find route
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " discarded (destination unreachable)"
				continue				
			
			arp = ""
			#if next_hop_result[2] == "32" or next_hop_result[0] != ("0.0.0.0"):
			if True:
				try:
					r = result
					if r == "0.0.0.0":
						r = s_list[2]
					
					arp = "-" + arp_table[r]
					
				except:
					arp = ""
			
			if TTL_expired:
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " discarded (TTL expired)"
			
			
			elif result[0] == "Lost":
				print "No route"
				print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " discarded (destination unreachable)"
			
			else:
				if result == "0.0.0.0":
					print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " directly connected (" + interface + arp + ") ttl " + str(s_list[4]) 
				else:
					print s_list[1] + ":" + s_list[5] + "->" + s_list[2] + ":" + s_list[6] + " via " + result + "(" + interface + arp + ") ttl " + str(s_list[4]) 
	
if __name__ == "__main__":
	main()