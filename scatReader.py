import pyfits as pf
from numpy import mean, dtype, float64, array, shape, concatenate, vstack, asarray
from copy import deepcopy

def f5(seq, idfun=None):  
    # order preserving 
    if idfun is None: 
        def idfun(x): return x 
    seen = {} 
    result = [] 
    for item in seq: 
        marker = idfun(item) 
        # in old Python versions: 
        # if seen.has_key(marker) 
        # but in new ones: 
        if marker in seen: continue 
        seen[marker] = 1 
        result.append(item) 
    return result



class scatReader:

    def __init__(self, fileName):
        

        if fileName == "summed":
            return
        
        self.modelNames = []
        self.models = []

        self.scat  = pf.open(fileName)

        self.tBins  = self.scat[2].data['TIMEBIN']
        self.meanTbins = map(mean,self.tBins)

        self.phtFlux = self.scat[2].data['PHTFLUX']
        self.phtFluence = self.scat[2].data['PHTFLNC']
        self.covars = self.scat[2].data['COVARMAT']

        # I may take this out at some point

        self.ExtractModels()



    def __add__(self,other):

        

        if other.modelNames != self.modelNames:
            print "modelNames do not match"
            return
          
        new = scatReader('summed')
        new.modelNames = self.modelNames
        new.numParams = self.numParams
        new.paramNames = self.paramNames

        new.tBins = concatenate((self.tBins,other.tBins))
        new.meanTbins=map(mean,new.tBins)
        
        new.phtFlux = concatenate((self.phtFlux,other.phtFlux))

        new.phtFluence = concatenate((self.phtFluence,other.phtFluence))

        new.covars = concatenate((self.covars,other.covars))





        tmp1 = []

    
        dicString = ['values','-','+']

        
        for x in self.modelNames:
            
            
            errorsplus = concatenate((self.models[x]['+'], other.models[x]['+']  ))
            errorsminus = concatenate((self.models[x]['-'], other.models[x]['-']  ))
            values = concatenate((self.models[x]['values'], other.models[x]['values'] ) )



            tmp = dict(zip(dicString,[values,errorsminus,errorsplus]))
            
            tmp1.append(tmp)


        new.models = dict(zip(self.modelNames,tmp1))

            
              

        return new 



    def GetParamArray(self, model,param):
        
        paramArr = deepcopy(self.models[model]['values'][param])
        paramErrplus = deepcopy(self.models[model]['+'][param])
        paramErrminus = deepcopy(self.models[model]['-'][param])
        tmp = asarray([paramArr,paramErrminus,paramErrplus]).transpose()[0]
        #tmp.dtype = dtype([(float,'value'),(float,'error')])
        return tmp
        



    def ExtractModels(self):


        header = self.scat[2].header.ascardlist()
        
        # Sort out the models in the scat file
        tmp = filter (lambda x: type(x.value)==str ,header)
        tmp1 = filter (lambda x:'FIT' not in x.value and  'PARAM' in  x.value ,tmp)
        self.numParams =  len(tmp1)
        
        tmp2 = map(lambda x: x.comment.split(':')[0].strip(), tmp1)

        # Find the unique entries in the list 
        self.modelNames = f5(tmp2)

        del tmp
        del tmp1
        del tmp2

        # Now extract the parameters from the models

        self.paramNames  =  map(lambda x: map(lambda y: y.comment.split(':')[1].strip() ,filter(lambda z: x in z.comment  ,header) ), self.modelNames)
        
        tmpParam =  map( lambda x: map(lambda y: y.value ,filter(lambda z: x in z.comment  ,header) ), self.modelNames)
        tmp =  map( lambda x: array( map(lambda y: self.scat[2].data[y].tolist() ,x)).transpose().tolist()  , tmpParam)
        tmp = map( lambda x: map(array,x) ,tmp)
        tmp2 =  map ( lambda x:   map(lambda y:  (y, float64)    ,x)  , self.paramNames)
        #tmp3 = map ( lambda x:   map(lambda y:  ([y,y], (float64, flo))    ,x)  , self.paramNames)
        #Assign dtypes to the params
   
        
        

        for x,y in zip(tmp,tmp2):
            for z in x:
                z.dtype = dtype(y)
                #z.dtype = dtype(y)

        dicString = ['values','-','+']
        
        tmp = map(lambda x: dict(zip(dicString,x))   ,tmp)

        self.models = dict(zip(self.modelNames,tmp))

        

        del tmp
        del tmp2

  


            




    


    
        
        
        

        

            

        
