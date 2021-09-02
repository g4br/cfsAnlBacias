'''
Demanda 4)

Crie um código que utilize o arquivo grb2 baixado no item 1 e quantifique a chuva média acumulada para cada uma das bacias hidrográficas disponibilizadas em bacias_cfs.zip. Após calculada, compare e calcule a diferença percentual com os dados disponibilizados no arquivo Chuva_CFS.rar, para cada uma das 7 bacias hidrográficas.



Considerando que os dados comtemplam os acumulados médios mensais, a comparação se faz interessante se gerarmos uma anomalia... a méida "climatologia" menos o previsto 
'''

import numpy as np
import os
import matplotlib.pyplot as plt


import sys
datarun = sys.argv[1]
bacia = sys.argv[2]

pahtcfs='./cfs'
ncname = 'cfs.01.'+datarun+'.nc'
ncfile = os.path.join(pahtcfs,datarun,ncname)
shp = './bacias/'+bacia+'/'+bacia+'.shp'


# linhas são os meses
# colunas são os anos desde 1979
anoi=1979
if bacia == 'bacia_do_amazonas':
	file = './chuvas/chuva_CFS_tocantins.txt'
if bacia == 'bacia_do_grande':
	file = './chuvas/chuva_CFS_grande.txt'
if bacia == 'bacia_do_iguacu':
	file = './chuvas/chuva_CFS_iguacu.txt'
if bacia == 'bacia_do_paranapanema':
	file = './chuvas/chuva_CFS_paranapanema.txt'
if bacia == 'bacia_do_tiete':
	file = './chuvas/chuva_CFS_tiete.txt'
if bacia == 'bacia_do_tocantins':
	file = './chuvas/chuva_CFS_tocantins.txt'
if bacia == 'bacia_do_uruguai':
	file = './chuvas/chuva_CFS_uruguai.txt'

import pandas as pd
df = pd.read_csv(file,sep='   ',header=None)

columns = np.arange(anoi,anoi+len(df.columns)).tolist()
meses = ['01','02','03','04','05','06','07','08','09','10','11','12']
df.columns = columns
df.index = meses

# remove a primeira e ultima coluna
del df[df.columns[0]]
del df[df.columns[-1]]

df['clima'] = df.mean(axis=1)

import datetime as dt
import salem
shdf = salem.read_shapefile(shp)
ds = salem.open_xr_dataset(ncfile)
dsSub = ds.salem.subset(shape=shdf, margin=2)
dsr = dsSub.salem.roi(shape=shdf)
#dsr.APCP_surface.isel(time=12).salem.quick_map()

times = []
means = []
for t,time in enumerate(dsr.time.values):
	PontoMax = np.nanmax(dsr.APCP_surface.isel(time=t).values)
	MediaBacia = np.nanmean(dsr.APCP_surface.isel(time=t).values)
	time = dsr.time.isel(time=t).values
	# converte de datetime64 → timestamp → datetime
	DateTime = dt.datetime.utcfromtimestamp(time.astype(dt.datetime)/1000000000)
	means.append(MediaBacia)
	times.append(DateTime)


dfCFS = pd.DataFrame({'datas':times,'values':means})
dfCFS.set_index('datas',inplace=True)
mesesDePrev = pd.date_range(times[0],times[-1], freq='1M').strftime('%Y-%m')
mesesDeClima = pd.date_range(times[0],times[-1], freq='1M').strftime('%m')
prev = np.array([dfCFS[mes].sum().values[0] for mes in mesesDePrev])
clima = np.array([df['clima'][mes] for mes in mesesDeClima])
anomalia = prev-clima


import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, FormatStrFormatter,AutoMinorLocator

fig, ax = plt.subplots(2,sharex=True,gridspec_kw={'hspace': 0})

ax[0].set_ylabel('Acumulado [mm]', fontsize=6)
ax[0].tick_params(axis='y', which='major', labelsize=6)
ax[0].bar(mesesDePrev,prev,color='#2800ba')
ax[0].plot(mesesDePrev,clima,linestyle='-', marker='o',color='k')
ymin, ymax = ax[1].get_ylim()
ax[0].yaxis.tick_right()
ax[0].set_xlim([mesesDePrev[0], mesesDePrev[-1]])
ax[0].grid(axis='y',linestyle=':',alpha=0.25,color='k')
ax[0].grid(axis='x',linestyle='-',alpha=0.25,color='k')

my_color=np.where(anomalia<0, '#ff6b6b', '#1e6eeb')
ax[1].set_ylabel('Anomalia [%]', fontsize=6)
ax[1].tick_params(axis='y', which='major', labelsize=6)
ax[1].bar(mesesDePrev,(anomalia/clima)*100,color=my_color)
ymin, ymax = ax[1].get_ylim()
ax[1].yaxis.tick_right()
ax[1].set_xlim([mesesDePrev[0], mesesDePrev[-1]])
ax[1].set_ylim([-150, 150])
ax[1].grid(axis='y',linestyle=':',alpha=0.25,color='k')
ax[1].grid(axis='x',linestyle='-',alpha=0.25,color='k')

#ax[1].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
#ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%b/%Y'))

ax[1].xaxis.set_tick_params(rotation=45,labelsize=8)

from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
	Line2D([0], [0], label='Clima',color='k',linestyle='solid',marker='o',linewidth=1),
	Patch(facecolor='#2800ba',label='Acumulado Mensal'),
	Patch(facecolor='#1e6eeb',label='Anomalia Positiva'),
	Patch(facecolor='#ff6b6b',label='Anomalia Negativa')]

ax[0].legend(handles=legend_elements, loc='upper left',shadow=True, handlelength=1, fontsize=8)

plt.suptitle('Acumulado Mesanl e Anomalia da '+bacia+'\nFonte: CFS - Ens: 01 - Run: '+datarun)


path_png = os.path.join('./figs',bacia)
if not os.path.exists(path_png):
    os.makedirs(path_png)
png=path_png+'/anom_'+datarun+'.png'
plt.savefig(png, dpi=300, bbox_inches='tight',pad_inches = .1)
print(png)