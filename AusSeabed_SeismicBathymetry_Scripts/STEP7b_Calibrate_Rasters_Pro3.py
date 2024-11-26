# This script applies vertical corrections to the raster grids and XYZ
# files using the correction values specified in the master spreadsheet.
# The script will also clip values as specified. The script then
# resamples and merges all raster grids into a single file. Layers are
# included in the merged raster depending on their drawing order in the Arc
# project.
# contact: ulysse.lebrec@uwa.edu.au
import os
import arcpy

summary_file = r"path_to_summary_file_generated_during_7a.csv"
output = r"output_folder"
XYZ = r"input_folder_containing_XYZ_files"
Bathymetry_project = r"path_to_Arc_pro_project.aprx"

XYZ_output = os.path.join(output,"04_XYZ_EGM_WGS84")
os.mkdir(XYZ_output)

Raster_Correted = os.path.join(output,"01_Raster_Corrected_EGM_WGS84")
os.mkdir(Raster_Correted)

RS_raster_folder = os.path.join(output,"02_Raster_RS_EGM_WGS84")
os.mkdir(RS_raster_folder)
CS = 0.0003
z_factor = 0.00001171

SN_raster_folder = os.path.join(output,"03_Raster_SN_EGM_WGS84")
os.mkdir(SN_raster_folder)

Merge_folder = os.path.join(output,"05_Merge_EGM_WGS84")
os.mkdir(Merge_folder)
merge_file = "NCB_WGS84_EGM2008_0003deg.tif"

if arcpy.CheckExtension("3D")=="Available":    
    arcpy.CheckOutExtension("3D")
else:
    print("3D Extension not available")
if arcpy.CheckExtension("Spatial")=="Available":
    arcpy.CheckOutExtension("Spatial")
else:
    print("Spatial extension not available")

print("starting")

arcpy.env.cellSize = "MINOF"
arcpy.env.resamplingMethod = "BILINEAR"

aprx = arcpy.mp.ArcGISProject(Bathymetry_project)
m = aprx.listMaps()[0]

merge_list = []
i = 0
for lyr in m.listLayers():
    if lyr.isRasterLayer == True and "HS" not in lyr.name and "Out_Merge" not in lyr.longName:
        i=i+1
        datasource = lyr.dataSource
        basename = "_".join(lyr.name.split("_")[:-3])

        print(basename)
        
        suma = open(summary_file,"r")
        for line in suma:
            if line.split(",")[0] == basename:
                Corr = line.split(",")[13]
                if Corr == "": Corr = 0
                clip = line.split(",")[14].replace("\n","")
        
        print("     applying ENC correction "+str(Corr))      
        Corr_raster = arcpy.sa.Raster(datasource) + round(float(Corr),2)
        Corr_raster.save(os.path.join(Raster_Correted,lyr.name))

        
        BSS = float("0."+lyr.name.split("_")[-3][:-1])
        print("     Resampling from "+str(BSS))

        if BSS > 8*CS:
            RS_raster8 = os.path.join(RS_raster_folder, basename+"RS0024deg.tif")                      
            arcpy.Resample_management (Corr_raster, RS_raster8, CS*8, "BILINEAR")

            RS_raster4 = os.path.join(RS_raster_folder, basename+"RS0012deg.tif")                      
            arcpy.Resample_management (RS_raster8, RS_raster4, CS*4, "BILINEAR")

            RS_raster2 = os.path.join(RS_raster_folder, basename+"RS0006deg.tif")                      
            arcpy.Resample_management (RS_raster4, RS_raster2, CS*2, "BILINEAR")
            
            Corr_raster = RS_raster2

        if BSS <= 8*CS and BSS > 4*CS:
            RS_raster4 = os.path.join(RS_raster_folder, basename+"RS0012deg.tif")                      
            arcpy.Resample_management (Corr_raster, RS_raster4, CS*4, "BILINEAR")

            RS_raster2 = os.path.join(RS_raster_folder, basename+"RS0006deg.tif")                      
            arcpy.Resample_management (RS_raster4, RS_raster2, CS*2, "BILINEAR")
            
            Corr_raster = RS_raster2

        if BSS <= 4*CS and BSS > 2*CS:
            RS_raster2 = os.path.join(RS_raster_folder, basename+"RS0006deg.tif")                      
            arcpy.Resample_management (Corr_raster, RS_raster2, CS*2, "BILINEAR")
            
            Corr_raster = RS_raster2
          
        RS_raster = os.path.join(RS_raster_folder, basename+"0003deg.tif")
        arcpy.Resample_management (Corr_raster, RS_raster, CS, "BILINEAR")
        SN_Raster = os.path.join(SN_raster_folder, basename+"0003degSN.tif")
        
        if clip != "":
            print("     cropping")
            outSetNull = arcpy.sa.SetNull(RS_raster, RS_raster, "VALUE > -"+str(clip))
            outSetNull.save(SN_Raster)
            merge_list.append(SN_Raster)
        else:
            merge_list.append(RS_raster)
        
        print("     Exporting XYZ")    
        for dirs, subdirs, files in os.walk(XYZ):
            for fileN in files:
                if fileN.endswith(".xyz"):
                    if basename == fileN[:-4]:
                        
                        XYZ_file = open(os.path.join(dirs,fileN),"r")
                        XYZ_file_output = open(os.path.join(XYZ_output,fileN),"w")
                        for line in XYZ_file:
                            X = line.split(",")[0]
                            Y = line.split(",")[1]
                            Z = float(line.split(",")[2].replace("\n","")) + float(Corr)
                            XYZ_file_output.write(X+","+Y+","+str(Z)+"\n")
                       
        print("     completed")

print(i)
print("Merging files")
merge_list.reverse()
arcpy.MosaicToNewRaster_management(merge_list, Merge_folder, merge_file, 4326, "32_BIT_FLOAT", CS, 1, "LAST")
arcpy.HillShade_3d(os.path.join(Merge_folder,merge_file),os.path.join(Merge_folder,merge_file[:-4]+"_HS.tif"),290,45,"#",z_factor)

