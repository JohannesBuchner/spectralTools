import Tkinter, Tkconstants, tkFileDialog


class fileDialog(Tkinter.Frame):

  def __init__(self, root, pulsefit):

    Tkinter.Frame.__init__(self, root)

    #Grab the pulseFit module
    self.pf = pulsefit 

    # options for buttons
    button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

    label_opt = {}

    entry_opt = { 'padx': 5, 'pady': 2}

    # define buttons
    Tkinter.Button(self, text='Load TTE File', command=self.openTTE).pack(**button_opt)
    Tkinter.Button(self, text='Load Flux File', command=self.openFlux).pack(**button_opt)
    Tkinter.Button(self, text='Save Pulse Fit', command=self.SaveFit).pack(**button_opt)
   
   #### TTE Settings

    Tkinter.Label(self,text='TTE: E Min',fg="red").pack(**label_opt)
    
    self.eMinBox = Tkinter.Entry(self,width=8)
    self.eMinBox.pack(**entry_opt)
    self.eMinBox.insert(0,"10")

    Tkinter.Label(self,text='TTE: E Max',fg="red").pack(**label_opt)

    self.eMaxBox = Tkinter.Entry(self,width=8)
    self.eMaxBox.pack(**entry_opt)
    self.eMaxBox.insert(0,"10000.")

    Tkinter.Label(self,text='TTE: T Min',fg="blue").pack(**label_opt)
    
    self.tMinBox = Tkinter.Entry(self,width=8)
    self.tMinBox.pack(**entry_opt)
    self.tMinBox.insert(0,"0.")

    Tkinter.Label(self,text='TTE: T Max',fg="blue").pack(**label_opt)

    self.tMaxBox = Tkinter.Entry(self,width=8)
    self.tMaxBox.pack(**entry_opt)
    self.tMaxBox.insert(0,"10.")

    Tkinter.Label(self,text='TTE: dT',fg="blue").pack(**label_opt)

    self.deltaTBox = Tkinter.Entry(self,width=8)
    self.deltaTBox.pack(**entry_opt)
    self.deltaTBox.insert(0,"1.")

  #  Tkinter.Button(self, text='askdirectory', command=self.askdirectory).pack(**button_opt)

    # define options for opening or saving a file
    self.file_opt = options = {}
    options['defaultextension'] = '' # couldn't figure out how this works
    options['filetypes'] = [('tte', '*tte*.fit'), ('flux', '*.p')]
    options['initialdir'] = 'C:\\'
    #options['initialfile'] = 'myfile.txt'
    options['parent'] = root
    options['title'] = 'Pulse Fitting File Dialog'

    # This is only available on the Macintosh, and only when Navigation Services are installed.
    #options['message'] = 'message'

    # if you use the multiple file version of the module functions this option is set automatically.
    #options['multiple'] = 1

    # defining options for opening a directory
    self.dir_opt = options = {}
    options['initialdir'] = 'C:\\'
    options['mustexist'] = False
    options['parent'] = root
    options['title'] = 'This is a title'

#  def askopenfile(self):
#
#    """Returns an opened file in read mode."""
#
#    return tkFileDialog.askopenfile(mode='r', **self.file_opt)

  def openTTE(self):

    """Returns an opened file in read mode.
    This time the dialog just returns a filename and the file is opened by your own code.
    """

    # get filename
    filename = tkFileDialog.askopenfilename(**self.file_opt)
   # print filename
    if filename:
      self.pf.ReadTTE(filename,float(self.eMinBox.get()),float(self.eMaxBox.get()),float(self.tMinBox.get()),float(self.tMaxBox.get()),float(self.deltaTBox.get()))
    


  def openFlux(self):

    """Returns an opened file in read mode.
    This time the dialog just returns a filename and the file is opened by your own code.
    """

    # get filename
    filename = tkFileDialog.askopenfilename(**self.file_opt)

#    return filename
    if filename:
      self.pf.LoadFlux(filename)


#  def asksaveasfile(self):
#
#    """Returns an opened file in write mode."""
#
#    return tkFileDialog.asksaveasfile(mode='w', **self.file_opt)

  def SaveFit(self):

    """Returns an opened file in write mode.
    This time the dialog just returns a filename and the file is opened by your own code.
    """

    # get filename
    filename = tkFileDialog.asksaveasfilename(**self.file_opt)

    # open file on your own
    if filename:
     self.pf.SaveFit(filename)


if __name__=='__main__':
  root = Tkinter.Tk()
  fileDialog(root,'').pack()
 # root.mainloop()
