from geopy.geocoders import Nominatim
import json

geolocator = Nominatim()


#This function locates the place names in the txt file and generates a json file
#containing a dictionary with the coordinates, county and place name.
#It only requires the name of the disease, provided that the hospitals_'disease'.txt exists.

def generate_hospitals(disease):
    data = []
    f = open('./Hospitals/hospitals_'+disease+'.txt','r')
    for line in f:
        location=geolocator.geocode(line)
        if location:
            lat, lon = location.latitude, location.longitude
            address = location.address.strip('/n').split(', ')
            country = address[-1]
            data.append({'lat': lat, 'lon': lon, 'name': line, 'country': country})
        else:
            print('could not find '+line)
    with open('./ProcessedData/hospitals_information_'+disease+'.json', 'w', encoding='utf-8') as h:
        json.dump(data, h, ensure_ascii=False, indent=4)

generate_hospitals('melanoma')
