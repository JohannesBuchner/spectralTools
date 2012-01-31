import Tkinter, Tkconstants, tkFileDialog
from pulseModel import KRLPulse, NorrisPulse

class pulseModSelector(Tkinter.Frame):

  def __init__(self, root, pulsefit):

    Tkinter.Frame.__init__(self, root)

    #Grab the pulseFit module
    self.pf = pulsefit 

    # options for buttons
    button_opt = {'fill': Tkconstants.BOTH, 'anchor': Tkconstants.W  ,'padx': 5, 'pady': 10}

    pulseInt = Tkinter.IntVar()
    self.pulseInt = pulseInt
    # define buttons
    
    
    #KRL Pulse Shape variable = 0
    Tkinter.Radiobutton(self, text="KRL", variable=pulseInt, value=0).grid(row=0,column=0)

    # Lables and entry for the starting parameters for the KRL pulse model 
    Tkinter.Label(self, text="p1", bg="red", fg="white").grid(row=1,column=0)
    Tkinter.Label(self, text="p2", bg="red", fg="white").grid(row=1,column=1)
    Tkinter.Label(self, text="p3", bg="red", fg="white").grid(row=1,column=2)
    Tkinter.Label(self, text="p4", bg="red", fg="white").grid(row=1,column=3)

    p1a = Tkinter.Entry(self,width=4)
    p1b = Tkinter.Entry(self,width=4)
    p1c = Tkinter.Entry(self,width=4)
    p1d = Tkinter.Entry(self,width=4)
    p1a.grid(row=2,column=0)
    p1b.grid(row=2,column=1)
    p1c.grid(row=2,column=2)
    p1d.grid(row=2,column=3)


    #Norris Pulse Shape variable = 1
    Tkinter.Radiobutton(self, text="Norris", variable=pulseInt, value=1).grid(row=4,column=0)

    # Lables and entry for the starting parameters for the KRL pulse model 
    Tkinter.Label(self, text="p1", bg="red", fg="white").grid(row=5,column=0)
    Tkinter.Label(self, text="p2", bg="red", fg="white").grid(row=5,column=1)
    Tkinter.Label(self, text="p3", bg="red", fg="white").grid(row=5,column=2)
    Tkinter.Label(self, text="p4", bg="red", fg="white").grid(row=5,column=3)

    p2a = Tkinter.Entry(self,width=4)
    p2b = Tkinter.Entry(self,width=4)
    p2c = Tkinter.Entry(self,width=4)
    p2d = Tkinter.Entry(self,width=4)
    p2a.grid(row=6,column=0)
    p2b.grid(row=6,column=1)
    p2c.grid(row=6,column=2)
    p2d.grid(row=6,column=3)



    #Tkinter.Radiobutton(self, text="Norris", variable=pulseInt, value=2).pack(side=Tkconstants.BOTTOM,**button_opt)


    def GetPulseMod():
      
      
        
        pm = (KRLPulse(),NorrisPulse())[self.pulseInt]
        
        pm.SetInitialValues()
        pm.FixParams()
        
        

        return 
      
    
  

if __name__=='__main__':
  root = Tkinter.Tk()
  p=pulseModSelector(root,'')
  p.pack()
  #root.mainloop()
