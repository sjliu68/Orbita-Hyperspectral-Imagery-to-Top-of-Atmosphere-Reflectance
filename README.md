# Orbita-Hyperspectral-Imagery-to-Top-of-Atmosphere-Reflectance
Convert Orbita Level-1 Zhuhai-1 satellite data to TOA reflectance

欧比特珠海一号高光谱数据转表观反射率



## Motivation and Goal

- The Zhuhai-1 hyperspectral satellite imagery did not provide offical TOA reflectance data. 
- The level-1 data are raw data with method for radiometric calibration, which can covert the raw data to TOA radiance. 
- TOA radiance is an observation that reflects both energy density of the ground target and the sun. 

- To eliminate the effect of sun and covert radiance to reflectance, we need to calculate how strong the sum is on top of atmosphere. 
- To do so, we need a solar irradiance spectrum. Then, we can convert radiance to reflectance by the following formula:

- (pi * *L* * square(*d*) * cos(*theta*)) / *ESUN*

where *L* is radiance, *d* is the local Earth-Sun distance in astronomical units, *theta* is solar zenith angle in degrees, and *ESUN* is the calculated mean solar exoatmospheric irradiances.

## The ESUN file of Zhuhai-1 Hyperspectral sensors 
- Various solar spectrum are available. 

- In my implementation, the 1985 Wehrli Standard Extraterrestrial Solar Irradiance Spectrum is chosen because it is the first spectrum that came to my eyes. 

- A set ot the *ESUN* values of Zhuhai-1 hyperspectral sensors is provided here as *esun_obt.xlsx*

