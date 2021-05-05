import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def plot(loc):
    hm = pd.read_csv(loc+r'\xd_fou.grd_jnk2RDA.log',
                    sep = '\s+')
    plt.rc('font',family='Minion Pro')
    #with plt.style.context('seaborn-paper')
    f, ax1 = plt.subplots(1,figsize = (2,4))
    ax1.grid(True, linestyle = '--')
    ax1.scatter(hm['rho_0'],hm['df(rho_0)'], zorder = 10)
    ax1.set_xlabel(r'$\rho_0 [e\AA^{-3}]$')
    ax1.set_ylabel('$d^f$')
    #ax1.set_xlim(-0.2,0.2)
    ax1.set_ylim(0.5,3)
    #ax1.set_xticks([-0.2,-0.1,0,0.1,0.2])
    ax1.set_yticks([1,2,3])
    plt.tight_layout()
    plt.savefig(loc+r'\HM-Plot', dpi = 300)


plot('.')


