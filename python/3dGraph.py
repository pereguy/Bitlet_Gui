import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

x = np.arange(-5,5,0.1)
y = np.sin(x)
fig = plt.figure(figsize=(10,10))
ax = fig.gca(projection='3d')
ax.plot(x,y,'bo', zs=0, zdir='y')

origin = [0,0,0]
ax.text(origin[0],origin[0],origin[0],"origin",size=20)

ax.set_xlabel('X',labelpad=10,fontsize='large')
ax.set_ylabel('Y',labelpad=10,fontsize='large')
ax.set_zlabel('Z',labelpad=10,fontsize='large')

fig.show()