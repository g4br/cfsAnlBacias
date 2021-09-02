'''
Demanda 2)

Faça plots de superfície (pcolor, pcolormesh, etc) dos dados disponíveis no arquivo grb2, utilizando a linguagem de programação Python.

'''
import os
import sys
import netCDF4 
import datetime as dt
import numpy as np

pahtcfs='./cfs'
datarun = sys.argv[1]
ncname = 'cfs.01.'+datarun+'.nc'
ncfile = os.path.join(pahtcfs,datarun,ncname)

nc = netCDF4.Dataset(ncfile)

# nc.variables.keys() ÓTIMO!
# dict_keys(['time', 'longitude', 'latitude', 'APCP_surface', 'ACPCP_surface'])

lon = nc.variables['longitude']
lat = nc.variables['latitude']
time_var = nc.variables['time']
dtime = netCDF4.num2date(time_var[:],time_var.units)

lons,lats = np.meshgrid(lon,lat)


# color map
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import BoundaryNorm
levs  = np.array([7.5,22.5,37.5,75.,150.,225.,300.,375.,562.5,750.,1125.,1500.])
cmap = LinearSegmentedColormap.from_list('custom',['white','navy'])
norm = BoundaryNorm(levs, ncolors=cmap.N, clip=True)
cmap.set_under('#ffffff00')	


# cria um array de trempos com os períodos de interesse
import pandas as pd
ncTimesDateTime = pd.Index([dt.datetime.strptime(str(dtime[i])[0:19],"%Y-%m-%d %H:00:00") for i in range(len(dtime))])
interest_tiems = pd.date_range(ncTimesDateTime[0],ncTimesDateTime[-1], freq='1M')

# plot
import matplotlib.pyplot as plt 
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
import cartopy.feature as cfeature

columns = 4
rows = 2
proj = ccrs.PlateCarree()
fig = plt.figure(tight_layout=False)
for t in range(len(interest_tiems)):
	if t+1 < len(interest_tiems):
		tempo1= interest_tiems[t]
		posi1 = ncTimesDateTime.get_loc(tempo1)
		tempo2=interest_tiems[t+1]
		posi2 = ncTimesDateTime.get_loc(tempo2)
		var = np.sum(nc.variables['APCP_surface'][posi1:posi2],axis=0)
	ax = fig.add_subplot(rows, columns, t+1, projection=proj)
	ax.set_extent([-75,-33,-34,6])
	mappable = ax.pcolormesh(lons,lats,var,cmap=cmap,norm=norm,transform=proj)
	states = NaturalEarthFeature(category='cultural', scale='50m',facecolor='none',name='admin_1_states_provinces_shp',edgecolor='k')
	ax.add_feature(cfeature.BORDERS,linewidth=1.05, edgecolor='k',zorder=2)
	ax.add_feature(states, linewidth=1.05, edgecolor='k',zorder=2)
	ax.coastlines('50m', linewidth=1.05, color='k',zorder=2)
	ax.set_title(tempo1.strftime("%F")+' a '+tempo2.strftime("%F"),fontsize=6)
plt.suptitle('Previsão para Precipitação Acumulada\nFonte: CFS - Ens: 01 - Run: '+datarun)

cbar_ax = fig.add_axes([0.2, .525, .6, .025])
cbar = plt.colorbar(mappable, cax=cbar_ax, orientation='horizontal',extend='both',ticks=levs,)
cbar.ax.tick_params(labelsize=7)
cbar.ax.set_xlabel('mm')


png='./figs/mensal_'+datarun+'.png'
plt.savefig(png, dpi=300, bbox_inches='tight',pad_inches = .1)
print(png)