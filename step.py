def Step(ax,tBins,y,col='k',lw=1,ls='-',fill=False):

    x=[]
    newY=[]
    for t,v in zip(tBins,y):
        x.append(t[0])
        newY.append(v)
        x.append(t[1])
        newY.append(v)
    if fill:
        ax.fill_between(x,0,newY,color=col, alpha=.6, linestyle=ls, linewidth=lw )
    else:
        ax.plot(x,newY,color=col,linewidth=lw,linestyle=ls)
