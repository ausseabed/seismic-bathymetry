# This script is used to generate raster gris from the shapefiles. Note
# that there are optional paragraphs to include a multiplicative factor
# on the bin size (from the master spreadsheet) and to generate
# hillshades.
# contact: ulysse.lebrec@uwa.edu.au

import sys
import math
import multiprocessing
import time
import tqdm
import datetime
import os
import shutil
import arcpy

# Input folder containing XYZ as SHP
Input_folder1 = r"input_folder"
Input_folder2 = r""
targets =[Input_folder1]
Summary = r"Path_to_master_spreadsheet"

# Output Folder
output = r"output_folder"

#Initial aggregation distance !!! use the unit of input file i.e., metres vs degrees
aggrem = float(5)

# Minimum Binsize !! use the unit of input file i.e., metres vs degrees
MinBin = float(1)

# define unit degrees or metres
unit = "metres"

if unit == "degrees":
    aggrem = aggrem/100000
    MinBin = MinBin/100000

z_factor = 1

output2 = os.path.join(output,"Raster_Grids")
if os.path.isdir(output2) == False:
    os.mkdir(output2)
check_loc = os.path.join(output,"Footprints")
if os.path.isdir(check_loc) == False:
    os.mkdir(check_loc)
if os.path.isdir(os.path.join(output2,"Bathymetry")) == False:
    os.mkdir(os.path.join(output2,"Bathymetry"))
if os.path.isdir(os.path.join(output2,"Hillshade")) == False:
    os.mkdir(os.path.join(output2,"Hillshade"))
    
def interp(shapefile):
    aggreM = aggrem    
    shapeN = os.path.split(shapefile)[-1]
    shapeN = shapeN[:-4].replace(" ","_")
    
    tempFolder = os.path.join(output,'Temp_%s'% shapeN)
    newTempFolder = os.path.join(output,"Temp_"+ shapeN+"_TempVa")
    os.mkdir(tempFolder)
    os.mkdir(newTempFolder)
    os.environ["TEMP"] = newTempFolder
    os.environ["TMP"] = newTempFolder

    EPSG = 28350#int(shapeN.split("_")[-3])
    import arcpy  
    
    if arcpy.CheckExtension("3D")=="Available":    
        arcpy.CheckOutExtension("3D")
    else:
        print("This Sucks")
    if arcpy.CheckExtension("Spatial")=="Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        print("This really sucks")

    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(EPSG)
    arcpy.scratchWorkspace = tempFolder

    GDBO = os.path.join(output2,"Bathymetry")
    z = 1
    
    try:
        
        # Bin size calculate from near points
        polyName = os.path.join(output,"Footprints",shapeN.replace("_Pts","")+"_BBOX.shp")
       
        if os.path.exists(polyName)==False:
            li = 0
            nearP = 0
            pc = 0
            
            MP_group = arcpy.management.GetCount(shapefile)[0]
            MP_group_list = []
            
            if int(MP_group) < z:
                x = int(MP_group)
            else:
                x = z
            if x == 0:
                print(shapefile)
            sample_treshold = int(MP_group)/(int(x))
            
            for n in range(0,int(x)):
                MP_group_list.append(str('"FID" = '+str(int(n*sample_treshold))))
            request = str("OR".join(MP_group_list))
         
            tempname = shapeN+"MP_TEMP_NEAR.shp"
            arcpy.FeatureClassToFeatureClass_conversion(shapefile,tempFolder,tempname,request)

            tempname2 = shapeN+"TEMP_NEAR.shp"
            arcpy.MultipartToSinglepart_management(os.path.join(tempFolder,tempname), os.path.join(tempFolder,tempname2))
            arcpy.Near_analysis(os.path.join(tempFolder,tempname2),os.path.join(tempFolder,tempname2))

            for row in arcpy.da.SearchCursor(os.path.join(tempFolder,tempname2),"NEAR_DIST"):
                li = li+1
                nearP = nearP + row[0]

            if unit == "degrees":
                binSize = float(round(nearP/li,5))
            else:
                binSize = int(round(nearP/li))

            if binSize < MinBin:
                binSize = MinBin
            binsize = 250
            #if 25*binSize>aggreM:
            #    aggreM = 25*binSize

            #aggreM = str(aggreM)
            arcpy.Delete_management(os.path.join(tempFolder,tempname2))
            arcpy.Delete_management(os.path.join(tempFolder,tempname))
         
            # Aggregation of points
            polyN = os.path.join(tempFolder,shapeN.replace("_Pts","")+"_BBOX_TEMP.shp")
            a = 1
            while a == 1:
                try:
                    arcpy.AggregatePoints_cartography(shapefile,polyN,aggreM)
                    a = 2
                except arcpy.ExecuteError:
                    if os.path.exists(polyN):
                        arcpy.Delete_management(polyN)
                        arcpy.Delete_management(polyN[:-4]+"_Tbl.dbf")
                    print("\n"+
                  "     "+os.path.split(shapefile)[-1]+"\n"+str(arcpy.GetMessages())+"__"+str(aggreM))
                
            arcpy.AddField_management(polyN,"Adm","TEXT")
            arcpy.Dissolve_management(polyN,polyName,"Adm",multi_part="MULTI_PART")
            
            arcpy.Delete_management(polyN)
            arcpy.Delete_management(polyN[:-4]+"_Tbl.dbf")
      
        area = [row[0] for row in arcpy.da.SearchCursor(polyName,"SHAPE@AREA")]
        
        # Bin size calculated from area
        for row in arcpy.da.SearchCursor(shapefile,"PointCount"):
            pc = pc + row[0]
        pointsCrop = float(pc)
       
        ptsRatio = float(area[0])/float(pointsCrop)
        print(area, pc, ptsRatio)
        if unit == "degrees":
            binsize = float(round(math.sqrt(ptsRatio),5))
        else:
            binsize = int(round(math.sqrt(ptsRatio),0))
            
        if binsize < MinBin:
            binsize = MinBin
        '''
        check1 = "no"
        
        file_list = open(os.path.join(Summary),"r")
        for line in file_list:
            if line.split(",")[0] in shapeN:
                check1 = "yes"
                binsize = float(binsize)*float(line.split(",")[2])
                if unit == "degrees":
                    binsize = float(round(binsize,5))
                else:
                    binsize = int(round(binsize,0))
        
        if check1 == "no":
            print(shapeN)
        '''
        # Interpolation of the points
        
        if unit == "degrees":
            rasterClip = os.path.join(GDBO,shapeN.replace("_Pts","")+"_"+str(binsize).replace("0.","").replace("-","")+"d_Area_IDW.tif")
            hillshade = os.path.join(output2,"Hillshade",shapeN.replace("_Pts","")+"_"+str(binsize).replace("0.","").replace("-","")+"d_Area_IDW_HS.tif")
            rasterName = os.path.join(tempFolder,shapeN.replace("_Pts","")+"_"+str(binsize).replace("0.","").replace("-","")+"d_Area_IDW_COARSE.tif")

        else:
            rasterClip = os.path.join(GDBO,shapeN.replace("_Pts","")+"_"+str(binsize)+"m_Area_IDW.tif")
            hillshade = os.path.join(output2,"Hillshade",shapeN.replace("_Pts","")+"_"+str(binsize)+"m_Area_IDW_HS.tif") 
            rasterName = os.path.join(tempFolder,shapeN.replace("_Pts","")+"_"+str(binsize)+"m_Area_IDW_COARSE.tif")
        
        power = 2         
        RF = 5*binsize
        arcpy.Idw_3d(shapefile,"Shape.Z",rasterName,binsize,power,"FIXED "+str(RF))       
        
        # Clip the output to Aggregate
        try:
            arcpy.Clip_management(rasterName, "#",rasterClip, polyName,"#","ClippingGeometry","NO_MAINTAIN_EXTENT")
            arcpy.Delete_management(rasterName)
            arcpy.HillShade_3d(rasterClip,hillshade,290,45,"#",z_factor)
            print("\n"+
                  "     "+os.path.split(shapefile)[-1]+"\n"+
                  "     Ideal Binsize (Near) is "+str(binSize)+" and the associated agggreM is :"+str(aggreM)+"\n"+
                  "     Ideal Binsize (Area) is "+str(binsize)+"\n"+
                  "     Process Completed")
        except:
            print(rasterName,rasterClip)
            print(arcpy.GetMessages())

        #Hillshade
        
        '''   
        arcpy.HillShade_3d(rasterClip,hillshade,315,45)
        
        print("\n"+
              "     "+os.path.split(shapefile)[-1]+"\n"+
              "     Ideal Binsize (Near) is "+str(binSize)+" and the associated agggreM is :"+str(aggreM)+"\n"+
              "     Ideal Binsize (Area) is "+str(binsize)+"\n"+
              "     Process Completed")
        '''
    except:
        print(shapeN+"\n"+str(arcpy.GetMessages()))
            
