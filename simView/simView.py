from spectralTools.scatReader import scatReader
from numpy import array, isfinite
import matplotlib.pyplot as plt




class simView:


    def __init__(self, scatFile):

        self.scat = scatReader(scatFile)
        

    def Compare(self, other, dCstat=None  ,nbins = 500):
        '''
        Compare the delta Cstat of two simulations

        dCstat is the delta Cstat from the two initial fits that
        you want to compare with

        '''


        fig=plt.figure(10)
        ax=fig.add_subplot(111)


        deltaCstat = self.scat.cstat - other.scat.cstat
        #Check for nan values (failed fits!)
        numInitialCstat = len(deltaCstat)

        deltaCstat = deltaCstat[isfinite(deltaCstat)]
        print "Threw away %s bad D-Cstats due to NAN\n\n"%(numInitialCstat-len(deltaCstat))
        numInitialCstat = len(deltaCstat)

        deltaCstat = deltaCstat[deltaCstat>=0.]

        print "Threw away %s bad D-Cstats due to negative values\n\n"%(numInitialCstat-len(deltaCstat))
        n, bins, patches = ax.hist(deltaCstat, bins=nbins, histtype = 'bar', color = 'k', linewidth=.000001)


        n=array(n)

        #Find which hist bin the dCstat value lies within
        
        bins = array(bins)  

        hIndex = bins.searchsorted(dCstat)
        
        if dCstat != None:
            for p in patches[hIndex-1:]:
                p.set_facecolor('r')



        ax.set_xlabel(r'$\Delta_{\rm C-Stat}$')
        ax.set_ylabel('N')

        if dCstat != None:
            ax.vlines(dCstat, 0, n.max()+n.max()*.05,linestyles='dashed')
            ax.text(dCstat, n.max()+n.max()*.06,str(dCstat), horizontalalignment='center')



        fig2 = plt.figure(11)
        ax2 = fig2.add_subplot(111)

        frac = []
        for i in range(len(bins)-1):
            frac.append( float(n[i:].sum())/float(len(deltaCstat)))


        
        binCenters =[]
        
        for i in range(len(bins)-1):
            binCenters.append( (bins[i+1]+bins[i])/2.  )

        
        
        binCenters = array(binCenters)
        ax2.hlines(1.-.68, binCenters.mean()-.9*binCenters.mean(), binCenters.mean()+.9*binCenters.mean()  )
        ax2.text(binCenters.mean()+.9*binCenters.mean()+1,1.-.68,' p = '+str(1-.68))

        ax2.hlines(1-.997, binCenters.mean()-.9*binCenters.mean(), binCenters.mean()+.9*binCenters.mean()  )
        ax2.text(binCenters.mean()+.9*binCenters.mean()+1,1-.997,' p = '+str(1-.999))


        #ax2.hlines(1.-.99999, binCenters.mean()-.9*binCenters.mean(), binCenters.mean()+.9*binCenters.mean()  )
        #ax2.text(binCenters.mean()+.9*binCenters.mean()+1,1.-.99999,'5 $\sigma$')

        
        
        ax2.semilogy(binCenters,frac,color='blue',linewidth=1.3)
        ax2.set_ylim(top=1.1,bottom=min(frac))
        if dCstat != None:
            ax2.semilogy(binCenters[hIndex-1:],frac[hIndex-1:], color='r',linewidth=1.3)
            

        ax2.set_ylabel(r"frac > $\Delta_{\rm C-Stat}$")
        ax2.set_xlabel(r'$\Delta_{\rm C-Stat}$')
        ax2.set_xlim(left=0)
       
        



        ax2.grid('on')




        
        self.dCstatFig = fig
        self.fracFig = fig2
        

        accepted = n[hIndex-1:].sum()/float(len(deltaCstat))

        if dCstat != None:
            print "Prob. to obtain D C-Stat of %s by chance is %s "%(dCstat, accepted)

        



        plt.draw()

          
    def Goodness(self, fitStat):
        '''
        Examines the number of trials with the statistic
        being less than the statistic achieved from 
        the data. If the observed data comes from the model 
        this number should be around 50
        
        '''
        print "Make sure you fit the simulation"
        print "with the model you simulated!"


        cstat = self.scat.cstat
        cstat = cstat[[isfinite(cstat)]]
        truthtable = cstat < fitStat


        numLess = len(cstat[truthtable])

        percent = 100.* float(numLess)/float(len(cstat))

        print '\n\n%s percent of the simulations were less than %s\n\n'%(percent,fitStat)



    def PlotParameterDistributions(self):

        figItr = 100
        for md, prms in zip(self.scat.modelNames, self.scat.paramNames):

            for par in prms:
                
                fig = plt.figure(figItr)
                ax = fig.add_subplot(111)

                ax.hist(self.scat.models[md]['values'][par],histtype='step',bins=100)
                

                ax.set_xlabel(md+', '+par)
                ax.set_ylabel('N')

                figItr+=1
