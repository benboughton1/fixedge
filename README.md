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

You need to install Numpy before GDAL or some GDAL libraries will not be included. 

Numpy & SciPy

`pip install numpy scipy`

GDAL

(More help here - https://gist.github.com/cspanring/5680334)

`pip install gdal --global-option=build_ext --global-option="-I/usr/include/gdal/"`

Deactive virtualenv with `deactivate`

