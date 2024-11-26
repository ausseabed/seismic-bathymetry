# This script is used to reformat/rename output files from Palaeoscan
# contact: ulysse.lebrec@uwa.edu.au

import os
output = r"Path_to_output_folder"
target = r"Path_to_input_folder"
'''
for dirs, subdirs, files in os.walk(target):
    for fileN in files:
        i = 0
        print(fileN)
        outputFN = fileN#"_".join(fileN.split("_")[2:-3]).replace(" ","_")+"_FirstPick.xyz"
        timef = open(os.path.join(dirs,fileN),"r")
        depthf = open(os.path.join(output,outputFN),"w")
        for line in timef:
            try:
                i = i+1
                X = round(float(line.split(" ")[0]),3)
                Y = round(float(line.split(" ")[1]),3)
                Z = line.split(" ")[2].replace("\n","")
                depthf.write(str(X)+","+str(Y)+","+str(Z)+"\n")
            except:
                print(i, line)
                
        depthf.close()
        timef.close()

'''
for dirs, subdirs, files in os.walk(target):
    for fileN in files:
        F1 = open(os.path.join(dirs,fileN),"r")
        F2 = open(os.path.join(output,fileN),"w")
        for line in F1:
            if line !="\n":
                X = line.split(" ")[0]
                Y = line.split(" ")[1]
                Z = -float(line.split(" ")[2].replace("\n",""))
                F2.write(str(X)+","+str(Y)+","+str(Z)+"\n")
        F1.close()
        F2.close()
                    
        
        
