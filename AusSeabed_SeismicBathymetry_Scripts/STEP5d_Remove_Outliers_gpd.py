# This script is used to remove outliers from XYZ files by comparing XYZ
# files and raster grids. note that the % treshold can be set in the
# masterspreadsheet.
# contact: ulysse.lebrec@uwa.edu.au

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
import shutil

XYZ = r"input_folder_XYZ"
Raster = r"input_folder_Raster"
output = r"output_folder"
Summary = r"Path_to_master_spreadsheet"

XYZ_EGM2008_Corr = os.path.join(output,"XYZ_EGM2008_Corr")
XYZ_EGM2008_Error = os.path.join(output,"XYZ_EGM2008_Error")

def importXYZ(fileXYZ):
        
    fileN = os.path.split(fileXYZ)[-1]               
    baseName = fileN[:-4]
    EPSG = int(baseName.split("_")[-2])
    
    if "_FP_" not in baseName:
        file_list = open(os.path.join(Summary),"r")
        for line in file_list:
            if line.split(",")[0] in fileN:
                Max_error = float(line.split(",")[3])
                
                
        for dirs, subdirs, files in os.walk(Raster):
            for fileName in files:
                if fileName.endswith(".tif"):
                    raster_name = "_".join(fileName.split("_")[:-3])
                    if raster_name == baseName:
                        
                        df = pd.read_csv(fileXYZ, delimiter=",",lineterminator="\n", names=['Point_X', 'Point_Y', 'Point_Z'])
                        df.index = range(len(df))
                        coords = [(x,y) for x, y in zip(df.Point_X, df.Point_Y)]
                        src = rasterio.open(os.path.join(dirs,fileName))
                        df['grid'] = [x[0] for x in src.sample(coords)]
                        df = df[df.grid > -9999]
                        df['Diff'] = abs((df.grid - df.Point_Z)/df.grid)
                        df0 = df[df.Diff < Max_error]
                        df1 = df[df.Diff >= Max_error]
                        new_df = df0[['Point_X', 'Point_Y', 'Point_Z']]
                        new_df1 = df1[['Point_X', 'Point_Y', 'Point_Z']]
                        i = len(new_df)
                        j = len(new_df1)
                        np.savetxt(os.path.join(XYZ_EGM2008_Corr, fileN), new_df, delimiter=",",fmt="%s", newline='\n')
                        np.savetxt(os.path.join(XYZ_EGM2008_Error, fileN), new_df1, delimiter=",",fmt="%s", newline='\n')
                        print(baseName + " removed "+str(j)+" out of "+str(i+j), Max_error)
                        
    else:
        shutil.copyfile(fileXYZ, os.path.join(XYZ_EGM2008_Corr,fileN))
        
        print(baseName + " not corrected ")
        
def main():
    start = time.time()
    print("      __INIT__")
    print("target file = "+XYZ)
    
    xyz_list = []
    CZ = 1
    
    j=0
    k=0
    
    os.mkdir(XYZ_EGM2008_Error)
    os.mkdir(XYZ_EGM2008_Corr)
    
    for dirs, subdirs, files in os.walk(XYZ):
        for fileName in files:
            if fileName.endswith(".xyz"):
                j = j+1
                k = k + float(os.path.getsize(os.path.join(dirs,fileName)))
                xyz_list.append(os.path.join(dirs, fileName))
    
    print("     Number of files to Process: "+str(j))
    print("     size of files to Process: "+str(round(k/1000000,2))+" MB")

    cores = multiprocessing.cpu_count()
    print("     The script will fully use all cores: "+str(cores))
    print("\n")

    pool = multiprocessing.Pool(12)
    for _ in tqdm.tqdm(pool.imap_unordered(importXYZ, xyz_list,CZ), total=len(xyz_list)):
        pass
    pool.close()
    pool.join()

    elapsed = time.time() - start
    print("Script completed in "+str(datetime.timedelta(seconds=elapsed)))

if __name__ == '__main__':
    main()

        

