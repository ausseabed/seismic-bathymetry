# This script is used to import all raster gris into ArcGIS Pro for visualisation
# contact: ulysse.lebrec@uwa.edu.au
import arcpy
import os

#path to folder containing bathy rasters
bathy = r"input_folder_raster"

#path to folder containing Hillshade rasters
hillshade = r"input_folder_hillshade"

# path to empty argis pro project
aprx = arcpy.mp.ArcGISProject(r"Path_to_ArcPro_project.aprx")

# path to empty group layer (you can use the one included in the folder)
st_layer = arcpy.mp.LayerFile(r"path_to_empty_layer.lyr")

m = aprx.listMaps()[0]

for dirs, subdirs, files in os.walk(bathy):
    for fileN in files:
        if fileN.endswith(".tif")and "_HS" not in fileN:
            bathyFile = fileN[:-4]
            #bathyFile = bathyFile[4:]
            print(bathyFile)
            m.addLayer(st_layer, "BOTTOM")
            for lyr in m.listLayers():
                if lyr.name == "survey_type":
                    lyr.name = bathyFile
   
            m.addDataFromPath(os.path.join(dirs,fileN))
            m.addLayerToGroup(m.listLayers(bathyFile)[0], m.listLayers(fileN)[0], "BOTTOM")
            for lyr in m.listLayers(fileN):
                if lyr.longName==fileN:
                    m.removeLayer(lyr)
                    
            for dirs2, subdirs2, files2 in os.walk(hillshade):
                for fileN2 in files2:
                    if fileN2.endswith(".tif")and "_HS" in fileN2:
                        hsFile = fileN2[:-7]
                        
                        #print()
                        if hsFile == bathyFile:
                            print(hsFile)
                            m.addDataFromPath(os.path.join(dirs2,fileN2))
                            m.moveLayer(m.listLayers(fileN)[0], m.listLayers(fileN2)[0],"AFTER")
                            print("file_added")
aprx.save()

