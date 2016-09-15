import xml.etree.cElementTree as ET
import re
import codecs
import json

area = ''
osm = "{}.osm".format(area)

last_word = re.compile(r'\b\S+\.?$', re.IGNORECASE)
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
mapping = {
    'Ave' : 'Avenue',
    'Plz' : 'Plaza',
    'A' : 'Avenue',
    'St' : 'Street',
    'Blvd' : 'Boulevard',
    'Dr' : 'Drive',
    'Rd' : 'Road',
    'Ave.' : 'Avenue',
    'st' : 'Street',
    'St.' : 'Street',
    'Ctr' : 'Court',
    'Blvd.' : 'Boulevard',
    'Hwy' : 'Highway',
    'avenue' : 'Avenue',
    'Pl' : 'Plaza'
}

def shape_element(element):
    """This function shapes each element and its children in the OSM (XML) File. The output is a dictionary.
    The function only process 2 types of top level tags - nodes and ways, and all its second level tags.
    All attributes of these elements are turned into key/value pairs with a few exceptions. Keys that are in the CREATED list
    are stored within a dictionary. The data about longitude and latitude are stored within a list. It ignores all keys with
    problematic characters and keys with second colon."""
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['created'] = {}
        node['pos'] = []
        node['type'] = element.tag
        node['address'] = {}
        for key, value in element.attrib.items():
            if key in CREATED:
                node['created'][key] = value
            elif key == 'lat' or key == 'lon':
                node['pos'].append(value)
            else:
                node[key] = value
        for child in element.findall('tag'):
            key = child.attrib['k']
            if key == 'address':
                continue
            value = child.attrib['v']
            if re.search(problemchars,key):
                continue
            elif key.startswith('addr:'):
                if re.search('(.*):(.*):(.*)',key):
                    continue
                key = key[5:]
                node['address'][key] = value
            else:
                node[key] = value
        if element.tag == 'way':
            node['node_refs'] = []
            for ref in element.findall('nd'):
                node['node_refs'].append(ref.attrib['ref'])
        for key,value in node.items():
            if key == 'address' and value == {}:
                del node['address']
            elif key == 'address' and value != {}:
                for key2, value2 in value.items():
                    if key2 == 'street':
                        street = last_word.search(value2).group()
                        if street in mapping:
                            value['street'] = re.sub(last_word,mapping[street],value2)
                    elif key2 == 'postcode':
                        value2 = re.sub("\D","",value2)
                        value['postcode'] = value2[:5]
                    elif key2 == 'housenumber':
                        #I haven't found this to be a problem. Just to be sure housenumber is a number.
                    	value['housenumber'] = re.sub("\D","",value2)
        return node
    else:
        return None

def create_json(file_in):
    """This file iterates through the top level elements of the OSM (XML) file, for each element it calls the shape_element function.
    It then iterates through the item (dictionary) to look for street within an address to correct abbreviated street type names.
    It uses the mapping dictionary to correct abbreaviated street types. After the element is shaped it writes it directly into the JSON file
    so that no data are being stored in a memory."""
    file_out = "{0}.json".format(file_in)
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                fo.write(json.dumps(el) + "\n")

create_json(osm)
