def Step(ax,tBins,y,col,lw,ls='-'):

    x=[]
    newY=[]
    for t,v in zip(tBins,y):
        x.append(t[0])
        newY.append(v)
        x.append(t[1])
        newY.append(v)
    ax.plot(x,newY,color=col,linewidth=lw,linestyle=ls)
