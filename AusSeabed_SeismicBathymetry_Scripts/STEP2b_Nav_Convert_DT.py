# This script is used to convert Nav data from the depth domain back to
# the time domain when the default time-depth conversion used to generate
# nav data is deemed unsuitable - typically when a constant 1500m/s was
# used - the data can then be converted to depth again using a proper
# velocity model
# contact: ulysse.lebrec@uwa.edu.au
import os

target =r"input_folder"
output =r"output_folder"
csvFile = r"PAth_to_master_spreadsheet_containing_velocity_values"

sign = -1

for dirs, subdirs, files in os.walk(target):
    for fileName in files:
        if fileName.endswith(".xyz"):
            csv = open(csvFile,"r")
            survey = " ".join(fileName.split("_")[:-2])
            for lineCSV in csv:
                if lineCSV.split(",")[12] == "1500" and lineCSV.split(",")[0] == survey:
                    velocity = 1500
                    depthf = open(os.path.join(dirs,fileName),"r")
                    timef = open(os.path.join(output,fileName[:-4]+".xyt"),"w")
                    for line in depthf:
                        try:
                            X = float(line.split(",")[0])
                            Y = float(line.split(",")[1])
                            T = float(line.split(",")[2])*2*sign/velocity
                            timef.write(str(X)+","+str(Y)+","+str(T)+"\n")
                        except:
                            print(fileName)
                    print(fileName)
                    depthf.close()
                    timef.close()
                      
            
        
        
