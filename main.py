routes_table = {}
#===============================================================================
#Function to parse routes.txt and insert values into routes dictionary
def routesParser() :
    with open("routes.txt", "r") as f:
        for line in f:
            line_list = line.split()
            routes_table[line_list[0]] = line_list[1:3]
            
            print line_list
            
#===============================================================================   


routesParser()
print routes_table