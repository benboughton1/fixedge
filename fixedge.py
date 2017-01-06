import os
import numpy as np
import scipy.ndimage
from osgeo import gdal
import time


def make_raster(in_ds, fn, data, data_type, nodata=None):
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

#in_fn = 'a12.tif'
#out_fn  = 'a12_out.tif'

def remove_outside_cells(data, rep_value, edge_id):
        #Check for original nodata
        if data[4] == 0:
                return 0
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

def fill_cells1(data,reps):
#       print 'data[4]=',data[4]
        if data[4] == -2.0:
                #print 'fill_cells1 reps',reps
                if reps > 10:
                        return max(data)
                else:
                        count = 0
                        total = 0
                        for i in data:
                                #print 'n',i
                                if i > -1 and i != 0:
                                        count = count + 1
                                        total = total + i
                        if count < 2:
                                #print 'returning:-2'
                                #print 'count ',count,' total ',total
                                return -2.0
                        else:
                                #print 'total/count av'
                                try:
                                        av = total/count
                                except:
                                        print 'av fail'
                                        av = -2
                                #print total,count,av
                                #print 'returning:',av
                                return av
        else:
                #print 'returning:',data[4]
                return data[4]


def fill_cells2(data,reps):
#        print 'data[4]=',data[4]
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
                #        print 'n',i
                        if i > -1 and i != 0:
                                count = count + 1
                                total = total + i
                if count < 2:
                        return -1
                else:
                #       print 'total/count av'
                        try:
                                av = total/count
                        except:
                #               print 'av fail'
                                av = -1
                #       print total,count,av
                        return av
        else:
                return data[4]


def fill1(data,number):
        #print 'min:',scipy.ndimage.minimum(data)
        #print 'found?:',str(scipy.ndimage.find_objects([-1]))
        reps = 0
        while scipy.ndimage.minimum(data) == number:
                if reps < 20:
                        data = scipy.ndimage.filters.generic_filter(data, fill_cells1, size=3, mode='nearest', extra_arguments=(reps,))
                        reps += 1
                else:
                        break
        return data

def fill2(data,number):
        #print 'min:',scipy.ndimage.minimum(data)
        #print 'found?:',str(scipy.ndimage.find_objects([-1]))
        reps = 0
        while scipy.ndimage.minimum(data) == number:
                if reps < 20:
                        data = scipy.ndimage.filters.generic_filter(data, fill_cells2, size=3, mode='nearest', extra_arguments=(reps,))
                        reps += 1
                else:
                        break
        return data

def change_nodata(data):
        if data[4] == 0:
                return -9999
        else:
                return data[4]

def fe(in_,out):
        in_ds = gdal.Open(in_)
        in_band = in_ds.GetRasterBand(1)
        in_data = in_band.ReadAsArray().astype(np.float32)

        #remove single row of outside cells and replace with -1
        rep_value = -1.0
        edge_id = 0
        data_ = scipy.ndimage.filters.generic_filter(in_data, remove_outside_cells, size=3, mode='nearest', extra_arguments=(rep_value, edge_id))
        #remove second row of outside cells and replace with -2
        rep_value = -2.0
        edge_id = -1
        data = scipy.ndimage.filters.generic_filter(data_, remove_outside_cells, size=3, mode='nearest', extra_arguments=(rep_value, edge_id))

        d1 = fill1(data,-2)
        d2 = fill2(d1,-1)

        d3 = scipy.ndimage.filters.generic_filter(d2, change_nodata, size=3, mode='nearest')

        make_raster(in_ds, out, d3, gdal.GDT_Float32, nodata=-9999)

        del in_ds
