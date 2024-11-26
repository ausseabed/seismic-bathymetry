# This script is used to convert all XYZ files to shapefiles. this
# conversion is required to generate the grids afterwards.
# contact: ulysse.lebrec@uwa.edu.au

import arcpy
import os
import sys
import math
import multiprocessing
import tqdm
import time
import datetime
 
target = r"input_folder"
output = r"output_folder"

Pts_spacing = 1 #degrees or metres !!!

def importXYZ(fileXYZ):

    if arcpy.CheckExtension("3D")=="Available":    
        arcpy.CheckOutExtension("3D")
    else:
        print("3D Extension not available")
    if arcpy.CheckExtension("Spatial")=="Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        print("Spatial extension not available")
        
    fileName = os.path.split(fileXYZ)[-1]
    EPSG = 28350#int(fileName[:-4].split("_")[-2])

    #extract and clean filename                    
    baseName = fileName[:-4]
    cleanName = baseName.replace("-","_")
    cleanName2 = cleanName.replace(".","_").replace("'","_")

    #load XYZ file as point shapefile in ArcGIS
    arcpy.env.outputZFlag = "Enabled"
    pointShp = os.path.join(output,cleanName2+"_Pts.shp") 
    crs=arcpy.SpatialReference(EPSG)

    try:
        arcpy.ASCII3DToFeatureClass_3d(fileXYZ,"XYZ",pointShp,"MULTIPOINT",z_factor=1,input_coordinate_system=crs,average_point_spacing = Pts_spacing, decimal_separator="DECIMAL_POINT")
        print("\n"+
              "     "+"Processing file: "+fileName+" is completed"+"\n")
    except arcpy.ExecuteError:
        print("\n"+
              "     "+"Processing file: "+fileName+" failed"+"\n")
        print(arcpy.GetMessages())
    
def main():
    start = time.time()
    print("      __INIT__")
    print("target file = "+target)
    
    xyz_list = []
    CZ = 1
    
    j=0
    k=0
    
    for dirs, subdirs, files in os.walk(target):
        for fileName in files:
            #print(fileName[:-4].split("_")[-1])
            if fileName.endswith(".xyz"):# and "Curt_3D_MSS_2012_FP" in fileName:
                j = j+1
                k = k + float(os.path.getsize(os.path.join(dirs,fileName)))
                xyz_list.append(os.path.join(dirs, fileName))
    
    print("     Number of files to Process: "+str(j))
    print("     size of files to Process: "+str(round(k/1000000,2))+" MB")

    cores = multiprocessing.cpu_count()
    print("     The script will fully use all cores: "+str(24))
    print("\n")

    
    pool = multiprocessing.Pool(1)
    for _ in tqdm.tqdm(pool.imap_unordered(importXYZ, xyz_list,CZ), total=len(xyz_list)):
        pass
    pool.close()
    pool.join()

    elapsed = time.time() - start
    print("Script completed in "+str(datetime.timedelta(seconds=elapsed)))

if __name__ == '__main__':
    main()

        

