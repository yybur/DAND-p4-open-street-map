
# coding: utf-8

# 
# # Data Cleaning and Coverting the OSM into CSVs
# 
# 1. Having a general idea of the data to be wrangled:
# (what tags are there and how many)
# 
# 2. Interactive parsing
# 
# 3. Data wrangling: improving tags
# 
# 4. Shaping elements to be written into csv format
# 
# 5. Writting csv into SQL database
# 
# ## Cleaned Data in this file:
# 1. Street names and types
# 2. Phone number
# 3. Unifying key names in SQL database: postalcode and postcode, fixme and FIXME

# In[1]:

#!/usr/bin/env python



# import modules
import os
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import csv
import cerberus # for validation
import osm_schema # for validation


# FILE TO BE USED
soho = "soho_london.osm"  # test
# london = "extract_of_london.osm"  # project

# SCHEMA
SCHEMA = osm_schema.schema


# ## 1. Auditing street names and types
# 1. Finding street names to be improved, i.e. ending with abrreviation (St.) or British street types(mew）
# 2. Improving the street types

# ### 1.1 Finding street names to be improved

# In[2]:

# constructing street type
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected1 = ['Avenue', 'Boulevard', 'Buildings', 'Commons', 'Court', 'Circus', 
                    'Drivbe', 'Gardens', 'Lane', 'Mews','Parkway', 'Place', 
             'Road', 'Row', 'Square', 'Street', 'Trail', 'Yard']


# finding addr:street elements
def is_street_name(tag):
    return (tag.attrib['k'] == "addr:street")


# adding unexpected street types into a list
def audit_street_type(street_types, street_name, expected_list):
    # street_types = defaultdict(set)  <---in the outer function
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected_list:
            street_types[street_type].add(street_name)

            
# getting street names with bad street types
# these street names will be updated later

def street_names_to_improve(osmfile, expected_list):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'], expected_list)
    osm_file.close()
    return street_types


# In[3]:

# names to be improved

# UNCOMMENT THIS CODE TO SEE NAMES TO BE IMPROVED
# st_names1 = street_names_to_improve(london, expected1)
# st_names1


# 
# ### 1.2 Updating street types
# There are **two types of street names** in the set raised above: uncommonly seen street type and bad street types.
# #### 1. Uncommonly seen street type such as Mew or Row
# Supplementing such street types in the "expected" list 
# 
# #### 2. Bad street types such as abbreviations
# Creating a mapping dictionary to update bad street type
# 

# In[4]:

# updating the expected list
expected2 = ['Avenue', 'Arcade', 'Arch', 'Arches', 'Bank', 'Bridge', 'Boulevard', 'Buildings', 
             'Commons', 'Court', 'Circus', 'Circle', 'Close', 'Crescent', 
             'Docks', 'Drive', 
             'Fields',
             'Garden', 'Gate','Gardens', 'Ground','Green','Grove',
             'Hill', 'Highway',
             'Lane', 
             'Market','Mews', 
             'Park', 'Passage', 'Path', 'Pavement', 'Piazza', 'Plaza', 'Parkway', 'Place', 
             'Quay',
             'Road', 'Row', 'Square', 'Street',  
             'Terrace', 'Trail', 'Villas', 'Walk', 'Wharf','Yard',
             'South', 'North', 'East', 'West'
            ]


# In[5]:

# street names to be improved after updating the expected list

# UNCOMMENT THIS CODE TO SEE UPDATED STREET NAMES
#st_names2 = street_names_to_improve(london, expected2)
# st_names2


# In[6]:

# creating a mapping dictionary for names to be improved
mapping = { "Dock": "Docks",
           "James'": "James's'",
           
           "St": "Street",
            "St.": "Street",
           "street": "Street",
           "sreet": "Street",
           "Steet": "Street",
           "STREET": "Street",
           
           "Snowfields": "Snowsfields'",
           
           "Sq": "Square",
           "square": "Square",
           
           "Picadilly": "Piccadilly",
           
           "Ave": "Avenue",
           "Rd.": "Road",
           "road": "Road",
           "place": "Place",
           "lane": "Lane",
           "WQalk": "Walk",
           "way": "Way",
           "wharf": "Wharf",
           "gate": "Gate",
           "market": "Market",
           "parade": "Parade",
           "passage": "Passage",
           "place": "Place",
           "turnstile": "Turnstile"          
            }


# ### 1.3 Updated street names
# Check the street names after updating.

# In[7]:

def update_st_name(name, mapping):
    n = street_type_re.search(name)
    if n:
        n = n.group()
        if n in mapping:
            name = name[:-len(n)] + mapping[n]
            return name
        
        return name



