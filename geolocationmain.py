from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import xml.etree.ElementTree as ET

# index : 3 => address, 7 => lat ,10 => lng 
output_templat = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" ,  \
                     "<root>\n" ,                                   \
                        "\t<address>",  "" ,   "</address>\n",      \
                        "\t<coordinates>\n",                        \
                                        "\t\t<lat>", "" ,"</lat>\n",\
                                        "\t\t<lng>", "" ,"</lng>\n",\
                        "\t</coordinates>\n" ,                      \
                    "</root>" ]


GEOLOC_API_KEY = 'PUT_YOUR_API_KEY_HERE'
base_url = 'https://maps.googleapis.com/maps/api/geocode/'

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home_page.html")

@app.route("/getAddressDetails", methods=["POST"])
def add():
    address       = request.form.get("address")
    output_format = request.form.get("output_format")
    params = {
        'key': GEOLOC_API_KEY,
        'address': address.replace(' ', '+')
    }
    
    if output_format == 'json':
         response = requests.get(base_url + 'json?', params=params)
         result      = formated_result_json(response.json())
    else:
         response = requests.get(base_url + 'xml?',  params=params)
         result      = formated_result_xml(response.text) 
              
    return render_template("home_page.html", address=address ,\
                         data_format=output_format,result=result)


def formated_result_json(raw_json_output):
    for obj in raw_json_output["results"]:
        formated_result = { "address": obj["formatted_address"] , "coordinates": {
                "lat": obj["geometry"]["location"]["lat"] ,
                "lng": obj["geometry"]["location"]["lng"]
            }
        }

    return formated_result 

def formated_result_xml(raw_xml_output):
    root = ET.fromstring(raw_xml_output)
    #root = tree.getroot()
    for element in root.findall("./result/formatted_address") :
        output_templat[3] = element.text 

    for element in root.findall("./result/geometry/location") :
        for latlng in element:
            if latlng.tag == 'lat':   
                output_templat[7] = latlng.text
            else:
                output_templat[10]= latlng.text
                
    return "".join(output_templat)

if __name__ == "__main__":
    app.run(debug=True)

# [INPUT FORMAT(google map api data)]
# <?xml version="1.0" encoding="UTF-8"?>
# <GeocodeResponse>
#  ..
#  <result>
#   ...
#   <formatted_address># 3582,13 G Main Road, 4th Cross Rd, HAL 2nd Stage, Doopanahalli, Indiranagar, Bengaluru, Karnataka 560008, India</formatted_address>
#   ...
#   ...
#   <geometry>
#    <location>
#     <lat>12.9652501</lat>
#     <lng>77.6394230</lng>
#    </location>
#       ...
#       ...
#   </geometry>      Reformating
#    ...
#    ...                ||
#  </result>            ||
# </GeocodeResponse>   \\//
#                       \/
# [OUTPU FORMAT]
# <?xml version="1.0" encoding="UTF-8"?>    [Another Way to Look]
# <root>                                || root
#   <address>  some data</address>      ||    address
#   <coordinates>                       ||    coordinates
#       <lat>value 1</lat>              ||         lat
#       <lng>value 2</lng>              ||         lng
#   </coordinates>
# </root>