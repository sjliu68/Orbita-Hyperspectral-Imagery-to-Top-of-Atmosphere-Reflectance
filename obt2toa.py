# -*- coding: utf-8 -*-
"""
Created on Oct 3 2019

@author: SJ
@Email: liushengjie0756@gmail.com

This script coverts orbita zhuhai-1 hyperspectral Level-1 data to TOA reflectance

# support multiple datasets 

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline
import glob
import gdal
import jdcal
from io import StringIO
from io import open
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from xml.dom.minidom import parse
import xml.dom.minidom

path = 'E:/hsi/*MSS_CCD*'  # location to hyperspectral data directory
esunfile = 'E:/esun_obt.xlsx'  # location to ESUN files
outputpath = 'E:/data/'


#%% processing

fps = glob.glob(path)  # load all directory

# read pdf and split elements 
def read_pdf(pdf):
    # resource manager
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    
    # device
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    process_pdf(rsrcmgr, device, pdf)
    device.close()
    content = retstr.getvalue()
    retstr.close()
    
    lines = str(content).split("\n")
    return lines

for fp in fps:
    fp1 = glob.glob(fp+'/*.tif')   # load image
    mypdf = glob.glob(fp+'/*.pdf')   # load data description in pdf format

    my_pdf = open(mypdf[0], "rb")  #  read pdf
    out = read_pdf(my_pdf)   # anazlye pdf and split elements
    my_pdf.close()  #  close pdf
    
    
    # obtain date time and theta 
    theta_s = np.float64(out[40])  # theta 
    date = out[36]
    year = np.uint16(date.split('年')[0])
    tmp1 = date.split('月')
    month = np.uint8(tmp1[0].split('年')[-1])
    day = np.uint8(tmp1[1].split('日')[0])
    
    # find bias and gain
    for i in range(len(out)):
        each = out[i]
        if '增益参数' in each:
            gain = out[i+3:i+3+32]
        if '偏移参数' in each:
            bias = out[i+3:i+3+32]
            
    # gain and bias
    gain = np.float32(gain)
    bias = np.float32(bias)
    
    # obtain TDIStage for radiometric calibration
    xmlfile = glob.glob(fp+'/*_meta.xml')[0]
    DOMTree = xml.dom.minidom.parse(xmlfile)
    collection = DOMTree.documentElement
    TDI = collection.getElementsByTagName("TDIStages")[0].childNodes[0].data
    TDI = TDI.split(',')
    TDI = np.uint8(TDI)
    
    
    # obtain esun based on sensor type
    esun = pd.read_excel(esunfile)
    sensor = 'ESUN_'+mypdf[0][-25]+'cmos'+mypdf[0][-19]
    esun = np.array(esun[sensor])
    
    
    count = 0  # counting how many sets of hyperspectral data
    name = outputpath+fp[-36:]  # output location
    
    
    # create output data
    im = gdal.Open(fp1[0],gdal.GA_ReadOnly)
    imx = im.RasterXSize
    imy = im.RasterYSize
    outdata = gdal.GetDriverByName('GTiff').Create(name+'.tif', imx, imy, 32, gdal.GDT_UInt16)
    bandcount = 0  # count band
    for _fp in fp1:
        print(_fp) # print current processing data
            
        # raw data
        im = gdal.Open(_fp,gdal.GA_ReadOnly)
        proj = im.GetProjection()
        geo = im.GetGeoTransform()
        im = im.ReadAsArray()
        
        im = gain[count]*im/TDI[count]+bias[count]  # raw data to radiance
        im = np.float32(im)
        
        # radiance to reflectance
        _esun = esun[count]
        count += 1
        jd = np.sum(jdcal.gcal2jd(year,month,day))
        d = 1-0.01674*np.cos((0.9856*(jd-4)*np.pi/180))
        cos=np.cos(np.radians(90-theta_s))
        toa = np.pi*im*d*d/(_esun*cos)
        toa = np.float32(toa)
        
        # save the data as int to save space
        # the output data is TOAreflectance*10000
        toa = np.uint16(toa*10000)
        
        bandcount += 1
        outdata.GetRasterBand(bandcount).WriteArray(toa)
        outdata.FlushCache() ##saves to disk!!
    
    # save data
    outdata.SetGeoTransform(geo)
    outdata.SetProjection(proj)
    outdata.FlushCache()
    outdata = None
    
    # remain rpc projection
    prj = glob.glob(fp+'/*.txt')
    prj = pd.read_csv(prj[0])
    prj.to_csv(name+'_rpc.txt',index=False)