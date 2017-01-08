"""Docstring"""

import numpy as np
import scipy.ndimage
from osgeo import gdal

def make_raster(in_ds, fn, data, data_type, nodata=None):
    """
    Export raster using GDAL.
    Code borrowed from excellent book 'Geoprocessing with Python' 
    (Manning Publishing) by Chris Garrard
    """
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(fn, in_ds.RasterXSize, in_ds.RasterYSize, 1, data_type)
    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    if nodata is not None:
        out_band.SetNoDataValue(nodata)
    out_band.WriteArray(data)
    out_band.FlushCache()
    out_band.ComputeStatistics(False)
    return out_ds

def remove_outside_cells(data, rep_value, edge_id, nodatain):
    """Removes outside cells of raster"""
    #Skip if cell is no data
    if data[4] == nodatain:
        return nodatain
    #Skip if cell has been assigned as already removed
    elif data[4] == -1:
        return -1
    else:
        edge_pixel = False
        for i in data:
            if i == edge_id:
                edge_pixel = True
        if edge_pixel:
            return rep_value
        else:
            return data[4]

def fill_cells1(data, reps):
    """Fills cells back in 1 (filter instructions)"""
    if data[4] == -2.0:
        if reps > 10:
            return max(data)
        else:
            count = 0
            total = 0
            for i in data:
                if i > -1 and i != 0:
                    count = count + 1
                    total = total + i
            if count < 2:
                return -2.0
            else:
                try:
                    av = total/count
                except:
                    print 'av fail'
                    av = -2
                return av
    else:
        return data[4]


def fill_cells2(data, reps):
    """Fills cells back in 2 (filter instructions)"""
    #print 'data[4]=',data[4]
    #print 'fill_cells2 reps:',reps
    if reps > 15:
        if max(data) < 0:
            return 0.01
        else:
            return data[4]
    if data[4] == -1.0:
        count = 0
        total = 0
        for i in data:
            if i > -1 and i != 0:
                count = count + 1
                total = total + i
        if count < 2:
            return -1
        else:
            try:
                av = total/count
            except:
                av = -1
            return av
    else:
        return data[4]


def fill1(data, number):
    """
    Fills cells back in 1
    Can run up to to 20 times to make sure no cells are left empty
    """
    #print 'min:',scipy.ndimage.minimum(data)
    #print 'found?:',str(scipy.ndimage.find_objects([-1]))
    reps = 0
    while scipy.ndimage.minimum(data) == number:
        if reps < 20:
            data = scipy.ndimage.filters.generic_filter(
                data, fill_cells1, size=3, mode='nearest', extra_arguments=(reps,))
            reps += 1
        else:
            break
    return data

def fill2(data, number):
    """Fills cells back in 2"""
    #print 'min:',scipy.ndimage.minimum(data)
    #print 'found?:',str(scipy.ndimage.find_objects([-1]))
    reps = 0
    while scipy.ndimage.minimum(data) == number:
        if reps < 20:
            data = scipy.ndimage.filters.generic_filter(
                data, fill_cells2, size=3, mode='nearest', extra_arguments=(reps,))
            reps += 1
        else:
            break
    return data

def change_nodata(data, nodatain, nodataout):
    """Set nodata value to whatever"""
    if data[4] == nodatain:
        return nodataout
    else:
        return data[4]

def fixedge(in_, out, nodatain=0, nodataout=0):
    """
    Main fixedge function.
    Deletes outside cells and replaces with new values calculated from neighbours
    """
    in_ds = gdal.Open(in_)
    in_band = in_ds.GetRasterBand(1)
    in_data = in_band.ReadAsArray().astype(np.float32)

    #remove single row of outside cells and replace with -1
    rep_value = -1.0
    edge_id = nodatain
    data_ = scipy.ndimage.filters.generic_filter(
        in_data, remove_outside_cells, size=3, mode='nearest',
        extra_arguments=(rep_value, edge_id, nodatain))
    #remove second row of outside cells and replace with -2
    rep_value = -2.0
    edge_id = -1
    data = scipy.ndimage.filters.generic_filter(
        data_, remove_outside_cells, size=3, mode='nearest',
        extra_arguments=(rep_value, edge_id, nodatain))

    d1 = fill1(data,-2)
    d2 = fill2(d1,-1)

    d3 = scipy.ndimage.filters.generic_filter(
        d2, change_nodata, size=3, mode='nearest',
        extra_arguments=(nodatain, nodataout))

    make_raster(in_ds, out, d3, gdal.GDT_Float32, nodata=nodataout)

    del in_ds
