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
        deltaCstat = deltaCstat[isfinite(deltaCstat)]

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
        ax2.hlines(.68, binCenters.mean()-.9*binCenters.mean(), binCenters.mean()+.9*binCenters.mean()  )
        ax2.text(binCenters.mean()+.9*binCenters.mean()+1,.68,'1 $\sigma$')

        ax2.hlines(.05, binCenters.mean()-.9*binCenters.mean(), binCenters.mean()+.9*binCenters.mean()  )
        ax2.text(binCenters.mean()+.9*binCenters.mean()+1,.05,'3 $\sigma$')


        ax2.hlines(1e-5, binCenters.mean()-.9*binCenters.mean(), binCenters.mean()+.9*binCenters.mean()  )
        ax2.text(binCenters.mean()+.9*binCenters.mean()+1,1e-5,'5 $\sigma$')

        
        
        ax2.semilogy(binCenters,frac,color='green')
        ax2.set_ylim(top=1.1,bottom=min(frac))
        if dCstat != None:
            ax2.semilogy(binCenters[hIndex-1:],frac[hIndex-1:], color='r')
            

        ax2.set_ylabel(r"frac > $\Delta_{\rm C-Stat}$")
        ax2.set_xlabel(r'$\Delta_{\rm C-Stat}$')

       
        ax2.hlines(.68, binCenters.mean()-.9*binCenters.mean(), binCenters.mean()+.9*binCenters.mean()  )



        ax2.grid('on')




        
        self.dCstatFig = fig
        self.fracFig = fig2
        

        accepted = n[hIndex-1:].sum()/float(len(deltaCstat))

        if dCstat != None:
            print "Prob. to obtain D C-Stat by chance %s is %s "%(dCstat, accepted)

        



        plt.draw()

          
