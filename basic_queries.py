
# coding: utf-8

# # Basic queries about the osm file
# 
# 1. What's the size of the file
# 2. How many elements' tags (node, way, relation) are there and what are they?
# 3. Who has contributed to the OSM? (individual user)

# In[1]:

#!/usr/bin/env python


# import modules
import os
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# FILE TO BE USED
soho = "soho_london.osm"  # test
london = "extract_of_london.osm"  # project


# ## 1. What's the size of the file?

# In[2]:

print "1. Size of the file:", os.path.getsize(london)


# ## 2. How many elements' tags (node, way, relation) are there and what are they?

# In[3]:

def count_tags(filename):
        tags = defaultdict(int)
        for event, elem in ET.iterparse(filename):
            tag = elem.tag
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1
        return tags


# In[8]:

print "Tags in the file:", 
pprint.pprint(count_tags(london))


# ## 3. Who has contributed to the OSM? (individual user)
# 

# In[14]:

# Note:there are some elements without user attribute (missing attribute)

# to get the get user id that contributed to the element
def get_user(element):
    try:
        if element.attrib["user"]:
            u = element.attrib["user"]
            return u
    except:
        pass

    
# to get list of individul users who contributed to the osm
def process_map_for_id(filename):
    users = set()
    user_list= []
    for _, element in ET.iterparse(filename):
        user = get_user(element)
        
        if user != None: # there are none in the returned, so must get rid of the None value first.
            user_list.append(user)
    users= set(user_list)
    return users


# In[15]:

users = process_map_for_id(london)
print "Number of users who contributed to the file", len(users)
print "\n"
print "Usernames:"
pprint.pprint(users)


# In[ ]:



