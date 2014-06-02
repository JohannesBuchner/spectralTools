import os, subprocess, time
from numpy import genfromtxt



def MakeLightCurve(bins,contents,tStart,ncp_prior):

    if len(bins) != len(contents):
        print "Bins and Contents not same size!!"
        return
    directory = "" 
    tmpBins = open("tmpBins.txt","w")
    tmpContents = open("tmpContents.txt","w")

    for b,c in zip(bins,contents):
        tmpBins.write(str(b)+"\n")
        tmpContents.write(str(c)+"\n")

    tmpBins.close()
    tmpContents.close()
 

    
    
    subprocess.call(["./bb" ,str(len(bins)), str(tStart), str(ncp_prior)])
    
    os.remove("tmpBins.txt")
    os.remove("tmpContents.txt")
    
    ret = genfromtxt("tmpLightCurve.txt")
    os.remove("tmpLightCurve.txt")
    
    return ret 
                    
    #os.system(callString)
    





