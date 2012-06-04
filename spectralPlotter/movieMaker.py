import os, sys, glob

figDir = "/Users/jburgess/Utilities/python_lib/tmpFigs/"

def CreateMovie(figs, fps=10, title="output"):

	os.chdir(figDir)
	numberOfFrames = len(figs) 
	
	command = ('mencoder',
           '*.png',
           '-mf',
           'type=png:w=800:h=600:fps=25',
           '-ovc',
           'lavc',
           '-lavcopts',
           'vcodec=mpeg4',
           '-oac',
           'copy',
           '-o',
           title+'.avi')

	

	for i in range(numberOfFrames):
		
	filename = str('%03d' % i) + '.png'
	figs[i].savefig(filename, dpi=100)
	print 'Wrote file', filename


	print "Starting to encode video...."
	os.spawnvp(os.P_WAIT, 'mencoder', command)
	print "DONE!!!"
	filesToRemove = glob.glob("*.png")
	for  f2r in filesToRemove:
		os.remove(f2r)
