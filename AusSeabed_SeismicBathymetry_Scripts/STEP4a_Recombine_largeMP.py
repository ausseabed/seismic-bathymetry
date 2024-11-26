# This script is used to recombine files that were previously split to
# improve processing speed.
# contact: ulysse.lebrec@uwa.edu.au

import os
import shutil

input_file = r"input_folder"
output_file = r"output_folder"

previous = ""

for dirs, subdirs, files in os.walk(input_file):
    for fileN in files:
        if fileN.endswith(".xyz"):
            print(fileN)
            if "SplitPart" in fileN:
                baseName = fileN.split("SplitPart")[0]
                in_file = open(os.path.join(dirs,fileN),"r")
                if baseName != previous:
                    out_file = open(os.path.join(output_file,baseName+"4326_EGM2008.xyz"),"w")
                    for line in in_file:
                        out_file.write(line)
                else:
                    for line in in_file:
                        out_file.write(line)
                previous = baseName
            else:
                shutil.copyfile(os.path.join(dirs,fileN), os.path.join(output_file,fileN))
                
            
            
            
