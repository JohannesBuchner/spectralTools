import spectralTools.scatReader as sRead
import fluxLightCurve as flc
import sys, os


inDir = sys.argv[1]
eMin = float(sys.argv[2])
eMax = float(sys.argv[3])

print "Looking for SCATS in "+ inDir

files = os.listdir(inDir)


print "Found: "
for x in files:
    print "\t"+x


scats = map(lambda x: sRead.scatReader(inDir + x), files)

combinedScat = scats[0]

for s in scats[1:]:
    combinedScat = combinedScat + s


fl = flc.fluxLightCurve(combinedScat,eMin,eMax)
fl.FormatCovarMat()
fl.LightCurveErrors()
fl.CreateLightCurve()
fl.Save(inDir+"/fluxSave.p")
