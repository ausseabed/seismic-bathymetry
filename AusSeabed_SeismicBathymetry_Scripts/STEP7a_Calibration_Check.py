# This script compares the raster grids with callibration points (in this
# case AHO depth values in a SHP, EMG2008 format) to generate an error
# report.
# contact: ulysse.lebrec@uwa.edu.au
import os
import arcpy

# Check sign of error calculation ligne 51 and 58

# Input data
Bathymetry_folder = r"input_folder_raster"
Footprint_folder =  r"input_folder_footprints_shp"

#Output folder
CPr = r"output_folder"
os.mkdir(os.path.join(CPr,"SHP_Analysis"))
# control points MSL
in_features = r"path_to_MSL_control_point.shp"

#Control points LAT
in_features1 = r"path_to_LAT_control_point.shp"

suma = open(os.path.join(CPr,"Summary.csv"),"w")
suma.write("name,MSL_pts,MSL_median,MSL_average,MSL_min,MSL_max,LAT_pts,LAT_median,LAT_average,LAT_min,LAT_max"+"\n")

if arcpy.CheckExtension("3D")=="Available":    
    arcpy.CheckOutExtension("3D")
else:
    print("3D Extension not available")
if arcpy.CheckExtension("Spatial")=="Available":
    arcpy.CheckOutExtension("Spatial")
else:
    print("Spatial extension not available")

for dirs, subdirs, files in os.walk(Bathymetry_folder):
    for fileN in files:
        if fileN.endswith(".tif") and "_HS" not in fileN:
            basename = fileN[:-4]
            basename = "_".join(fileN.split("_")[:-3])
            fp = os.path.join(Footprint_folder,basename+"_BBOX.shp")
            try:
                CP = os.path.join(CPr,"SHP_Analysis",fileN[:-4].replace(".","_")+"_CP.shp")
                CPD = os.path.join(CPr,"SHP_Analysis",fileN[:-4].replace(".","_")+"_CPD.shp")
                CP1 = os.path.join(CPr,"SHP_Analysis",fileN[:-4].replace(".","_")+"_CP1.shp")
                CPD1 = os.path.join(CPr,"SHP_Analysis",fileN[:-4].replace(".","_")+"_CPD1.shp")
                
                arcpy.Clip_analysis (in_features, fp, CP)
                arcpy.sa.ExtractValuesToPoints(CP, os.path.join(dirs,fileN), CPD)
                
                arcpy.Clip_analysis (in_features1, fp, CP1)
                arcpy.sa.ExtractValuesToPoints(CP1, os.path.join(dirs,fileN), CPD1)
                
                arcpy.AddField_management(CPD, "error", "DOUBLE", field_precision=15,field_scale=6)
                arcpy.CalculateField_management (CPD, "error", "error(!RASTERVALU!, !Elev_EGM!)", "Python_9.3", """def error( RASTERVALU, Depth):
                if  RASTERVALU != -9999:
                    return RASTERVALU- Depth
                else:
                    return -9999""")

                arcpy.AddField_management(CPD1, "error", "DOUBLE", field_precision=15,field_scale=6)
                arcpy.CalculateField_management (CPD1, "error", "error(!RASTERVALU!, !Depth!)", "Python_9.3", """def error( RASTERVALU, Depth):
                if  RASTERVALU != -9999:
                    return RASTERVALU- Depth
                else:
                    return -9999""")

                i = []
                with arcpy.da.UpdateCursor(CPD, ("error")) as cursor:
                    for row in cursor:
                        if row[0]<-100:
                            cursor.deleteRow()
                        else:
                            i.append(row[0])

                j = []
                with arcpy.da.UpdateCursor(CPD1, ("error")) as cursor:
                    for row in cursor:
                        if row[0]<-100:
                            cursor.deleteRow()
                        else:
                            j.append(row[0])
                            
                if len(i)> 0:
                    i.sort()
                    median = i[int(len(i)/2)]
                    average = sum(i)/len(i)
                    maximum = max(i)
                    minimum = min(i)
                    print(basename+"\n"+
                          "\t"+"median: "+str(median)+"\n"+
                          "\t"+"average: "+str(average)+"\n"+
                          "\t"+"maximum: "+str(maximum)+"\n"+
                          "\t"+"minimum: "+str(minimum)+"\n")
                    suma.write(basename+","+str(len(i))+","+str(median)+","+str(average)+","+str(maximum)+","+str(minimum)+",")
                else:
                    print(basename+"\n"+
                          "\t"+"No Control Points"+"\n")
                    suma.write(basename+",,,,,,")

                if len(j)> 0:
                    j.sort()
                    median = j[int(len(j)/2)]
                    average = sum(j)/len(j)
                    maximum = max(j)
                    minimum = min(j)
                    print(basename+"\n"+
                          "\t"+"median: "+str(median)+"\n"+
                          "\t"+"average: "+str(average)+"\n"+
                          "\t"+"maximum: "+str(maximum)+"\n"+
                          "\t"+"minimum: "+str(minimum)+"\n")
                    suma.write(str(len(j))+","+str(median)+","+str(average)+","+str(maximum)+","+str(minimum)+"\n")
                else:
                    print(basename+"\n"+
                          "\t"+"No Control Points"+"\n")
                    suma.write(",,,,"+"\n")
                                                
            except arcpy.ExecuteError:
                print("\n"+ str(arcpy.GetMessages()))
                suma.write(basename+",error"+"\n")
                      
suma.close()              
