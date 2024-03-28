from flask import Flask, request, render_template, redirect, url_for
import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from shapely.geometry import mapping
from shapely.geometry import Polygon
import pickle

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Load NDVI and SMI model
with open('ndvi_smi.pkl', 'rb') as file:
    ndvi_model, smi_model = pickle.load(file)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file uploads
        red_band = request.files['red_band']
        nir_band = request.files['nir_band']
        swir_band = request.files['swir_band']

        # Save uploaded files
        red_band_path = 'uploads/red_band.jp2'
        nir_band_path = 'uploads/nir_band.jp2'
        swir_band_path = 'uploads/swir_band.jp2'

        red_band.save(red_band_path)
        nir_band.save(nir_band_path)
        swir_band.save(swir_band_path)

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

        # Render the results page
        return render_template('results.html', ndvi=ndvi.tolist(), smi=smi.tolist())

    return render_template('upload.html')

def calculate_ndvi(red_band, nir_band):
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    # Clip NDVI values to the valid range of -1.0 to 1.0
    return np.clip(ndvi, -1.0, 1.0)

def calculate_smi(swir_band, nir_band):
    smi = (nir_band - swir_band) / (nir_band + swir_band)
    # Clip SMI values to the valid range of 0.0 to 1.0
    return np.clip(smi, 0.0, 1.0)

if __name__ == '__main__':
    app.run(debug=True)
