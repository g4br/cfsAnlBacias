# Demanda 1)
#Crie um código na linguagem de programação Python que utilize a ferramenta grib filter do NOMADS (NOAA) para baixar a variável de precipitação total de uma rodada de previsão do modelo meteorológico CFSv2.

#Apesar de que na demanda é pedido explicitamente um código em Python, acredito que seja mais eficiente rodarmos esta tarefa em um scrip bash, pois trabalharemos primordialmente com operadores/softwares nativos do sistema unix. Além de uma maior facilidade de implementação em ambiente operacional via crontab. 

# Deste modo, seguimos... 
wgrib2=./grib2/wgrib2/wgrib2
run=`date -u +%Y%m%d00`
horaRun=${run:8:2}
pathgrib=./cfs/$run


function geraprodutos(){
 mkdir -p ./figs
 python geraMapas.py $run
 bacias=('bacia_do_amazonas' 'bacia_do_grande' 'bacia_do_iguacu' 'bacia_do_paranapanema' 'bacia_do_tiete' 'bacia_do_tocantins' 'bacia_do_uruguai')
 for bac in ${bacias[*]}
 do
  mkdir -p ./figs/$bac
  python ./quaisPontos.py $run $bac &
  python ./geraGraf.py $run $bac &
  python ./geraAnom.py $run $bac
 done
}

mkdir -p $pathgrib

# loop download dos dados de 6 em 6 horas, até aparecer um 404 e dar erro no wget
# Além disso, faço a conversão de grib2 para netcdf, mais fácil de manipular
step=0
while :
do

 dataPrev=`date --date="${run:0:8} $horaRun + $step hours" +%Y%m%d%H`

 gribfile=$pathgrib/pgbf$dataPrev.01.$run.grb2
 tmpnc=$pathgrib/cfs.tmp.$step.nc
 # precipitação total acumulada e precipitação convectiva
 url="https://nomads.ncep.noaa.gov/cgi-bin/filter_cfs_pgb.pl?file=pgbf$dataPrev.01.$run.grb2&lev_surface=on&var_APCP=on&subregion=&leftlon=-80&rightlon=-30&toplat=10&bottomlat=-40&dir=%2Fcfs.${run:0:8}%2F$horaRun%2F6hrly_grib_01"
 
 # se der 404, wget retorna erro 8, se ocorrer tudo normal erro 0
 wget $url -O $gribfile; if [ $? != 0 ]; then rm $gribfile; break; fi
 let step+=6
done

# junta todos os gribs em um único netcdf com o wgrib2
cat $pathgrib/pgbf*.$run.grb2 | $wgrib2 - -netcdf $pathgrib/cfs.01.$run.nc

# chama a funcão que roda os python
geraprodutos
exit



