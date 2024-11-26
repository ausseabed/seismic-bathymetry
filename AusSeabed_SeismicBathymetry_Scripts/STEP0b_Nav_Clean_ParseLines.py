# In some cases, Navigation files are formated as a single line of text.
# This script reformats the file in columns.
# contact: ulysse.lebrec@uwa.edu.au

import os

target = r"Path_to_folder_containing_files_to_be_corrected"
output_folder = r"Path_to_output_folder"


for dirs, subdirs, files in os.walk(target):
    for fileName in files:
        if fileName.endswith(".nav"):
            folder = os.path.split(dirs)[-1]
            try:              
                print(fileName)
                output = open(os.path.join(output_folder,fileName[:-4]+"_"+str(folder)+"_clean.p190"),"w")
                inspect = open(os.path.join(dirs,fileName), "r")
                print(folder)
                n=80
                for line in inspect:
                    chunks = [line[i:i+n] for i in range(0, len(line), n)]
                    for chunk in chunks:
                        output.write(str(chunk)+"\n")
                output.close()
                inspect.close()
                print("     file processed")
            except:
                print("    survey "+fileName+" returned an error")
                
