import gdal

# Path of netCDF file
netcdf_fname = "c:/temp/20110102120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_CDR2.0-v02.0-fv01.0.nc"

# Specify the layer name to read
layer_name = "analysed_sst"

# Open netcdf file.nc with gdal
ds = gdal.Open("NETCDF:{0}:{1}".format(netcdf_fname, layer_name))

print(ds.RasterXSize)
print(ds.RasterYSize)