# UNCOMMENT THE CODES BELOW TO SEE UPDATED STREET NAMES
#for st_type, st_name in st_names2.iteritems():
#        for name in st_name:
#            better_name = update_st_name(name, mapping)
#            print better_name


# ## 2. Fixing phone formats
# Getting rid of country code and zero number from the phone number and get rid of signals such as + or - or () from the number with the codes below.
# 
# * However, there are still one issue remain: some user input more than one number into a single field, such as "12345; 54321". These values are usually separated by ";", which made the the re/sub("\D") causing a new issue--"123454321". I will put that into to be improved later.

# In[8]:

country_code = ["44", "0044"]
zero = ["0", "00"]

# auditing if the tag is for phone number
def is_phone_num(tag):
    return (tag.attrib['k'] == "phone" or tag.attrib['k'] == "phone_1" )

# cleaning data to update phone number
def update_phone_num(v):
 
    num = re.sub("\D", "", v)
    
    for i in iter(country_code):
        if num.startswith(i):
            num = num[len(i):]
        else:
            continue
    
    for i in iter(zero):
        if num.startswith(i):
            num = num[len(i):]
        else:
            continue
    return num

# list of the updated phone number
def updated_phone_num(osmfile):
    osm_file = open(osmfile, "r")
    l = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone_num(tag):
                    x = "id", elem.attrib["id"],"phone",update_phone_num(tag.attrib["v"])
                    l.append(x)
    osm_file.close()
    return l


# In[9]:

# UNCOMMENTED THE CODE TO SEE UPDATED PHONE NUMBER
# updated_phone_num(london)


# ## 3. Unifying key names in SQL database during the shaping process 
# To convert postalcode into postcode, fixme into FIXME for easier SQL queries in the future.
# The cleaning process is scripted in shape_tag(el,t).

# # Shaping elements and writing the dataset into CSVs

# In[10]:

# csv files to be converted into
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# regular expression
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# In[11]:

# shape tags
def shape_tag(el, t): 
    tag = {'id': el.attrib['id'],
           'key': t.attrib['k'],
           'value': t.attrib['v'],
           'type' : 'regular'
          }

    # update the street type 
    if is_street_name(t):
        tag['value'] = update_st_name(tag['value'], mapping)

    # use .patrition to split attrib key before and after colon
    if LOWER_COLON.match(tag['key']):
        # partition: 
        tag['type'], _, tag['key'] = tag['key'].partition(':')

    # unify phone number formats
    if tag['key'] == "phone":
        tag['value'] = update_phone_num(tag['value'])
        
    # unify fixme keycode to all uppercase for easier SQL query 
    if tag['key'] == "fixme":
        tag["key"] =="FIXME"
        
    # unify postcode and postal_code for easier SQL query 
    if tag['key'] == "postal_code":
        tag['key'] = "postcode"
        
    return tag


# shape way_node
def shape_way_node(el, i, nd):
    return {
        'id'       : el.attrib['id'],
        'node_id'  : nd.attrib['ref'],
        'position' : i
    }


# shape element
def shape_element(el, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS):                     
    tags = [shape_tag(el, t) for t in el.iter('tag')]

    # I changed the old node_attribs codes a bit. (it should be as way_attribs codes) 
    # however the old scripts rasied KEY ERROR: USER 
    # after checking the original osm, the error was due to missing attributes in some nodes.
    
    if el.tag == 'node':
        node_attribs = {}
        for f in node_attr_fields:
            if f in el.attrib: # if the key name exists in the element's attributes
                node_attribs[f] = el.attrib[f] # return the value as the attribute's value
            else:
                node_attribs[f] = "Missing Attribute" # if it does not exist, return the value as missing attribute
        return {'node': node_attribs, 'node_tags': tags}

      
    elif el.tag == 'way':
        way_attribs = {f: el.attrib[f] for f in way_attr_fields}        
        way_nodes = [shape_way_node(el, i, nd) 
                     for i, nd in enumerate(el.iter('nd'))]
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# In[12]:

# get rid of random phone number 1234567890
def random_value(el):
    if el.tag == "node":
        t = el.iter("tag")
        for tag in t:
            if tag.attrib['k'] == "phone" and tag.attrib['v'] ==  "1234567890":
                return True


# In[13]:


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way')):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            
            # get rid of random phone numbers
            if random_value(elem):
                continue
                
            else:         
                yield elem
                root.clear()

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[14]:

# ================================================== #
#               Main Functions                       #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


# In[15]:

process_map(soho, validate = False)

# turned validation down here as some elements do not have uid attribute
#(Exception: 
#Element of type 'node' has the following errors:
#[{'uid': ["field 'uid' cannot be coerced: invalid literal for int() with base 10: 'Missing Attribute'",
#          'must be of integer type']}])


# In[ ]:



