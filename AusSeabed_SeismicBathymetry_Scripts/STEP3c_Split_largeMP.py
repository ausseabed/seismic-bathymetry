# The next step (Step4) may struggle with big files without a high-end
# workstation. This script is used to split large files into smaller
# chunks.
# contact: ulysse.lebrec@uwa.edu.au

import os
import shutil
import multiprocessing
import tqdm

input_file = r"input_folder"
output_file = r"output_folder"

def chunks(l, n):
    """Chunks iterable into n sized chunks"""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def splitfile(fileXYZ):
    fileN = os.path.split(fileXYZ)[-1]
    
    size = os.path.getsize(fileXYZ)
    if size > 100000000:
        # Collect all lines, without loading whole file into memory
        lines = []
        with open(fileXYZ) as main_file:
            for line in main_file:
                lines.append(line)

        # Write each group of lines to separate files
        for i, group in enumerate(chunks(lines, n=3000000), start=1):
            with open(os.path.join(output_file,fileN[:-4]+"_SplitPart"+str(i)+".xyz"), mode="w") as out_file:
                for line in group:
                    out_file.write(line)
    else:
        shutil.copyfile(fileXYZ, os.path.join(output_file,fileN))

def main():
    
    xyz_list = []
    CZ = 1
    
    for dirs, subdirs, files in os.walk(input_file):
        for fileN in files:
            if fileN.endswith(".xyz"):
                xyz_list.append(os.path.join(dirs, fileN))

    pool = multiprocessing.Pool(2)
    for _ in tqdm.tqdm(pool.imap_unordered(splitfile, xyz_list,CZ), total=len(xyz_list)):
        pass
    pool.close()
    pool.join()
            
if __name__ == '__main__':
    main()
            
