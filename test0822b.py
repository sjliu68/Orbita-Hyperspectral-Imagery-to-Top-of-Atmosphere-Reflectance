# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:31:03 2019

@author: SJ
"""

# Import the Py6S module
from Py6S import *
# Create a SixS object
s = SixS()
# Set the wavelength to 0.675um
s.wavelength = Wavelength(0.675)
# Set the aerosol profile to Maritime
s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Maritime)
# Run the model
s.run()
# Print some outputs
print(s.outputs.pixel_reflectance, s.outputs.pixel_radiance, s.outputs.direct_solar_irradiance)
# Run the model across the VNIR wavelengths, and plot the result
wavelengths, results = SixSHelpers.Wavelengths.run_vnir(s, output_name='pixel_radiance')
SixSHelpers.Wavelengths.plot_wavelengths(wavelengths, results, "Pixel radiance ($W/m^2$)")

