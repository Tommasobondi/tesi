#IMPORT (see i_before code)

import sentinelsat
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import numpy as np
import geojson    
import pandas as pd
from area import area
from geojson import Polygon
import sys
import pyunpack
import os
import zipfile
from pathlib import Path
from osgeo import gdal
from osgeo import ogr
from subprocess import run
#from fmask.cmdline import sentinel2Stacked
from s2cloudless import S2PixelCloudDetector
#from src import parser
import rasterio
from rasterio.warp import reproject, Resampling
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image



#SET THE WD

#theWD = 'C:\\Temp\\Sentinel'  #mywduni
#theWD = 'C:\\Temp\\Sentinel'  #kont
theWD = 'C:\\Users\\tommaso\\Desktop\\tesi\\Sentinel'  #mywdpc

theDownloadFolder = theWD + "\\Download"
if os.path.isdir(theDownloadFolder) == False: os.mkdir(theDownloadFolder)
#SET AOI AND GEOJ FILE

Xmax = 462000
Ymax = 4333000

Xmin = 459500
Ymin = 4330500

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

#alternative methods
'''
VectorDriver = ogr.GetDriverByName('ESRI Shapefile') #intialize vector
VectorDataset = VectorDriver.Open("boxes.shp", 1) 
layer = VectorDataset.GetLayer()
feature=layer[0] #select the first polygon (the circle shown in image)
geom = feature.GetGeometryRef() 
minX, maxX, minY, maxY = geom.GetEnvelope()
'''


#DOWNLOAD PRODUCTS

api = SentinelAPI('tommasobondi', 'francedo03!', 'https://scihub.copernicus.eu/dhus')  #mydata to accede
footprint = geojson_to_wkt(read_geojson(theWD + '\AOI.json'))

theDownloadFolder = theWD + "\\Download"
if os.path.isdir(theDownloadFolder) == False: os.mkdir(theDownloadFolder)
#download, check existing, try download offline and download online

#years = pd.Series(range(2017,2021)) #insert start and end year
years = [2022] #for puntual year
print(years)

directory_path = ''

for iyears in years:
    products=api.query(footprint,
        date=('%04.4d0828'%(iyears),'%04.4d0920'%(iyears)),  #date 
        platformname='Sentinel-2',      #platform
        cloudcoverpercentage=(0, 99),    #first cloud mask
        producttype='S2MSI1C')        #prodoucttype

    print("Passed")

    products_df = api.to_dataframe(products)
    count = products_df.shape[0] 
    print('For the year %04.4d, %02.2d imagines were found.'%(iyears,count))
    products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True]) 

    for i in range(0, len(products_df_sorted)):
        ExistBoolean = False
        for item in os.listdir(theWD + "\\Download"):
            ExistBoolean == False
            if os.path.isdir(theWD + "\\Download\\" + item):
                if products_df_sorted.iloc[i]['title'] == item[:-5]:
                    print(products_df_sorted['filename'].values[0]," already exists. Skipping")
                    ExistBoolean == True
                    break

        if ExistBoolean == False:
 
            print("DOWNLOAD")
            ifil = products_df_sorted.index[i]
            product_info = api.get_product_odata(ifil)

                          
            if product_info['Online']: 
                  print('Product {} is online. Starting download.'.format(ifil))
                  api.download(ifil, theWD + "\\Download", checksum=True)
            else:
                  print('Product {} is not online. Please try again later.'.format(ifil))
                  try:
                       api.download(ifil, theWD + "\\Download", checksum=True)
                  except:
                       pass            
                



