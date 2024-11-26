# This script extracts X, Y and Z values from a navigation file
# contact: ulysse.lebrec@uwa.edu.au
import os

input_folder = r"Path_to_input_folder"
output_folder = r"Path_to_output_folder"

# GDA94 = 4283, 283XX
# WGS84 = 4326, 327XX
# AGD84 = 4203, 203XX
# AGD66 = 4202, 202XX

output_file_GDA = "output_file_GDA94.xyz"
output_file_UTM = "output_file_UTM.xyz"

O_file_GDA = os.path.join(output_folder, output_file_GDA)
O_file_UTM = os.path.join(output_folder, output_file_UTM)

of_GDA = open(O_file_GDA,"w")
of_UTM = open(O_file_UTM,"w")

print("\n")
for dirs, subdirs, files in os.walk(input_folder):
    for fileName in files:
        if fileName.endswith(".p190"):
            print(fileName)
            nav_file = open(os.path.join(dirs,fileName), "r")
            i = 0
            for line in nav_file:
                i=i+1
                if line.startswith("E")== True and line.startswith("EOF")==False: #and i > 79:
                    try:
                        Ndeg = float(line[25:27].replace(" ",""))
                        Nmin = float(line[27:29].replace(" ",""))
                        Nsec = float(line[29:34].replace(" ",""))
                        Lat = -(Ndeg + Nmin/60 + Nsec/3600)

                        X = float(line[46:55].replace(" ",""))
                        
                        Edeg = float(line[35:38].replace(" ",""))
                        Emin = float(line[38:40].replace(" ",""))
                        Esec = float(line[40:45].replace(" ",""))
                        Long = Edeg + Emin/60 +Esec/3600

                        Y = float(line[55:64].replace(" ",""))
                        
                        Depth = line[64:70].replace(" ","")
                        
                        if Depth !="" and Depth !="0":
                            Depth = float(Depth)*-1
                            of_GDA.write(str(Long)+","+str(Lat)+","+str(Depth)+"\n")
                            of_UTM.write(str(X)+","+str(Y)+","+str(Depth)+"\n")
                    except:
                        print(i, line)
                    
            nav_file.close()
        
of_GDA.close()
of_UTM.close()
