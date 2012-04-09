from pylab import *


class TmaxSelector:

    def __init__(self,plot):
        self.plot = plot
        self.pulseCounter = 1
        self.cid = plot.figure.canvas.mpl_connect('button_press_event',self)
        self.lines=[]
        self.yMax = max(plot.get_ydata())
      
        self.numPulse = 1
        self.points=[]
        #self.tmax=[0]
        self.points=[]


    def SetNumPoints(self,num):

        self.numPulse = num
        #self.tmax = zeros(num)



    def Kill(self):

        self.plot.figure.canvas.mpl_disconnect(self.cid)
     


    def Reset(self):

        for x in self.lines:
            x.remove()
        self.plot.get_figure().canvas.draw()
        self.lines=[]
        self.points=[]


    def GetData(self):

        return self.points
          

    def __call__(self,event):

        if event.inaxes!=self.plot.axes: return
        xLoc = event.xdata
       # print xLoc

        if self.pulseCounter>self.numPulse:
            self.Reset()
            self.pulseCounter=1
       


        if self.pulseCounter==1:
            # print "first line is at " + str(xLoc)
            self.lines.append(self.plot.get_axes().vlines(xLoc,0,self.yMax,color='g'))
            self.points.append(xLoc)
            
        elif self.pulseCounter==2:
            # print "first line is at " + str(xLoc)
            self.lines.append(self.plot.get_axes().vlines(xLoc,0,self.yMax,color='r'))
            self.points.append(xLoc)
        elif self.pulseCounter==3:
            # print "first line is at " + str(xLoc)
            self.lines.append(self.plot.get_axes().vlines(xLoc,0,self.yMax,color='y'))
            self.points.append(xLoc)
       

        self.plot.get_figure().canvas.draw()
        self.pulseCounter+=1

      
