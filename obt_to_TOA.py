# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 10:03:19 2019

@author: SJ
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
#import xml.sax
from xml.dom.minidom import parse
import xml.dom.minidom

#%%
fp = r'E:\迅雷下载\重庆渝北区\8.12重庆渝北\HAM1_20190727205547_0006_L1_MSS_CCD2'
fp1 = glob.glob(fp+'/*.tif')
mypdf = glob.glob(fp+'/*.pdf')


#%%
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
    # 获取所有行
    lines = str(content).split("\n")
    return lines
 
#%%
my_pdf = open(mypdf[0], "rb")
out = read_pdf(my_pdf)
my_pdf.close()

theta_s = np.float64(out[40])
date = out[36]
year = np.uint16(date.split('年')[0])
tmp1 = date.split('月')
month = np.uint8(tmp1[0].split('年')[-1])
day = np.uint8(tmp1[1].split('日')[0])


for i in range(len(out)):
    each = out[i]
    if '增益参数' in each:
#        print(i)
        gain = out[i+3:i+3+32]
    if '偏移参数' in each:
#        print(i)
        bias = out[i+3:i+3+32]
        
gain = np.float32(gain)
bias = np.float32(bias)
#%%
xmlfile = glob.glob(fp+'/*_meta.xml')[0]
DOMTree = xml.dom.minidom.parse(xmlfile)
collection = DOMTree.documentElement
TDI = collection.getElementsByTagName("TDIStages")[0].childNodes[0].data
TDI = TDI.split(',')
TDI = np.uint8(TDI)
#%%
esun = pd.read_excel('E:/esun_obt.xlsx')
esun = np.array(esun['ESUN_Acmos2'])

count = 0
name = 'C:/toa'
im = gdal.Open(fp1[0],gdal.GA_ReadOnly)
imx = im.RasterXSize
imy = im.RasterYSize
outdata = gdal.GetDriverByName('GTiff').Create(name+'.tif', imx, imy, 32, gdal.GDT_Float32)
for _fp in fp1:
    print(_fp)
    im = gdal.Open(_fp,gdal.GA_ReadOnly)
    proj = im.GetProjection()
    geo = im.GetGeoTransform()
    im = im.ReadAsArray()
    
    im = gain[count]*im/TDI[count]+bias[count]
    im = np.float32(im)
    
    _esun = esun[count]
    count += 1
    jd = np.sum(jdcal.gcal2jd(year,month,day))
    d = 1-0.01674*np.cos((0.9856*(jd-4)*np.pi/180))
    cos=np.cos(np.radians(90-theta_s))
    toa = np.pi*im*d*d/(_esun*cos)
    toa = np.float32(toa)
    
    if count==1:
        outdata.SetGeoTransform(geo)
        outdata.SetProjection(proj)
    
    outdata.GetRasterBand(count).WriteArray(toa)
    outdata.FlushCache() ##saves to disk!!
outdata = None
    
    
    
    
    
