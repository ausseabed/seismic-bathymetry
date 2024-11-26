# This script is used to generate hillshades
# contact: ulysse.lebrec@uwa.edu.au

import arcpy
import os

target = r"input_folder"
output = r"output_folder"

z_factor = 0.00001171

if arcpy.CheckExtension("3D")=="Available":    
        arcpy.CheckOutExtension("3D")
else:
        print("3D Extension not available")
if arcpy.CheckExtension("Spatial")=="Available":
        arcpy.CheckOutExtension("Spatial")
else:
        print("Spatial extension not available")
        
for dirs, subdirs, files in os.walk(target):
        for fileN in files:
            if fileN.endswith(".tif"):
                print(fileN)
                Bathy = os.path.join(target,fileN)
                Hillshade = os.path.join(output,fileN[:-4] + "_HS.tif")              
                arcpy.HillShade_3d(Bathy,Hillshade,270,45,"#",z_factor)

