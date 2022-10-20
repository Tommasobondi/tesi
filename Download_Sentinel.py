import sentinelsat
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date


import geojson    
import pandas as pd
#from area import area
from geojson import Polygon
import sys


theWD = 'C:'\Users\geom21020\Desktop\Sentinel\\'

Xman = 26.55345
Ymax = 39.14115

Xmin = 26.53545
Ymin = 39.12395

d = {'X': [26.53545, 26.55345, 26.55345, 26.53545], 'Y': [39.12395, 39.12395, 39.14115, 39.14115]}
df = pd.DataFrame(data=d)

long_coords = df['X'].tolist()
lat_coords = df['Y'].tolist()

data = []
for i in range(0, len(long_coords)):
    data.append( tuple([long_coords[i],lat_coords[i]]) )

data.append(data[0])

print("Total GPS Coordinates: {}".format(len(data)))

obj = Polygon([data])  
    
f = open(theWD + "\AOI.json", "w")
f.write(str(obj))
f.close()




api = SentinelAPI('tommasobondi', 'francedo03!', 'https://scihub.copernicus.eu/dhus') #mypassandusername
footprint = geojson_to_wkt(read_geojson(theWD + '\AOI.json')) #my directory, file created with qgis, creating a polygon and extracting the shapefine in geojson

directory_path = ''

products = api.query(footprint,
                       date=('20211010', '20211020'), #+-, don't look so mutch but the amount is still and the pc block
                       platformname='Sentinel-2',
                       cloudcoverpercentage=(0, 20),
                       producttype='S2MSI1C') #ortheconvenient one, but it depends if the percentege is of the file or the area
                       #prodouctlevel='Level-1C' (alreadyeleborated one)



api.download_all(products, directory_path)
