'''
Demanda 3)

Utilizando os arquivos das bacias hidrográficas disponibilizados em bacias_cfs.zip, crie uma rotina/código que calcule a chuva média prevista para as bacias, em cada tempo dos resultados do modelo (6hrs). Esperamos ver um gráfico, com pelo menos 6 meses, com a chuva média calculada na ordenada e o tempo na abscissa.
'''

import os
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

import sys
datarun = sys.argv[1]
bacia = sys.argv[2]

pahtcfs='./cfs'
ncname = 'cfs.01.'+datarun+'.nc'
ncfile = os.path.join(pahtcfs,datarun,ncname)
shp = './bacias/'+bacia+'/'+bacia+'.shp'



import salem
shdf = salem.read_shapefile(shp)
ds = salem.open_xr_dataset(ncfile)
dsSub = ds.salem.subset(shape=shdf, margin=2)
dsr = dsSub.salem.roi(shape=shdf)
#dsr.APCP_surface.isel(time=12).salem.quick_map()

times = []
means = []
maximuns = []
for t,time in enumerate(dsr.time.values):
	PontoMax = np.nanmax(dsr.APCP_surface.isel(time=t).values)
	MediaBacia = np.nanmean(dsr.APCP_surface.isel(time=t).values)
	time = dsr.time.isel(time=t).values
	# converte de datetime64 → timestamp → datetime
	DateTime = dt.datetime.utcfromtimestamp(time.astype(dt.datetime)/1000000000)
	maximuns.append(PontoMax)
	means.append(MediaBacia)
	times.append(DateTime)

# convert list para np array
means = np.array(means)
maximuns = np.array(maximuns)
times = np.array(times)
accum = means.cumsum()

import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, FormatStrFormatter,AutoMinorLocator


fig, ax = plt.subplots()
ax.set_ylabel('Precipitação 6h [mm]', fontsize=6)
ax.tick_params(axis='y', which='major', labelsize=6)
ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.bar(times, means, color='#1e6eeb',linewidth=1)
ax.scatter(times, maximuns,s=1.5,marker='.',color='k')
ax.yaxis.set_label_position("left")
ax.yaxis.tick_left()
ax.set_xlim([times[0], times[-1]])

ax2=ax.twinx()
ax2.set_ylabel('Precipitação Acumulada\n [mm]', fontsize=6)
ax2.plot(times, accum, color='black',linestyle='dashed',linewidth=1)
ax2.tick_params(axis='y', which='major', labelsize=6)
ax2.yaxis.set_label_position('right')
ax2.yaxis.tick_right()
ax2.set_ylim(ymin=0)

ax.grid(axis='y',linestyle=':',alpha=0.25,color='k')
ax.grid(axis='x',linestyle='-',alpha=0.25,color='k')

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b/%Y'))

ax.xaxis.set_tick_params(rotation=45,labelsize=8)

from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
	Line2D([0], [0], label='Acumulado',color='k',linestyle='dashed',linewidth=1),
	Line2D([0], [0], marker='o', color='w', label='Máximo da Grade 6h',markerfacecolor='k', markersize=5),
	Patch(facecolor='#1e6eeb',label='Precipitação 6h'),
	Line2D([0], [0], label='Std Media '+str(np.std(means)),color='w',linestyle='dashed',linewidth=1),
	Line2D([0], [0], label='Média Média '+str(np.mean(means)),color='w',linestyle='dashed',linewidth=1),
	Line2D([0], [0], label='Std Máximos '+str(np.std(maximuns)),color='w',linestyle='dashed',linewidth=1),
	Line2D([0], [0], label='Média Max '+str(np.mean(maximuns)),color='w',linestyle='dashed',linewidth=1)]

ax.legend(handles=legend_elements, loc='upper left',shadow=True, handlelength=1, fontsize=7)

plt.suptitle('Time Series Para Os Pontos de Grade da '+bacia+'\nFonte: CFS - Ens: 01 - Run: '+datarun)

path_png = os.path.join('./figs',bacia)
if not os.path.exists(path_png):
    os.makedirs(path_png)
png=path_png+'/timeseries_'+datarun+'.png'
plt.savefig(png, dpi=300, bbox_inches='tight',pad_inches = .1)
print(png)