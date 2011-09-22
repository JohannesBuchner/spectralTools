from models import *
from scatReader import scatReader
from scipy.integrate import quadrature



def deriv(f):

    def df(x, h=0.1e-5):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df





class fluxLightCurve:


    def __init__(self,scat):

        
        
        

        self.modelNames = ''


        self.fit = ''

        self.modelDict = {'Band\'s GRB, Epeak': Band, 'Black Body': BlackBody}

        #self.model = modelDict[modelName]



    def ImportDataFromSCAT(self,scat):
        ''' 
        This method is used to read in an 
        from the scatreader object. It will then seperate 
        out the required info. 
        
        '''

        self.scat = scat

        data = scat.models


        self.tBins = scat.tBins
        self.values = data[self.modelName]['values']
        self.errors = data[self.modelName]['errors']
        self.modelNames = scat.modelNames
        


    def CalculateFlux(self,modelName,params):

        model = self.modelDict[modelName]


        val,err, = quadrature(model, self.eMin,self.eMax,args=params[0],maxiter=100)

        return val





    def GeneralizeModel(self,f,params):
        
        def func(x):
            
            val = f(x, *params)
            return val

        return func
            




    


    

   
    def FluxError(self, params):
        '''
        Params is a list of the params from each models
        [mod1,mod2,...]

        '''


        
        for modName,par  in zip(scat.modelNames,params):
            
            
            
            
            

            


        


   


        

 
