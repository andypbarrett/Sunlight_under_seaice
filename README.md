# Sunlight Under Sea Ice

Code for Sunlight Under Sea Ice project

__Under Construction__

Use `git clone `

## Example Usage
```
(base) nsidc-abarrett-442:sunlight$ ipython
Python 3.7.6 | packaged by conda-forge | (default, Mar  5 2020, 15:27:18) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.17.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from read_grads import read_grads, parse_xyzdim

In [2]: swe = read_grads('/home/apbarret/Data/Snow_on_seaice/grads_example/swed_ease_grid.gdat')

In [3]: swe[0,:,:,0].plot()
Out[3]: <matplotlib.collections.QuadMesh at 0x7f073b5a5710>

In [4]: import matplotlib.pyplot as plt

In [5]: plt.show()
```
