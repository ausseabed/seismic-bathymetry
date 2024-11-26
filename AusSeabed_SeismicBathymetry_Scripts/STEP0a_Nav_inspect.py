# This script is used to inspect navigation files that are too large to
# be opened with notepad
# contact: ulysse.lebrec@uwa.edu.au

import os

target = r"Path_to_input_file"

inspect = open(target, "r")
output = open(r"Path_to_output_file","w")
i=0
for line in inspect:
    i = i+1
    output.write(line)       
    if i ==10000:
        break
inspect.close()