def main():
    start = time.time()
    print("__INIT__")
    print("\n")
   
    fc_list=[]
    check_list=[]
    CZ = 1
   
    for dirs, subdirs, files in os.walk(check_loc):
        for fileN in files:
            EPSG = 28350#fileN[:-4].split("_")[-3]
            if fileN.endswith(".shp") and "_FP_" not in fileN:
                check_list.append(fileN.split("_"+str(EPSG))[0])   
                
    for tar in targets:
        for dirs, subdirs, files in os.walk(tar):
            for fileN in files:
                if fileN.endswith(".shp"):#and "_FP_" not in fileN:
                    EPSG = 28350#fileN[:-4].split("_")[-3]
                    if fileN.split("_"+str(EPSG))[0] not in check_list:# and "_E_" in fileN:
                        #if int(EPSG) in EPSG_list:
                        fc_list.append(os.path.join(dirs, fileN))
                        #print(fileN)
                    
    print("     Number of files to process: "+str(len(fc_list))+"\n")

    pool = multiprocessing.Pool(1)
    for _ in tqdm.tqdm(pool.imap_unordered(interp, fc_list,CZ), total=len(fc_list)):
        pass
    pool.close()
    pool.join()

    for dirs in os.listdir(output):
        if dirs.startswith("Temp_"):
            shutil.rmtree(os.path.join(output,dirs), ignore_errors = True)      
    
    elapsed = time.time() - start
    print("Script completed in "+str(datetime.timedelta(seconds=elapsed)))
    
if __name__ == '__main__':
    main()
    

                
