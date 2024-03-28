# Importing all necessary libraries
import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio       
import geopandas as gpd
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from shapely.geometry import mapping
from shapely.geometry import Polygon
import pickle

# Sentinel Hub credentials
username = 'yuvashree99'
password = 'Yuvan@2706'

# Connecting to the Sentinel Hub API
api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

# Defining the area of interest (AOI) as a GeoJSON string
aoi_geojson = {
    "type": "Polygon",
    "coordinates": [
        [
            [77.09627763799867, 8.293476270779884],
            [76.23538330651085, 11.572755944235755],
            [80.2667261298167, 13.564116537881423],
            [77.55105636567383, 8.077930655251784],  
            [77.09627763799867, 8.293476270779884] # the last point is the same as the first point 
        ]
    ]
}

# Output folder where downloaded data will be saved
output_folder = r'D:\Users\UVA\Tamilnadu'

# Searching for available Sentinel-2 products within the AOI
footprint = geojson_to_wkt(aoi_geojson)
# Start and end dates in the format 'YYYYMMDD'
start_date = '20230101'
end_date = '20231008'

# Searching for available Sentinel-2 products within the AOI with the correct date range
products = api.query(footprint, date=(start_date, end_date), platformname='Sentinel-2', cloudcoverpercentage=(0, 3))

# To download the most recent product
latest_product_id = max(products, key=lambda k: products[k]['beginposition'])
api.download(latest_product_id, output_folder)


# Functions for NDVI and SMI calculation
def calculate_ndvi(red_band, nir_band):
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    # Clip NDVI values to the valid range of -1.0 to 1.0
    return np.clip(ndvi, -1.0, 1.0)

def calculate_smi(swir_band, nir_band):
    smi = (nir_band - swir_band) / (nir_band + swir_band)
    # Clip SMI values to the valid range of 0.0 to 1.0
    return np.clip(smi, 0.0, 1.0)


# Defining file paths with raw strings
red_band_path = r'C:/Users/Ashwini/Desktop/S2A_MSIL2A_20230413T050651_N0509_R019_T43PGM_20230413T102555/S2A_MSIL2A_20230413T050651_N0509_R019_T43PGM_20230413T102555.SAFE/GRANULE/L2A_T43PGM_A040771_20230413T052406/IMG_DATA/R20m/T43PGM_20230413T050651_B04_20m.jp2'
nir_band_path = r'C:/Users/Ashwini/Desktop/S2A_MSIL2A_20230413T050651_N0509_R019_T43PGM_20230413T102555/S2A_MSIL2A_20230413T050651_N0509_R019_T43PGM_20230413T102555.SAFE/GRANULE/L2A_T43PGM_A040771_20230413T052406/IMG_DATA/R20m/T43PGM_20230413T050651_B8A_20m.jp2'
swir_band_path = r'C:/Users/Ashwini/Desktop/S2A_MSIL2A_20230413T050651_N0509_R019_T43PGM_20230413T102555/S2A_MSIL2A_20230413T050651_N0509_R019_T43PGM_20230413T102555.SAFE/GRANULE/L2A_T43PGM_A040771_20230413T052406/IMG_DATA/R20m/T43PGM_20230413T050651_B11_20m.jp2'


# Open files using rasterio.open
with rasterio.open(red_band_path) as red_band, \
     rasterio.open(nir_band_path) as nir_band, \
     rasterio.open(swir_band_path) as swir_band:
    # Read the pixel data from the opened files
    red = red_band.read(1)
    nir = nir_band.read(1)
    swir = swir_band.read(1)
    ndvi = calculate_ndvi(red, nir)
    smi = calculate_smi(swir, nir)
    
#Dumping NDVI and SMI model to a file using pickle    
with open('ndvi_smi.pkl', 'wb') as file:
    pickle.dump((ndvi, smi), file)
    
os.getcwd()

# Step to Check if the minimum and maximum values are within the expected range
min_ndvi = np.nanmin(ndvi)
max_ndvi = np.nanmax(ndvi)

if min_ndvi >= -1.0 and max_ndvi <= 1.0:
    print(f"NDVI values are within the expected range: Min={min_ndvi}, Max={max_ndvi}")
else:
    print(f"NDVI values were outside the expected range and have been clipped: Min={min_ndvi}, Max={max_ndvi}")


min_smi = np.nanmin(smi)
max_smi = np.nanmax(smi)

if min_smi >= 0 and max_smi <= 1.0:
    print(f"SMI values are within the expected range: Min={min_smi}, Max={max_smi}")
else:
    print(f"SMI values were outside the expected range and have been clipped: Min={min_smi}, Max={max_smi}")


# Plotting NDVI and SMI heatmaps using Matplotlib listed color map
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Defining custom color maps
ndvi_cmap = ListedColormap(['yellow', 'green', 'darkgreen'])
smi_cmap = ListedColormap(['yellow', 'orange', 'darkred'])

# Create=ing subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Displaying NDVI heatmap with custom colormap
im1 = ax1.imshow(ndvi, cmap=ndvi_cmap)
ax1.set_title('NDVI Heatmap')

# Displaying SMI heatmap with custom colormap
im2 = ax2.imshow(smi, cmap=smi_cmap)
ax2.set_title('SMI Heatmap')

# Adding colorbars
cbar1 = fig.colorbar(im1, ax=ax1)
cbar1.set_label('NDVI')
cbar2 = fig.colorbar(im2, ax=ax2)
cbar2.set_label('SMI')

plt.show()


#Creating heat maps and converting maps into analytic/Bar Graph
ndvi_mean = np.nanmean(ndvi)
smi_mean = np.nanmean(smi)

# Create a bar chart
categories = ['NDVI', 'SMI']
values = [ndvi_mean, smi_mean]

plt.bar(categories, values)
plt.xlabel('Category')
plt.ylabel('Mean Value')
plt.title('Mean NDVI and SMI')
plt.show()