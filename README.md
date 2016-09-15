# openstreetmap-wrangler
Cleans OpenStreetMap dataset, converts it from XML to JSON format. The cleaned .json file is ready to be imported into a MongoDB database using the <em>mongoimport</em> shell command.

It does the following things:
- process 2 types of top level tags: "node" and "way"
- attributes in the CREATED array should be added under a key "created"
- attributes for latitude and longitude are added to a "pos" array, for use in geospacial indexing.
- if the second level tag "k" value contains problematic characters, it is ignored
- if the second level tag "k" value starts with "addr:", it's added to a dictionary "address"
- if there is a second ":" that separates the type/direction of a street,
  the tag is ignored, for example:

tag k="addr:housenumber" v="5158"/
tag k="addr:street" v="North Lincoln Avenue"/
tag k="addr:street:name" v="Lincoln"/
tag k="addr:street:prefix" v="North"/
tag k="addr:street:type" v="Avenue"/

  is turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
...
}

- for "way" specifically:

  nd ref="305896090"/
  nd ref="1719825889"/

is turned into
"node_refs": ["305896090", "1719825889"]

- if the street type is abbreviated, the mapping dictionary corrects the abbreviations
- makes sure postcode is in a correct 5-digit form