#oldmethod, not so functonal if not previous download file
'''   
    for root, dirs, files in os.walk(theWD + "\\Download"):
        for SAFEdirsname in dirs:

            if SAFEdirsname.endswith(".SAFE"):
                  print(products_df_sorted['filename'].values[0]," already exists. Skipping")
            else:
                for steps in range(count):

                    if os.path.exists(products_df_sorted['filename'].values[0].replace('SAFE','zip')):                          
                          print(products_df_sorted['filename'].values[0]," already exists. Skipping")
                          continue
                    ifil = products_df_sorted.index[steps]
                    product_info = api.get_product_odata(ifil)              
                    if product_info['Online']: 
                          print('Product {} is online. Starting download.'.format(ifil))
                          api.download(ifil, theWD + "\\Download", checksum=True)
                    else:
                          print('Product {} is not online. Please try again later.'.format(ifil))
                          try:
                               api.download(ifil, theWD + "\\Download", checksum=True)
                          except:
                               pass
                print('\n\n')
'''
#avoid recall if offline
'''
    product_info = api.get_product_odata("products")
    is_online = product_info['Online']

    is_online = api.is_online("product_id")

    if is_online:
        print(f'Product {<product_id>} is online. Starting download.')
        api.download(<product_id>)
    else:
        print(f'Product {product_id>} is not online.')
        api.trigger_offline_retrieval(<product_id>)
    sys.exit()
'''

#or old method, ok if all is online and ready
'''
directory_path = ''

products = api.query(footprint,
                       date=('ymd', 'ymd'),  #date----this date download 2
                       platformname='Sentinel-2',      #platform
                       cloudcoverpercentage=(0, 20),    #first cloud mask
                       producttype='S2MSI1C')        #prodoucttype

api.download_all(products, theWD)
'''


#EXCTRACT TO .SAFE FILE, CUT AOI ANDE SAVE TO IMAGES FOLDER

