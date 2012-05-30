
from spectralTools.models import modelLookup
from spectralTools.scatReader import scatReader
from scipy.integrate import quad, quadrature
from numpy import array, sqrt, zeros, vstack
import pickle


def deriv(f):

    def df(x, h=0.1e-7):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df





class fluxLightCurve:


    def __init__(self,scat,eMin,eMax):

        
        self.eMin = eMin
        self.eMax = eMax
        

        self.scat = scat


        self.tBins = scat.tBins
        self.modelNames = scat.modelNames

        self.modelDict = modelLookup



    def __add__(self,other):

        if other.eMin != self.eMin:
            print "eMins do not match"
            return


        if other.eMax != self.eMax:
            print "eMaxs do not match"
            return


        if other.modelNames != self.modelNames:
            print "modelNames do not match"
            return
          
        new = fluxLightCurve(self.scat,self.eMin,self.eMax)
        tBins = array(self.tBins.tolist().extend(other.tBins.tolist()) )
        new.tBins = tBins

        new.fluxes = dict(self.fluxes)
        new.fluxErrors = list(self.fluxErrors)
        new.fluxErrors.extend(other.fluxErrors)
        
        for x in self.modelNames:
            new.fluxes[x].extend(other.fluxes[x])
              

        return new 
          




 

    def CalculateFlux(self,modelName,params):

        model = self.modelDict[modelName]
        
        if (modelName == 'Band\'s GRB, Epeak') or (modelName =='Power Law w. 2 Breaks'):
            
            val,err, = quadrature(model, self.eMin,self.eMax,args=params[0],tol=1.49e-10, rtol=1.49e-10, maxiter=200)
            return val
            

        val,err, = quad(model, self.eMin,self.eMax,args=params[0].tolist(),epsabs=0., epsrel= 1.e-5 )

        return val


   
    def FluxError(self, params, covar, currentModel):
        '''
        Params is a list of the params from each models
        [mod1,mod2,...]

        '''


        

        firstDerivates = []
        
        for modName,par, z  in zip(self.scat.modelNames,params, self.scat.paramNames):

            model = self.modelDict[modName]
            #print modName
            for parName in z:

                print parName
               

                def tmpFlux(currentPar):

                    tmpParams = par.copy()
                    #print "\nCurrent param:"
                    #print currentPar

  #                  print "\nTmp Params:"
   #                 print tmpParams
                    tmpParams[parName]=currentPar


    #                print "\n New Tmp Params:"
     #               print tmpParams

                    return self.CalculateFlux(modName,tmpParams)




                if modName == currentModel:
                    #print "in currentModel"
                    firstDerivates.append( deriv(tmpFlux)(par[parName]))

                elif currentModel == "total":
                    #print "in total"
                    firstDerivates.append( deriv(tmpFlux)(par[parName]))
                else:
                    #print "not currentModel"
                    firstDerivates.append(0.0)

        #print firstDerivates
    
        firstDerivates = array(firstDerivates)
        tmp = firstDerivates.dot(covar)

        errors =  tmp.dot(firstDerivates)
        return errors
  


    def FormatCovarMat(self):


        length = self.scat.numParams
        
        self.covars = []
      
        for x in self.scat.covars:
            
            covar = []
    

            for i in range(length):
                

                tmp = []

                for j in range(length):
                   

                    #tmp.append(x[i*length+j])
                    tmp.append(x[i][j])

                covar.append(tmp)
                    
            self.covars.append(array(covar))

    



    def CreateVariableLightCurve(self,eMin,eMax):

        fluxes = []

        for x in self.modelNames:

            tmp = []

            for pars,emin,emax in zip(self.scat.models[x]['values'],eMin,eMax):

                self.eMin = emin 
                self.eMax = emax 
                flux = self.CalculateFlux(x,pars)
                tmp.append(flux)


            fluxes.append(tmp)

       
        fluxes = map(array,fluxes)

        totFlux = zeros(len(fluxes[0]))

        for x in fluxes:
            totFlux+=x

        fluxes.append(totFlux)

        tmp = list(self.modelNames)
        tmp.append('total')

        self.fluxes = dict(zip(tmp,fluxes))
        



    def CreateLightCurve(self):


        fluxes = []

        for x in self.modelNames:

            tmp = []

            for pars in self.scat.models[x]['values']:

                flux = self.CalculateFlux(x,pars)
                tmp.append(flux)


            fluxes.append(tmp)

       
        fluxes = map(array,fluxes)

        totFlux = zeros(len(fluxes[0]))

        for x in fluxes:
            totFlux+=x

        fluxes.append(totFlux)

        tmp = list(self.modelNames)
        tmp.append('total')

        self.fluxes = dict(zip(tmp,fluxes))


        






    def LightCurveErrors(self):

        self.FormatCovarMat()

        tmpParamArray = map(lambda x: [] ,self.tBins)
        

        individualFluxError=[]
        for mod in self.modelNames:
            
            
            for x,row in zip(self.scat.models[mod]['values'],tmpParamArray):
                row.append(x)

        for mod in self.modelNames:
            
            individualFluxError.append(map(lambda par,cov:self.FluxError(par,cov,mod), tmpParamArray,self.covars  ))
        
        
        individualFluxError.append ( map(lambda par,cov:self.FluxError(par,cov,"total"), tmpParamArray,self.covars  ))
        #self.fluxErrors= map(lambda par,cov:self.FluxError(par,cov,"total"), tmpParamArray,self.covars  )
        self.fluxErrors=dict(zip(self.modelNames+['total'],individualFluxError))

            
            



    def Save(self,fileName='fluxSave.p'):


        dicString=['fluxes','errors','tBins','energies']
        save = dict(zip(dicString,[self.fluxes,self.fluxErrors,self.tBins,[self.eMin,self.eMax]]))

        pickle.dump(save,open(fileName,'w'))
        











