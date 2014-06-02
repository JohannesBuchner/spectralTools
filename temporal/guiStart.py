from pulseModSelector import pulseModSelector
from fileDialog import fileDialog
from pulseFit import pulseFit
import Tkinter





root = Tkinter.Tk()
root.withdraw()

fileWindow = Tkinter.Toplevel()
pulseWindow  = Tkinter.Toplevel()

pf = pulseFit()
pms = pulseModSelector(pulseWindow,pf)
fd = fileDialog(fileWindow,pf)

pms.pack()
fd.pack()

#root.mainloop()
