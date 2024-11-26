# This script is used to extract surveys deepest points - this value
# will be used to generate synthetic velocity profiles
# contact: ulysse.lebrec@uwa.edu.au
import os

target =r"input_folder"
output =r"output_folder"
# !!! check sign L18
OutputFile = open(os.path.join(output,"Deepest_POINT_FP.csv"),"w")

for dirs, subdirs, files in os.walk(target):
    for fileName in files:
        if fileName.endswith(".xyz"):
            IDfile = fileName.split("_")[:-3]
            IDfile = '_'.join(IDfile)
            XYZ = open(os.path.join(dirs,fileName),"r")            
            X = ""
            Y = ""
            MaxDepth = 0
            for line in XYZ:
                if float(line.split(",")[2])> MaxDepth:
                    MaxDepth = float(line.split(",")[2])
                    X = line.split(",")[0]
                    Y = line.split(",")[1]
            OutputFile.write(IDfile+","+X+","+Y+","+str(MaxDepth)+"\n")
            print (IDfile+" "+X+" "+Y+" "+str(MaxDepth))
                
                    
            XYZ.close()
