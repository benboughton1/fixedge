# fixedge
Fixes paddock edge effect on single band raster data

Setup virtualenv

Install virtualenv if you do not already have it

`sudo pip install virtualenv`

Create virtual environment

`virtualenv fixedge_virtualenv`

Open virtual environment

`source fixedge_virtualenv/bin/activate`

Install dependencies 

GDAL

(I already had GDAL installed globally when I installed QGIS. More help here - https://gist.github.com/cspanring/5680334)

`pip install gdal --global-option=build_ext --global-option="-I/usr/include/gdal/"`

Numpy & SciPy

`pip install numpy scipy`

Deactive virtualenv with `deactivate`

