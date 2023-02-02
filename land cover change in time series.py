Python 3.10.4 (tags/v3.10.4:9d38120, Mar 23 2022, 23:13:41) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import ee
import folium
import pandas as pd
import os

ee.Initialize()

# create a list of product ID
# in this case, we are going to use sentinel 2
product_list = ['COPERNICUS/S2/', 'COPERNICUS/S2_SR/']

# ID of the area/region that you want to monitor
polygon = ee.Geometry.Polygon([[
[103.65606689453125, 1.3775722351169123], 
[103.8262939453125, 1.3775722351169123], 
[103.8262939453125, 1.4182142725652363], 
[103.65606689453125, 1.4182142725652363], 
[103.65606689453125, 1.3775722351169123]]])

# list of date for the time series
start_date = ['2018-01-01', '2018-02-01', '2018-03-01', '2018-04-01', '2018-05-01', '2018-06-01', '2018-07-01', '2018-08-01', '2018-09-01', '2018-10-01', '2018-11-01', '2018-12-01']
end_date = ['2018-01-31', '2018-02-28', '2018-03-31', '2018-04-30', '2018-05-31', '2018-06-30', '2018-07-31', '2018-08-31', '2018-09-30', '2018-10-31', '2018-11-30', '2018-12-31']

total_data = []

for i in range(len(product_list)):
    for j in range(len(start_date)):
        # define the collection
        img_col = ee.ImageCollection(product_list[i])

        # filter the collection based on the date
        img_col_date = img_col.filterDate(start_date[j], end_date[j])

        # filter the collection based on the area
        img_col_date_area = img_col_date.filterBounds(polygon)

        # convert the collection into single image
        img = img_col_date_area.median()

        # create a dictionary object to store the results
        data = {}

        # get the data and store into the dictionary
        data['name'] = product_list[i]
        data['start_date'] = start_date[j]
        data['end_date'] = end_date[j]
        data['total_image'] = img_col_date_area.size().getInfo()
        data['ndvi'] = img.normalizedDifference(['B8', 'B4']).rename('ndvi').getInfo()
        data['ndwi'] = img.normalizedDifference(['B3', 'B8']).rename('ndwi').getInfo()
        data['evi'] = img.expression('2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
        'NIR': img.select('B8'),
        'RED': img.select('B4'),
        'BLUE': img.select('B2')}).rename('evi').getInfo()
        data['ndbi'] = img.normalizedDifference(['B11', 'B8']).rename('ndbi').getInfo()
        data['ndsi'] = img.normalizedDifference(['B3', 'B11']).rename('ndsi').getInfo()
        data['coastal'] = img.select('B2').rename('coastal').getInfo()

        # append the dictionary to the list
        total_data.append(data)

# write the results into csv file
df = pd.DataFrame(total_data)
df.to_csv('data_output.csv')