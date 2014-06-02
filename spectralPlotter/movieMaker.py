import os, sys, glob

#figDir = "/Users/jburgess/Utilities/python_lib/tmpFigs/"

class movieMaker:


	def __init__(self):
		
		self.figCount = 0
		self.curDir = os.getcwd()
		self.tmpPNGs = []

	def FigSave(self,fig):
		"""
		Called if you want to save files individually
		"""
		#os.chdir(figDir)
		filename = str('%03d' % self.figCount) + '.png'
		
		fig.savefig(filename, dpi=100)
		self.figCount = self.figCount + 1 #Increment the counter
		print 'Wrote file', filename
		self.tmpPNGs.append(filename)
		



	def CreateMovie(self,figs=None, fps=10, title="output"):

		
		
		
		command = ('mencoder',
			   'mf://*.png',
			   '-mf',
			   'type=png:w=800:h=600:fps='+str(fps),
			   '-ovc',
			   'lavc',
			   '-lavcopts',
			   'vcodec=mpeg4',
			   '-oac',
			   'copy',
			   '-o',
			   title+'.avi')

		if figs == None:
			print "Starting to encode video...."
			os.spawnvp(os.P_WAIT, 'mencoder', command)

		else:
			numberOfFrames = len(figs) 

	

			for i in range(numberOfFrames):
		
				filename = str('%03d' % i) + '.png'
				self.tmpPNGs.append(filename)
				figs[i].savefig(filename, dpi=100)
				print 'Wrote file', filename


			print "Starting to encode video...."
			os.spawnvp(os.P_WAIT, 'mencoder', command)
		print "DONE!!!"
		filesToRemove = glob.glob("*.png")
		
		for  f2r in self.tmpPNGs:
			os.remove(f2r)
		
