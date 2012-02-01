import Tkinter, Tkconstants, tkFileDialog
from pulseModel import KRLPulse, NorrisPulse

class pulseModSelector(Tkinter.Frame):

  def __init__(self, root, pulsefit):

    Tkinter.Frame.__init__(self, root)

    #Grab the pulseFit module
    self.pf = pulsefit 
    self.pf.SetPulseModSelector(self)
    # options for buttons
    button_opt = {'padx': 5, 'pady': 10}

    pulseInt = Tkinter.IntVar()
    self.pulseInt = pulseInt
    # define buttons
    
    
    #KRL Pulse Shape variable = 0
    Tkinter.Radiobutton(self, text="KRL", variable=pulseInt, value=0).grid(row=0,column=0,**button_opt)

    # Lables and entry for the starting parameters for the KRL pulse model 
    Tkinter.Label(self, text="c").grid(row=1,column=1)
    Tkinter.Label(self, text="r").grid(row=1,column=2)
    Tkinter.Label(self, text="d").grid(row=1,column=3)
    Tkinter.Label(self, text="tMax").grid(row=1,column=4)
    Tkinter.Label(self, text="fMax").grid(row=1,column=5)

    self.p1b = Tkinter.Entry(self,width=4)
    self.p1c = Tkinter.Entry(self,width=4)
    self.p1d = Tkinter.Entry(self,width=4)
    self.p1a = Tkinter.Entry(self,width=4)
    self.p1e = Tkinter.Entry(self,width=4)
    self.p1a.grid(row=2,column=1)
    self.p1b.grid(row=2,column=2)
    self.p1c.grid(row=2,column=3)
    self.p1d.grid(row=2,column=4)
    self.p1e.grid(row=2,column=5)
    
    

 

    self.p1a.insert(0,"1")
    self.p1b.insert(0,"1")
    self.p1c.insert(0,"1")
    self.p1d.insert(0,"1")
    self.p1e.insert(0,"1")
  
    # Variable fix checkboxes

    self.f1a = Tkinter.IntVar()
    self.f1b = Tkinter.IntVar()
    self.f1c = Tkinter.IntVar()
    self.f1d = Tkinter.IntVar()
    self.f1e = Tkinter.IntVar()


    Tkinter.Label(self, text="Fix: ", fg="blue").grid(row=3,column=0)
    Tkinter.Checkbutton(self,variable=self.f1a, onvalue=1, offvalue=0 ).grid(row=3,column=1)
    Tkinter.Checkbutton(self,variable=self.f1b, onvalue=1, offvalue=0 ).grid(row=3,column=2)
    Tkinter.Checkbutton(self,variable=self.f1c, onvalue=1, offvalue=0 ).grid(row=3,column=3)
    Tkinter.Checkbutton(self,variable=self.f1d, onvalue=1, offvalue=0 ).grid(row=3,column=4)
    Tkinter.Checkbutton(self,variable=self.f1e, onvalue=1, offvalue=0 ).grid(row=3,column=5)

   
    





    #Norris Pulse Shape variable = 1
    Tkinter.Radiobutton(self, text="Norris", variable=pulseInt, value=1).grid(row=4,column=0,**button_opt)

    # Lables and entry for the starting parameters for the KRL pulse model 
    Tkinter.Label(self, text="A").grid(row=5,column=1)
    Tkinter.Label(self, text="tr").grid(row=5,column=2)
    Tkinter.Label(self, text="td").grid(row=5,column=3)
    Tkinter.Label(self, text="ts").grid(row=5,column=4)

    self.p2b = Tkinter.Entry(self,width=4)
    self.p2c = Tkinter.Entry(self,width=4)
    self.p2d = Tkinter.Entry(self,width=4)
    self.p2a = Tkinter.Entry(self,width=4)
    self.p2a.grid(row=6,column=1)
    self.p2b.grid(row=6,column=2)
    self.p2c.grid(row=6,column=3)
    self.p2d.grid(row=6,column=4)

    self.p2a.insert(0,"1")
    self.p2b.insert(0,"1")
    self.p2c.insert(0,"1")
    self.p2d.insert(0,"1")
   


     # Variable fix checkboxes


    self.f2a = Tkinter.IntVar()
    self.f2b = Tkinter.IntVar()
    self.f2c = Tkinter.IntVar()
    self.f2d = Tkinter.IntVar()
  

    Tkinter.Label(self, text="Fix: ", fg="blue").grid(row=7,column=0)
    Tkinter.Checkbutton(self,variable=self.f2a, onvalue=1, offvalue=0).grid(row=7,column=1)
    Tkinter.Checkbutton(self,variable=self.f2b, onvalue=1, offvalue=0).grid(row=7,column=2)
    Tkinter.Checkbutton(self,variable=self.f2c, onvalue=1, offvalue=0).grid(row=7,column=3)
    Tkinter.Checkbutton(self,variable=self.f2d, onvalue=1, offvalue=0).grid(row=7,column=4)
 
   



    #Tkinter.Radiobutton(self, text="Norris", variable=pulseInt, value=2).pack(side=Tkconstants.BOTTOM,**button_opt)


  def GetPulseMod(self):
      
      
       #These arrays are designed to get the proper intial values
        # and fixed variables,
    tmp1 = ([self.p1a,self.p1b,self.p1c,self.p1d,self.p1e],[self.p2a,self.p2b,self.p2c,self.p2d]) #param values
    tmp2 = ([self.f1a,self.f1b,self.f1c,self.f1d,self.f1e],[self.f2a,self.f2b,self.f2c,self.f2d]) #fix values

      #This array is designed so that the selector grabs the right pulse model
    pm = (KRLPulse(),NorrisPulse())[self.pulseInt.get()]
        
    pm.SetInitialValues(map(float,  map( lambda x: x.get() ,   tmp1[self.pulseInt.get()] ) ) )
    pm.FixParams(map(int,  map( lambda x: x.get(), tmp2[self.pulseInt.get()] ) )  )
      
        

    return pm 
      
    
  

if __name__=='__main__':
  root = Tkinter.Tk()
  p=pulseModSelector(root,'')
  p.pack()
  #root.mainloop()
