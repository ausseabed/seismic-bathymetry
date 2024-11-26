# This script is used to remove obvious null values (0, -9999 etc.).
# L30 is used to correct the vessel draft if not already done.
# contact: ulysse.lebrec@uwa.edu.au

import os

target =r"Path_to_input_folder"
output =r"Path_to_output_folder"
csvFile = r"Path_to_master_spreadsheet_containing_draft_values"

for dirs, subdirs, files in os.walk(target):
    for fileName in files:
        if fileName.endswith(".xyz"):
            check = "n"
            survey = " ".join(fileName.split("_")[:-2])
            print(survey)
            csv = open(csvFile,"r")
            
            for lineCSV in csv:
                if lineCSV.split(",")[0] == survey:

                    XYZ = open(os.path.join(dirs,fileName),"r")            
                    OutputFile = open(os.path.join(output,fileName),"w")
                    check = "y"                
                    for line in XYZ:                
                        if float(line.split(",")[2])!= 0:
                            X = line.split(",")[0]
                            Y = line.split(",")[1]
                            Z = line.split(",")[2].replace("\n","")
                            if lineCSV.split(",")[16]!= "":
                                Z = float(Z)+float(lineCSV.split(",")[16])
                            OutputFile.write(str(X)+","+str(Y)+","+str(Z)+"\n")
                    XYZ.close()
            if check == "n":
                print("name error")
                print(fileName)

            else:
                print("file processed")
                print(fileName)
            
