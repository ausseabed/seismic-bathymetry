# This script is used to cross calibrate the Seismic data using the
# Navigation data. The master spreadsheet is used to select which
# surveys are corrected.
# contact: ulysse.lebrec@uwa.edu.au

import arcpy
import os
import sys
import math
import multiprocessing
import tqdm
import time
import datetime
import shutil
import numpy as np
import pandas as pd
import rasterio
import geopandas as gpd

# Input paths
inputXYZ = r"input_folder_XYZ"
#XYZ_SHP = r""
inputRaster = r"input_folder_raster"
Summary = r"path_to_master_spreadsheet"

# Output path
output = r"R:\Path_to_output_folder\step5e"

BaseLayerFolder = os.path.join(output,"01_BaseLayer")
CorrFiles = os.path.join(output,"02_CorrBathymetry")
XYZ_Corr = os.path.join(output,"02_Corr_XYZ")
# Parameters
binsize = 0.02048
RF = 5*binsize
z_factor = 0.00001171
Pts_spacing = 0.00025

def interp(raster):

    if arcpy.CheckExtension("3D")=="Available":    
        arcpy.CheckOutExtension("3D")
    else:
        print("3D Extension not available")
    if arcpy.CheckExtension("Spatial")=="Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        print("Spatial extension not available")
        
    shapeN = os.path.split(raster)[-1]
    baseName = "_".join(shapeN.split("_")[:-6])
    crs=arcpy.SpatialReference(4326) # check CRS
    BS = float(str("0.")+shapeN.split("_")[-3][:-1])
    status = open(Summary, "r")
    check = "n"
    for line in status:
        if line.split(",")[0] in shapeN and line.split(",")[4]=="y":
            check = "y"

    if check == "y":
        for dirs, subdirs, files in os.walk(inputXYZ):
            for fileN in files:
                if fileN.endswith(".xyz") and baseName in fileN and "_FP_"not in fileN:

                    df = pd.read_csv(os.path.join(dirs,fileN), delimiter=",",lineterminator="\n", names=['Point_X', 'Point_Y', 'Point_Z'])
                    df.index = range(len(df))
                    coords = [(x,y) for x, y in zip(df.Point_X, df.Point_Y)]
                    src = rasterio.open(raster)
                    df['error'] = [x[0] for x in src.sample(coords)]
                    df = df[df.error > -9999]
                    df['Er_FP_E'] = df.Point_Z - df.error
                    new_df = df[['Point_X', 'Point_Y', 'Er_FP_E']]
                    XYZcorrected = os.path.join(BaseLayerFolder,fileN[:-4]+"_error.xyz")
                    np.savetxt(XYZcorrected, new_df, delimiter=",",fmt="%s", newline='\n')

                    BaseLayerSHP2 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BLSHP.shp")
                    arcpy.ASCII3DToFeatureClass_3d(XYZcorrected,"XYZ",BaseLayerSHP2,"MULTIPOINT",z_factor=1,average_point_spacing = Pts_spacing,input_coordinate_system=crs)
                    
                    BaseLayer = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL.tif")
                    arcpy.Idw_3d(BaseLayerSHP2,"Shape.Z",BaseLayer,binsize,1,"FIXED "+str(RF))

                    BL_RS2 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RS2.tif")
                    arcpy.Resample_management(BaseLayer, BL_RS2, binsize/2, "BILINEAR")
                    
                    BL_RS4 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RS4.tif")
                    arcpy.Resample_management(BL_RS2, BL_RS4, binsize/4, "BILINEAR")

                    BL_RS8 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RS8.tif")
                    arcpy.Resample_management(BL_RS4, BL_RS8, binsize/8, "BILINEAR")

                    BL_RS16 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RS16.tif")
                    arcpy.Resample_management(BL_RS8, BL_RS16, binsize/16, "BILINEAR")

                    BL_RS32 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RS32.tif")
                    arcpy.Resample_management(BL_RS16, BL_RS32, binsize/32, "BILINEAR")

                    BL_RS64 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RS64.tif")
                    arcpy.Resample_management(BL_RS32, BL_RS64, binsize/64, "BILINEAR")

                    BL_RS128 = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RS128.tif")
                    arcpy.Resample_management(BL_RS64, BL_RS128, binsize/128, "BILINEAR")

                    BL_RSF = os.path.join(BaseLayerFolder,shapeN[:-4]+"BL_RSF.tif")
                    arcpy.Resample_management(BL_RS128, BL_RSF, BS, "BILINEAR")

                    Corr_raster = arcpy.sa.Raster(raster)+BL_RSF
                    Corr_raster.save(os.path.join(CorrFiles,shapeN))

                    arcpy.HillShade_3d(Corr_raster,os.path.join(CorrFiles,shapeN[:-4]+"_HS.tif"),290,45,"#",z_factor)
                    
                    for dirs, subdirs, files in os.walk(inputXYZ):
                        for fileN in files:
                            if fileN.endswith(".xyz") and baseName in fileN and "_FP_" in fileN:
                                df = pd.read_csv(os.path.join(dirs,fileN), delimiter=",",lineterminator="\n", names=['Point_X', 'Point_Y', 'Point_Z'])
                                df.index = range(len(df))
                                coords = [(x,y) for x, y in zip(df.Point_X, df.Point_Y)]
                                src = rasterio.open(BL_RSF)
                                df['error'] = [x[0] for x in src.sample(coords)]
                                df = df[df.error > -9999]
                                df['Point_Z_Cor'] = df.error + df.Point_Z
                                df['Point_Z_Cor'] = df['Point_Z_Cor'].round(2)
                                new_df = df[['Point_X', 'Point_Y', 'Point_Z_Cor']]
                                np.savetxt(os.path.join(XYZ_Corr, "_".join(shapeN.split("_")[:-3])+".xyz"), new_df, delimiter=",",fmt="%s", newline='\n')
                    
        print("Completed ... "+shapeN)
                    
    else:
        arcpy.CopyRaster_management(raster, os.path.join(CorrFiles,shapeN))
        arcpy.HillShade_3d(os.path.join(CorrFiles,shapeN),os.path.join(CorrFiles,shapeN[:-4]+"_HS.tif"),290,45,"#",z_factor)
        for dirs, subdirs, files in os.walk(inputXYZ):
            for fileN in files:
                if fileN.endswith(".xyz") and "_".join(shapeN.split("_")[:-3]) in fileN:
                    shutil.copyfile(os.path.join(dirs,fileN), os.path.join(XYZ_Corr,fileN))
        print("Not FP Calibrated ... "+shapeN)
                    
    
def main():
    start = time.time()
    print("      __INIT__")
    print("target file = "+inputRaster)
    
    xyz_list = []
    CZ = 1
    
    j=0
    k=0
    
    os.mkdir(CorrFiles)
    os.mkdir(BaseLayerFolder)
    os.mkdir(XYZ_Corr)
    
    for dirs, subdirs, files in os.walk(inputRaster):
        for fileName in files:
            if fileName.endswith(".tif"):
                j = j+1
                k = k + float(os.path.getsize(os.path.join(dirs,fileName)))
                xyz_list.append(os.path.join(dirs, fileName))
   
    print("     Number of files to Process: "+str(j))
    print("     size of files to Process: "+str(round(k/1000000,2))+" MB")

    cores = multiprocessing.cpu_count()
    print("     The script will fully use all cores: "+str(cores))
    print("\n")

    pool = multiprocessing.Pool(8)
    for _ in tqdm.tqdm(pool.imap_unordered(interp, xyz_list,CZ), total=len(xyz_list)):
        pass
    pool.close()
    pool.join()

    elapsed = time.time() - start
    print("Script completed in "+str(datetime.timedelta(seconds=elapsed)))

if __name__ == '__main__':
    main()
                
