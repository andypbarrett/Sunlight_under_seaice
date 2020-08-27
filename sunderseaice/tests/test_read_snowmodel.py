from sunderseaice.readers import snowmodel

gdatfile = '/home/apbarret/Data/Snow_on_seaice/SnowModelOutput/ERA5/snod.gdat'
ctlfile = '/home/apbarret/Data/Snow_on_seaice/SnowModelOutput/ERA5/SM_snod_era5_01Aug1980-31Jul2018.ctl'

snowDepth = snowmodel.read(gdatfile, ctlfile)

print(snowDepth)