for root, dirs, files in os.walk(theWD + "\\Download"):
    for ZIPfilename in files:
        if ZIPfilename.endswith(".rar") :
            print('RAR:'+os.path.join(root,ZIPfilename))
        elif ZIPfilename.endswith(".zip"):
            print('ZIP:'+os.path.join(root,ZIPfilename))
        name = os.path.splitext(os.path.basename(ZIPfilename))[0]
        if ZIPfilename.endswith(".rar") or ZIPfilename.endswith(".zip"):

            arch = pyunpack.Archive(os.path.join(root,ZIPfilename))
            arch.extractall(directory=root)


            theExtractedImagesPath = ZIPfilename.replace(".zip", ".SAFE") + "\\GRANULE\\"
            theImageName = os.listdir(theWD + "\\Download\\" + theExtractedImagesPath)[0]
            theExtractedQIPath = theExtractedImagesPath + theImageName + "\\QI_DATA\\"
            theExtractedImagesPath = theExtractedImagesPath + theImageName + "\\IMG_DATA\\"
            
            
            #theExtractedImagesPath = theWD + "\\" + theExtractedQIPath
            theDate = theExtractedImagesPath[11:19]

            theImagesFolder = theWD + "\\Images"
            if os.path.isdir(theImagesFolder) == False: os.mkdir(theImagesFolder)
            
            theOutputFolder = theWD + "\\Images\\" + str(theDate[-2:]) + str(theDate[5:7]) + str(theDate[:-4])
            if os.path.isdir(theOutputFolder) == False: os.mkdir(theOutputFolder)

        
            for Imagefilename in os.listdir(theWD + "\\Download\\" + theExtractedImagesPath):
                if Imagefilename.endswith(".jp2") : 
                    print(Imagefilename)
                    #Clip Raster Image and Savce iside Sentinel/Images/Date
                    raster = gdal.Open(theWD + "\\Download\\" + theExtractedImagesPath + Imagefilename, gdal.GA_ReadOnly) #read raster
                    dataraster = raster.ReadAsArray().astype(float)


                    projection = raster.GetProjectionRef()
                    geot = raster.GetGeoTransform()
                    ulx, xres, xskew, uly, yskew, yres  = raster.GetGeoTransform()


                    for cloudfilename in os.listdir(theWD + "\\Download\\" + theExtractedQIPath):
                    
                        if not cloudfilename.endswith(".gml") :

                            continue

                        input_folder = theWD + "\\Download\\" + theExtractedImagesPath
                        save_to = theOutputFolder
                        identifier=""
                        for filename in os.listdir(input_folder):
                            if("B01.jp2" in filename):
                                identifier=filename.split("B01")[0]
                                
                        def plot_cloud_mask(mask, figsize=(15, 15), fig=None):
                            
                            im_result = Image.fromarray(np.uint8(mask)) #uint8 #float32
                            im_result.save(os.path.join(save_to,"MSK_CLOUDS_B00.png"))  #png

                        def plot_probability_map(prob_map, figsize=(15, 15)):
                           
                            im_result = Image.fromarray(np.uint8(prob_map * 255)) #uint8 #float32
                            im_result.save(os.path.join(save_to,"MSK_CLOUDS_PROB_B00.png"))  #png #tif    

                        #Resampling to achieve 60 m resolution:

                        with rasterio.open(os.path.join(input_folder,identifier+"B01.jp2")) as dataset:
                            B01 = dataset.read(out_shape=(dataset.count,int(dataset.height * 1),int(dataset.width * 1)),resampling=Resampling.bilinear)                  
                            print(B01.shape)

                        with rasterio.open(os.path.join(input_folder,identifier+"B02.jp2")) as dataset:
                            B02 = dataset.read(out_shape=(dataset.count,int(dataset.height // 6),int(dataset.width // 6)),resampling=Resampling.bilinear)
                            print(B02.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B04.jp2")) as dataset:
                            B04 = dataset.read(out_shape=(dataset.count,int(dataset.height // 6),int(dataset.width // 6)),resampling=Resampling.bilinear)
                            print(B04.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B05.jp2")) as dataset:
                            B05 = dataset.read(out_shape=(dataset.count,int(dataset.height // 3),int(dataset.width // 3)),resampling=Resampling.bilinear)
                            print(B05.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B08.jp2")) as dataset:
                            B08 = dataset.read(out_shape=(dataset.count,int(dataset.height // 6),int(dataset.width // 6)),resampling=Resampling.bilinear)
                            print(B08.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B8A.jp2")) as dataset:
                            B8A = dataset.read(out_shape=(dataset.count,int(dataset.height // 3),int(dataset.width // 3)),resampling=Resampling.bilinear)
                            print(B8A.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B09.jp2")) as dataset:
                            B09 = dataset.read(out_shape=(dataset.count,int(dataset.height * 1),int(dataset.width * 1)),resampling=Resampling.bilinear)
                            print(B09.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B10.jp2")) as dataset:
                            B10 = dataset.read(out_shape=(dataset.count,int(dataset.height * 1),int(dataset.width * 1)),resampling=Resampling.bilinear)
                            print(B10.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B11.jp2")) as dataset:
                            B11 = dataset.read(out_shape=(dataset.count,int(dataset.height // 3),int(dataset.width // 3)),resampling=Resampling.bilinear)
                            print(B11.shape)
                            
                        with rasterio.open(os.path.join(input_folder,identifier+"B12.jp2")) as dataset:
                            B12 = dataset.read(out_shape=(dataset.count,int(dataset.height // 3),int(dataset.width // 3)),resampling=Resampling.bilinear)
                            print(B12.shape)
                        bands = np.array([np.dstack((B01[0]/10000.0,B02[0]/10000.0,B04[0]/10000.0,B05[0]/10000.0,B08[0]/10000.0,B8A[0]/10000.0,B09[0]/10000.0,B10[0]/10000.0,B11[0]/10000.0,B12[0]/10000.0))])

                        #Recommended parameters for 60 m resolution: average_over = 4, dilation_size=2
                        #Recommended parameters for 10 m resolution: average_over=22, dilation_size=11

                        cloud_detector = S2PixelCloudDetector(threshold=0.4, all_bands=False, average_over=4, dilation_size=2)  
                        cloud_probs = cloud_detector.get_cloud_probability_maps(bands)
                        mask = cloud_detector.get_cloud_masks(bands).astype(rasterio.uint8) #uint8

                        plot_cloud_mask(mask[0])
                        plot_probability_map(cloud_probs[0])

                        driver_cloud = ogr.GetDriverByName('PNG')
                        cloud_ds = driver_cloud.Open(theOutputFolder + 'MSK_CLOUDS_B00.png')
                        lyr = cloud_ds.GetLayer()
                        drv = ogr.GetDriverByName( 'ESRI Shapefile' )

                        drv_tiff = gdal.GetDriverByName("GTiff") 
                        cloud_img = drv_tiff.Create(theOutputFolder + "\\Cloud_" + str(Imagefilename[23:26] + ".tif"), raster.RasterXSize, raster.RasterYSize, 1, gdal.GDT_Float32)
                        cloud_img.SetGeoTransform(geot)
                        gdal.RasterizeLayer(cloud_img, [1], lyr)
                        cloud_img.GetRasterBand(1).SetNoDataValue(0)
                        datacloud = cloud_img.ReadAsArray().astype(np.float)
                        
                        cloud_img = None

                        out = np.where(datacloud == 0, dataraster, -9999)
                        out_ds = drv_tiff.Create(theOutputFolder + "\\Mask_" + str(Imagefilename[23:26] + ".tif"), raster.RasterXSize, raster.RasterYSize, 1, gdal.GDT_Float32)
                        out_ds.SetProjection(projection)
                        out_ds.SetGeoTransform(geot)
                        out_ds.GetRasterBand(1).WriteArray(out)
                        out_ds.GetRasterBand(1).FlushCache()
                            
                            
                        OutTile = gdal.Warp(theOutputFolder + "\\Band_" + str(Imagefilename[23:26] + ".tif"), out_ds, format='GTiff', outputBounds=[Xmin, Ymin, Xmax, Ymax],xRes=xres,yRes=xres,dstSRS=projection)
                        out_ds = None    

                        if cloudfilename.endswith(".gml") :

                            continue

                        driver_cloud = ogr.GetDriverByName('GML')
                        cloud_ds = driver_cloud.Open(theWD + "\\Download\\" + theExtractedQIPath + 'MSK_CLOUDS_B00.gml')
                        lyr = cloud_ds.GetLayer()
                        drv = ogr.GetDriverByName( 'ESRI Shapefile' )

                        drv_tiff = gdal.GetDriverByName("GTiff") 
                        cloud_img = drv_tiff.Create(theOutputFolder + "\\Cloud_" + str(Imagefilename[23:26] + ".tif"), raster.RasterXSize, raster.RasterYSize, 1, gdal.GDT_Float32)
                        cloud_img.SetGeoTransform(geot)
                        gdal.RasterizeLayer(cloud_img, [1], lyr)
                        cloud_img.GetRasterBand(1).SetNoDataValue(0)
                        datacloud = cloud_img.ReadAsArray().astype(np.float)
                        
                        cloud_img = None

                        out = np.where(datacloud == 0, dataraster, -9999)
                        out_ds = drv_tiff.Create(theOutputFolder + "\\Mask_" + str(Imagefilename[23:26] + ".tif"), raster.RasterXSize, raster.RasterYSize, 1, gdal.GDT_Float32)
                        out_ds.SetProjection(projection)
                        out_ds.SetGeoTransform(geot)
                        out_ds.GetRasterBand(1).WriteArray(out)
                        out_ds.GetRasterBand(1).FlushCache()
                            
                            
                        OutTile = gdal.Warp(theOutputFolder + "\\Band_" + str(Imagefilename[23:26] + ".tif"), out_ds, format='GTiff', outputBounds=[Xmin, Ymin, Xmax, Ymax],xRes=xres,yRes=xres,dstSRS=projection)
                        out_ds = None
                        
                        
                else:
                    os.remove(os.path.join(root,ZIPfilename))

sys.exit()

