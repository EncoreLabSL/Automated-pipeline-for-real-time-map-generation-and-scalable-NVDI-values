# Automated-pipeline-for-real-time-map-generation-and-scalable-NVDI-values
A pipeline generation to get and process images from Sentinel-2 for a specific ROI (Region of interest) to display and rescale NVDI values

## 1. Content
This asset is provided by the following items:
* Modules: Folder that contains a python script with the function needed for map generation. 
* Plots: Folder that contains some plots from La Rioja, Spain.
* Static: Folder that contains the file index.htlm to display the frontend of the website. 
* Main.py: Python file, the main script that must be run to display the website. 
* Plot.geojson and raster.plk are auxiliar files overwritten when the user interacts with the website. 

## 2. Automated pipeline. An overview of the files
### 2.1. Considerations
These files have been run inside of a server where satellite pictures are uploaded. The user will need to adjust the path for their local environment and download the Sentinel-2 images (in the code loaded from SAFE folder). 

### 2.2. NVDI
Normalized Difference Vegetation Index (NDVI) uses the NIR (Band 8) and red (Band 4) for calculations 
```
NVDI =(NIR-Red)/(NIR+Red)
```
NDVI always ranges from -1 to +1. Healthy vegetation (chlorophyll) reflects more near-infrared (NIR) and green light compared to other wavelengths. But it absorbs more red and blue light. Negative values correspond to water or buildings, values close to +1, means dense green leaves and close to zero, there aren’t green leaves, and it could even be an urbanized area. 
The process followed to calculate NDVI for every plot is:
![image](https://user-images.githubusercontent.com/130968808/232431890-cfbc7cfb-8212-4a57-9ffa-94818504e7d7.png)
An interpolation stage is needed to complete all dates as merging processes need all dates with a numerical value. The dates conversion was made using following fixed dates: 
* Day 2018-04-19 is day_index = 0 
* Day 2022-04-18 is day_index = daysbetween(2022/04/18 - 2018/04/19) = 1460 
Interpolation is made using linear interpolation interp from numpy library.

### 2.3. Plots situation for imaginary selection
Plots included in the asset are selected from vineyard with two grapes variety: 
* Tempranillo: 7 plots (P101, P102, P106, P111, P117, P119, P93), total area: 43.576 m2 
* Garnacha: 4 plots (P110, P109, P223, P81), total area: 84.413 m2 
The situation of these plots is:
![image](https://user-images.githubusercontent.com/130968808/232432128-80e6dc47-2acb-40ff-a221-3f72a94f953e.png)
All coordinates of the region of interest (ROIs) are located in tile 30TWM, as shown in the figure:
![image](https://user-images.githubusercontent.com/130968808/232432181-af800256-99ba-4b44-950f-dbc3cd674efa.png)
The script has been generated with the selection of tiles in SAFE format for 4 years (maximum available) from 2018-04-19 to 2022-04-18, and a cloud percentage limited to 15% and manually checked and chosen. 

### 2.4. Website appearance
Once the browser is loaded (after running main.py), the website will look like this:
![image](https://user-images.githubusercontent.com/130968808/232432304-97bd2572-0161-4273-85ad-ba81fb81faf8.png)
On the left side, there are the following items to interact:
* Plot section: it allows to load a geojson file, available in /plots/geojson/
* Date: a selector to choose the date for the NVDI calculation. 
* NVDI scroll bars: these scroll bars allows to manually adjust the minimum and maximum NVDI value from 0 to 1.
On the right side, the user will visualize the map for the crop defined on the geojson filled by the NVID scale.

### 2.5. More information
On the file uploaded Pipeline_Aditional_Asset_Information.pdf you will find more information, such as, an example of the website interaction and some brief explanation of the backend and frontend scripts.
