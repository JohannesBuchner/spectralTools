from numpy import array, append, empty
from scipy.stats import norm

class ContHist:
    
    def __init__(self,data,errors,xRange):
        
        
        numElements = len(data)
        
        self.elements = array([])
        self.data=array(data)
        self.errors = array(errors)
        self.xRange = array(xRange)
        
        self._BuildHistFunction()
        self._Sum()
    
    def _BuildHistFunction(self):
        '''
        
        
        
        '''
        for p,e in zip(self.data,self.errors):
            
                           
               self.elements = append(self.elements, NormDist(p,e))
                
        #        return norm.pdf(x,p,e)
        
    def _Sum(self):
    
    
    
        self.yRange = []
    
        for x in self.xRange:
        
            tmp = 0
            for el in self.elements:
                
                tmp+=el.Eval(x)
            self.yRange.append(tmp)
            
            
            
        
class NormDist:
    
    def __init__(self,p,e):
        
        self.p = p
        self.e= e
        
    def Eval(self,x):
        
        return norm.pdf(x,self.p,self.e)
