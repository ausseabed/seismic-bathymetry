# This script is used to convert data (either seismic data or nav data)
# from the time domain to the depth domain. It uses as input symthetic
# velocity profiles from Doris (note that any SVP can be used).
# contact: ulysse.lebrec@uwa.edu.au

import os
import numpy as np
import numpy.lib.recfunctions
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import multiprocessing
import tqdm

# check sign of depth
inputProfile = r"Path_to_folder_containing_SVP"
targetXYT =r"input_folder"
output =r"output_folder"

np.seterr(divide='ignore', invalid='ignore')

def Reverse(lst):
    new_lst = lst[::-1]
    return new_lst

def interp(profile_path):
    profile = open(profile_path,"r")
    dirs = os.path.split(profile_path)[:-1]
    fileName = os.path.split(profile_path)[-1]
    ProfileID = "_".join(fileName.split("_")[:-2])#fileName[:-4].replace(" ","_") 
          
    array = np.loadtxt(profile, delimiter=" ")
    velocity = array[:,1]
    depthM = array[:,0]

    ve_sum_int = 0
    vel_sum = 0
    avg_vel_list = []
    avg_vel_list.append(velocity[0])
    for i in range(len(depthM)):
        if i > 0:
            vel_sum_int = ((velocity[i-1]+velocity[i])/2)*(depthM[i]-depthM[i-1])
            vel_sum = vel_sum + vel_sum_int
            avg_vel = vel_sum / depthM[i]
            avg_vel_list.append(avg_vel)
    AverageVelocity = avg_vel_list
    #print(AverageVelocity)
   
    depthT = depthM*2/AverageVelocity

    array = np.delete(array,2,1)
    array = np.delete(array,2,1)   #array a 2 colones
    array = np.insert(array,2,AverageVelocity, axis=1)
    array = np.insert(array,3,depthT,axis=1)
    #print(array)
    best_deg2 = {}
    for deg2 in range(1,31,1):    
        poly2 = PolynomialFeatures(degree=deg2, include_bias=False)
        poly_features2 = poly2.fit_transform(depthT.reshape(-1, 1))
        reg2 = LinearRegression()
        reg2.fit(poly_features2, AverageVelocity)
        velocity_predicted2 = reg2.predict(poly_features2)
        r = metrics.r2_score(AverageVelocity,velocity_predicted2)
        best_deg2[deg2] = r
        
    max_key2 = max(best_deg2, key=best_deg2.get)
    poly2 = PolynomialFeatures(degree=max_key2, include_bias=False)
    poly_features2 = poly2.fit_transform(depthT.reshape(-1, 1))
    reg2 = LinearRegression()
    reg2.fit(poly_features2, AverageVelocity)
    velocity_predicted2 = reg2.predict(poly_features2)
        
    CoeffCroissant = reg2.coef_.tolist()
    CoeffDecroissant = Reverse(CoeffCroissant)
    CoeffDecroissant.append(reg2.intercept_)
    function2 = np.poly1d(CoeffDecroissant)   #fonction qui lie velocity en fonction de depth en metres
    array = np.insert(array,4,function2(depthT)*depthT/2,axis=1)
     
    plt.figure(figsize=(10,20))
    plt.scatter(list(velocity),list(depthM*-1), color ="black", label = "interval velocity points")
    #plt.plot(velocity_predicted,list(depthM*-1),  color="black", label = "interval velocity function")
    plt.scatter(avg_vel_list,list(depthM*-1),  color="green", label = "average velocity points")
    #plt.scatter(AverageVelocity,list(depthM*-1),  c="red", label = "average velocity points")
    plt.plot(velocity_predicted2,list(depthM*-1),  c="red", label = "average velocity function")
    plt.title("Velocity Analysis: "+ProfileID[:-4]) 
    plt.xlabel('Velocity') 
    plt.ylabel('Depth')
    plt.legend( loc='lower right', borderaxespad=0)
    Xt = min(list(velocity))
    Yt = (max(list(depthM*-1)) - min(list(depthM*-1)))*0.9 + min(list(depthM*-1))
    #plt.text(Xt,Yt,"polynomial order int = "+str(max_key)+"\n"+"r2: "+str(round(max(best_deg.values()),2))+"\n"+"polynomial order avg = "+str(max_key2)+"\n"+"r2: "+str(round(max(best_deg2.values()),2)))
    plt.text(Xt,Yt,"polynomial order avg = "+str(max_key2)+"\n"+"r2: "+str(round(max(best_deg2.values()),2)))
    figure = os.path.join(output,ProfileID+".pdf")
    plt.ylim(min(list(depthM*-1.05)),0)
    plt.tight_layout(rect=[0,0,0.75,1])
    plt.savefig(figure)
                
    sign = -1
    
    pro = "n"
    for Dirs, Subdirs, Files in os.walk(targetXYT):
        for fileName1 in Files:
            if ProfileID in fileName1:
                print("file processed: "+fileName)
                
                XYT = open(os.path.join(Dirs,fileName1),"r")
                arrayXYT = np.loadtxt(XYT, delimiter=",")
                XYZcorrected = open(os.path.join(output,fileName1[:-4]+".xyz"),"w")        
                T = arrayXYT[:,2]
                arrayXYZcor = arrayXYT
                arrayXYZcor = np.delete(arrayXYZcor,2,1)
                D = np.round(function2(T)*T/2*sign,2)
                arrayXYZcor = np.insert(arrayXYZcor,2,D,axis=1)
                #csv.writer(XYZcorrected,delimiter=",").writerows(arrayXYZcor)
                numpy.savetxt(XYZcorrected, arrayXYZcor, delimiter=",",fmt="%s", newline='\n')
                XYT.close()
                XYZcorrected.close()
                
                pro = "y"
          
    if pro == "n":
        print("file not found: "+fileName)

def main():
    profile_list = []
    CZ = 1
    
    for dirs, subdirs, files in os.walk(inputProfile):
        for fileName in files:
            profile_list.append(os.path.join(dirs,fileName))

    pool = multiprocessing.Pool(1)
    for _ in tqdm.tqdm(pool.imap_unordered(interp, profile_list,CZ), total=len(profile_list)):
        pass
    pool.close()
    pool.join()   
if __name__ == '__main__':
    main()
