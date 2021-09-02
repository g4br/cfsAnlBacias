import os
import sys
import matplotlib.pyplot as plt

pahtcfs='./cfs'
datarun = sys.argv[1]
ncname = 'cfs.01.'+datarun+'.nc'
ncfile = os.path.join(pahtcfs,datarun,ncname)
bacia = sys.argv[2]
shp = './bacias/'+bacia+'/'+bacia+'.shp'


import salem
shdf = salem.read_shapefile(shp)
ds = salem.open_xr_dataset(ncfile)
dsr = ds.salem.roi(shape=shdf)
dsr.APCP_surface.isel(time=12).salem.quick_map()


path_png = os.path.join('./figs',bacia)
if not os.path.exists(path_png):
    os.makedirs(path_png)
png=path_png+'/pontos_'+datarun+'.png'
plt.savefig(png, dpi=300, bbox_inches='tight',pad_inches = .1)
print(png)