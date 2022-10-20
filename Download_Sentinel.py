import sentinelsat
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

import geojson    
import pandas as pd
#from area import area
from geojson import Polygon
import sys
import pyunpack
import os
import zipfile

theWD = 'C:\\Users\\geom21020\\Desktop\\Sentinel'  #mywd

#intrest area coordinates
#build the geojson file

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

#download immagines


api = SentinelAPI('tommasobondi', 'francedo03!', 'https://scihub.copernicus.eu/dhus')  #mydata to accede
footprint = geojson_to_wkt(read_geojson(theWD + '\AOI.json'))

directory_path = ''

products = api.query(footprint,
                       date=('20211103', '20211120'),  #date
                       platformname='Sentinel-2',      #platform
                       cloudcoverpercentage=(0, 20),    #first cloud mask
                       producttype='S2MSI1C')        #prodoucttype



api.download_all(products, theWD)

#extract and delete the compressed


basis_folder =  r (theWD)

for root, dirs, files in os.walk(basis_folder):
    for filename in files:
        if filename.endswith(".rar") :
            print('RAR:'+os.path.join(root,filename))
        elif filename.endswith(".zip"):
            print('ZIP:'+os.path.join(root,filename))
        name = os.path.splitext(os.path.basename(filename))[0]
        if filename.endswith(".rar") or filename.endswith(".zip"):
            try:
                arch = pyunpack.Archive(os.path.join(root,filename))
                # os.mkdir(name)
                arch.extractall(directory=root)
                os.remove(os.path.join(root,filename))
            except Exception as e:
                print("ERROR: BAD ARCHIVE "+os.path.join(root,filename))
                print(e)
                try:
                    pass
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise 
