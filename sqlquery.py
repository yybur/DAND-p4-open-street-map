#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pprint

conn = sqlite3.connect('p1.db')
c = conn.cursor()


#############################
######    users       #######
#############################

# users contributed to nodes
q_user = '''select user, count (*) as num from nodes group by user order by num desc limit 5'''
c.execute(q_user)
user = c.fetchall()
pprint.pprint(user)


# users contributed to ways
q_user2 = '''select user, count (*) as num from ways group by user order by num desc limit 5'''
c.execute(q_user2)
user = c.fetchall()
pprint.pprint(user)



#############################
######    theatres    #######
#############################

# theatres marked in nodes
q_theatre = '''select id, value from nodes_tags where key = "name" and id in 
(select id from nodes_tags where key = "amenity" and "value" = "theatre")'''
c.execute(q_theatre)
theatres = c.fetchall()
#pprint.pprint(theatres) # there are duplication in the result 
theatre_list = []
for theatre in theatres:
	theatre_list.append(theatre[1])
pprint.pprint(set(theatre_list))
print len(theatre_list)


# theatres marked in ways
q_theatre2 = '''select id, value from ways_tags where key = "wikipedia" and id in 
(select id from ways_tags where key = "amenity" and "value" = "theatre")'''
c.execute(q_theatre2)
theatres2 = c.fetchall()
#pprint.pprint(theatres2) # there are duplication in the result 
theatre_list2 = []
for theatre2 in theatres2:
	theatre_list2.append(theatre2[1][3:]) 
	# as the returned is wikipedia title, with "en:"" before the theatre name. SO [3:] is used to remove en:
print len(theatre_list2)


x = theatre_list + theatre_list2  # combine the two lists
pprint.pprint(set(x)) # use set to avoid duplication
print len(x)




###################################
######    bicycle_parking    ######
###################################

# number of bicycle_parking spots in nodes_tag
parking_spot = '''select value, count(*) as num from nodes_tags where key = "amenity" and value = "bicycle_parking"'''
c.execute(parking_spot)
bicycle_parking = c.fetchall()
pprint.pprint(bicycle_parking)

# sum of total bicycle_parking capacity
# not all of bicycle_parking tag has capacity info provided 
parking_capacity = '''select count(*) as num, sum(value) from nodes_tags where key = "capacity" and 
id in
(select id from nodes_tags where key = "amenity" and value = "bicycle_parking")'''
c.execute(parking_capacity)
bicycle_parking_sum = c.fetchall()
print bicycle_parking_sum


