# Reading satellite imagery
import rasterio as rio
from rasterio.mask import mask
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject


# General utilities
from datetime import  datetime
import glob
from pathlib import Path
import numpy as np
import geopandas as gpd
import pickle
# List of safe
from safe.safe_list import safe_list


DATES_BEGIN = datetime(2018, 4, 19)
DATES_END = datetime(2022, 4, 18)


def crop_rasters(filenames, aoi, nodata, output_path, label, nd=65535):
    """Crop a list of rasters based on a AOI and save the outputs."""
    output_files = []
    
    for f in filenames:
        with rio.open(f) as raster:
            
            # Get crs from profile and convert input aoi
            profile = raster.profile
            crop_bound = aoi.to_crs(profile["crs"])

            # Mask raster
            out_img, out_transform = mask(raster, shapes=crop_bound, crop=True, nodata=nd)

            # Save raster
            output_files.append(Path(f"{output_path}/{Path(f).stem}_{label}_crop.tiff"))
            write_raster(Path(f"{output_path}/{Path(f).stem}_{label}_crop.tiff"), out_img[0, :, :], profile["crs"],
                         out_transform, nd, driver='GTiff')

    return output_files  

def mosaic_rasters(filenames):
    """Mosaic several rasters."""
    to_mosaic = []
    crs = []
    nodata = []
    
    for file in filenames:
        src = rio.open(file, masked=True)
        nodata.append(src.nodata)
        to_mosaic.append(src)
        crs.append(src.profile["crs"])
        
    mosaic, transform = merge(to_mosaic)
    
    if not all(x==crs[0] for x in crs):
        raise ValueError("Not all files in the same projection!")
        
    if not all(x==nodata[0] for x in nodata):
        raise ValueError("Not all file have the same nodata mask!")
               
    return np.where(mosaic==nodata[0], np.nan, mosaic), transform, crs[0]

def write_raster(path, raster, crs, transform, nodata, driver='GTiff'):
    """Write a raster to a file."""
    
    with rio.open(path, 'w', driver=driver, height=raster.shape[0], width=raster.shape[1],
                       count=1, dtype=raster.dtype, crs=crs, transform=transform, nodata=nodata) as dst:
        dst.write(raster, 1)
        
def reproject_raster(inpath, outpath, crs, method="nearest"):
    "Reproject a raster to a new coordinate system."
    
    dst_crs = f'EPSG:{crs}'
    
    with rio.open(inpath) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        
        with rio.open(outpath, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rio.band(src, i),
                    destination=rio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=rio_resample(method))
                
def rio_resample(method):
    """Return a rasterio resampling method based on a string."""
    
    resampling_methods = {"nearest": rio.enums.Resampling.nearest,
                          "bilinear": rio.enums.Resampling.nearest,
                          "cubic": rio.enums.Resampling.nearest,
                          "cubic_spline": rio.enums.Resampling.cubic_spline,
                          "lanczos": rio.enums.Resampling.lanczos,
                          "average": rio.enums.Resampling.average,
                          "mode": rio.enums.Resampling.mode,
                          "gauss": rio.enums.Resampling.gauss,
                          "max": rio.enums.Resampling.max,
                          "min": rio.enums.Resampling.min,
                          "med": rio.enums.Resampling.med,
                          "q1": rio.enums.Resampling.q1,
                          "q3": rio.enums.Resampling.q3,
                          "sum": rio.enums.Resampling.sum,
                          "rms": rio.enums.Resampling.rms,
                         }
    
    if method not in resampling_methods:
        raise ValueError("Wrong resampling method selected."
                         " See: https://rasterio.readthedocs.io/en/latest/api/rasterio.enums."
                         "html#rasterio.enums.Resampling")
    
    return resampling_methods[method]

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'same') / w


def render_map(geojson: str, fecha: str, ndvi_min: float=0.0, ndvi_max: float=1.0) -> Path:
    """
    Returns 
    """

    ndvi_min = float(ndvi_min)
    ndvi_max = float(ndvi_max)
    with open('plot.geojson', 'wt') as h:
        h.write(geojson)
    plot = 'plot.geojson'
    plot_name = 'plotfromweb'
    
    fechas = []
    safes = []
    for safe in safe_list:
        year = safe.split('_')[2][0:4]
        month = safe.split('_')[2][4:6]
        day = safe.split('_')[2][6:8]
        #print(f"EODATA_BASE_PATH/{year}/{month}/{day}/{safe}/**/*B0[2-3-4-8]_10m.jp2")
        fechas.append(f"{year}/{month}/{day}")
        safes.append(safe)

    # sort fechas and safes together
    sorted_index = np.array(fechas).argsort()
    fechas = np.array(fechas)[sorted_index]
    safes = np.array(safes)[sorted_index]

    # get the closest date from 'fecha'.
    indice = np.flatnonzero(np.where(fechas < fecha, 0, 1))[0] - 1
    fecha = fechas[indice]
    
    EODATA_BASE_PATH = "/eodata/Sentinel-2/MSI/L2A"
    bands = []
    bands.extend(glob.glob(f"{EODATA_BASE_PATH}/{fechas[indice]}/{safes[indice]}/GRANULE/**/*B0[4-8]_10m.jp2", recursive=True))
   
    ## Extraccion de NDVI
    bands_B04 = [x for x in bands if "B04" in x]
    bands_B08 = [x for x in bands if "B08" in x]
    roi = gpd.read_file(plot)

    cropped_B04 = crop_rasters(bands_B04, roi.geometry, 65535, "./data/cropped", plot_name)
    cropped_B08 = crop_rasters(bands_B08, roi.geometry, 65535, "./data/cropped", plot_name)

    mosaic_B04, trans_B04, crs_B04 = mosaic_rasters(cropped_B04)
    mosaic_B08, trans_B08, crs_B08 = mosaic_rasters(cropped_B08)
    ndvi_original = (mosaic_B08 - mosaic_B04) / (mosaic_B08 + mosaic_B04)

    with open(Path(f"data/processed/ndvi_Grass_data.pickle"), 'rb') as handler:
        grass_data = pickle.load(handler)

    td = (datetime.strptime(fecha, "%Y/%m/%d") - DATES_BEGIN).days
    grass_data_mean = np.roll(moving_average(np.nanmean(grass_data, axis=(1, 2)), 25), 109)
    lane_compensation = grass_data_mean[td]

    ndvi = ndvi_original - lane_compensation
    ndvi[ndvi < 0] = 0

    fecha = fecha.replace("/", "-")
    ndvi_path = f"./data/viz_raster/NDVI_{fecha}_{plot_name}.tif"
    write_raster(ndvi_path, (ndvi[0,:,:] - ndvi_min) / (ndvi_max - ndvi_min), crs_B04, trans_B04, 0)
    reproject_raster(ndvi_path, f"{ndvi_path}_4326.tif", 4326, method="nearest")
    ndvi_4326 = rio.open(f"{ndvi_path}_4326.tif")
    bounds=[[ndvi_4326.bounds.bottom, ndvi_4326.bounds.left], 
            [ndvi_4326.bounds.top, ndvi_4326.bounds.right]],
    image=ndvi_4326.read(1)
    with open("raster.pkl", "wb") as h:
        pickle.dump([image, bounds], h)
