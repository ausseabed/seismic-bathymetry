# This scripts is used to generate a list of all SHP files - this can be
# used to create the masterspreadsheet used in subsequent steps.
# contact: ulysse.lebrec@uwa.edu.au

import os

final = open(os.path.join(r"outputFile"),"w")
for dirs, subdirs, files in os.walk(r"inputFolder"):
    for fileN in files:
        if fileN.endswith(".shp"):
            final.write(fileN[:-4]+"\n")
            
            
