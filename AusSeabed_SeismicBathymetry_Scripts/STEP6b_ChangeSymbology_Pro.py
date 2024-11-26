# This script is used to appli symbologies to all layers in ArcGIS Pro
# contact: ulysse.lebrec@uwa.edu.au
import arcpy
import os

# Path to arcgis pro project
aprx = arcpy.mp.ArcGISProject(r"path_to_arcPro_project.aprx")
m = aprx.listMaps()[0]

# Path to the bathymetry symbology layer - you can create a symbology
# layer file by opening your arcgis pro project, set the symbology of a
# layer as you want it to be, then go to "share" and export as layer
# file. Use the path of the layer file. make sure the bathymetry has 40%
# transparency
inputLayer1 = r"path_to_symbology_layer.lyrx"
# Path to the hillshade symbology layer. same as above, no transparency
inputLayer2 = r"path_to_symbology_layer.lyrx"

for lyr in m.listLayers():
    if lyr.isRasterLayer == True:
        print(lyr.name)
        if "HS" in lyr.name:
            arcpy.management.ApplySymbologyFromLayer(lyr, inputLayer2)
        else:
            arcpy.management.ApplySymbologyFromLayer(lyr, inputLayer1,"","MAINTAIN")
aprx.save()
