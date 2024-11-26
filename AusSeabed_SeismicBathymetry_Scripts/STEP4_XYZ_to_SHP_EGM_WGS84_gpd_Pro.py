# This script is used to convert XYZ data from MSL or LAT to EGM2008
# datum. It requires conversion grids as input. note that this is
# computing intensive and large files may crash.
# contact: ulysse.lebrec@uwa.edu.au

import arcpy
import os
import sys
import math
import multiprocessing
import tqdm
import time
import datetime
import numpy as np
import pandas as pd
import rasterio
import geopandas as gpd

target = r"input_folder"
output = r"output_folder"
MSL_EGM = r"Path_to_MSL_EGM_TIF_conversion_grid"
LAT_EGM = r"Path_to_LAT_EGM_TIF_conversion_grid"
summary_file = r"Path_to_master_spreadsheet_with_input_datum_info"

XYZ_SHP_Raw = os.path.join(output,"XYZ_SHP_raw")
XYZ_SHP_4326 = os.path.join(output,"XYZ_SHP_4326")
XYZ_SHP_EGM2008 = os.path.join(output,"XYZ_SHP_4326_EGM2008")
XYZ_EGM2008 = os.path.join(output,"XYZ_4326_EGM2008")

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
    EPSG = int(fileName[:-4].split("_SplitPart")[0].split("_")[-1])

    #extract and clean filename                    
    baseName = fileName[:-4]

    #load XYZ file as point shapefile in ArcGIS
    arcpy.env.outputZFlag = "Enabled"
    pointShp = os.path.join(XYZ_SHP_Raw,baseName+"_Pts.shp") 
    crs=arcpy.SpatialReference(EPSG)
    
    #load XYZ
    try:
        SHP_WGS84 = os.path.join(XYZ_SHP_4326,baseName+"_4326_Pts.shp")
        
        arcpy.ASCII3DToFeatureClass_3d(fileXYZ,"XYZ",pointShp,"POINT",z_factor=1,input_coordinate_system=crs)

        #Project XYZ file to WGS84
        
        #print(SHP_WGS84)
        arcpy.Project_management(pointShp, SHP_WGS84, arcpy.SpatialReference(4326))
        arcpy.AddGeometryAttributes_management(SHP_WGS84, "POINT_X_Y_Z_M")
        #arcpy.AddXY_management(SHP_WGS84)
        
        #Extract EGM2008 Correction
        summary = open(summary_file,"r")
        check = "n"
        for line in summary:
            lineName = line.split(",")[0].replace(" ","_")
            if lineName in baseName:
                
                df = gpd.read_file(SHP_WGS84 )
                df = df[["POINT_X","POINT_Y","POINT_Z"]]

                df.index = range(len(df))
                coords = [(x,y) for x, y in zip(df.POINT_X, df.POINT_Y)]
                if line.split(",")[1].replace("\n","")=="MSL":
                    src = rasterio.open(MSL_EGM)
                    df['EGM_Cor'] = [x[0] for x in src.sample(coords)]
                    df['Corr_Z'] = df.EGM_Cor + df.POINT_Z
                    df['Corr_Z'] = df['Corr_Z'].round(2)
                    new_df = df[['POINT_X', 'POINT_Y', 'Corr_Z']]
                    np.savetxt(os.path.join(XYZ_EGM2008, baseName+"_4326_EGM2008.xyz"), new_df, delimiter=",",fmt="%s", newline='\n')            
                    check = "y"

                elif line.split(",")[1].replace("\n","")=="LAT":
                    src = rasterio.open(LAT_EGM)
                    df['EGM_Cor'] = [x[0] for x in src.sample(coords)]
                    df['Corr_Z'] = df.EGM_Cor + df.POINT_Z
                    df['Corr_Z'] = df['Corr_Z'].round(2)
                    new_df = df[['POINT_X', 'POINT_Y', 'Corr_Z']]
                    np.savetxt(os.path.join(XYZ_EGM2008, baseName+"_4326_EGM2008.xyz"), new_df, delimiter=",",fmt="%s", newline='\n')
                    check = "y"
                    
                elif line.split(",")[1].replace("\n","")=="EGM":
                    np.savetxt(os.path.join(XYZ_EGM2008, baseName+"_4326_EGM2008.xyz"), df, delimiter=",",fmt="%s", newline='\n')
                    check = "y"
                else:
                    np.savetxt(os.path.join(XYZ_EGM2008, baseName+"_4326_EGM2008.xyz"), df, delimiter=",",fmt="%s", newline='\n')
                    print(baseName+" . . . NO DATUM REF")
                
                break
        if check == "n":
            print(lineName, baseName+" . . . NO DATUM REF")
    except:
        print(fileXYZ+"_CRASHED")
        print(arcpy.GetMessages())
    
def main():
    start = time.time()
    print("      __INIT__")
    print("target file = "+target)
    
    xyz_list = []
    CZ = 1
    
    j=0
    k=0

    os.mkdir(XYZ_SHP_Raw)
    os.mkdir(XYZ_SHP_4326)
    os.mkdir(XYZ_SHP_EGM2008)
    os.mkdir(XYZ_EGM2008)
    
    for dirs, subdirs, files in os.walk(target):
        for fileName in files:
            #print(fileName[:-4].split("_")[-1])
            if fileName.endswith(".xyz"):
                j = j+1
                k = k + float(os.path.getsize(os.path.join(dirs,fileName)))
                xyz_list.append(os.path.join(dirs, fileName))
    
    print("     Number of files to Process: "+str(j))
    print("     size of files to Process: "+str(round(k/1000000,2))+" MB")

    cores = multiprocessing.cpu_count()
    print("     The script will fully use all cores: "+str(16))
    print("\n")

    pool = multiprocessing.Pool(8)
    for _ in tqdm.tqdm(pool.imap_unordered(importXYZ, xyz_list,CZ), total=len(xyz_list)):
        pass
    pool.close()
    pool.join()

    elapsed = time.time() - start
    print("Script completed in "+str(datetime.timedelta(seconds=elapsed)))

if __name__ == '__main__':
    main()

        

