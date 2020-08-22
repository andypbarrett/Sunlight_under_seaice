import readers.grads

# Na25 grid parameters
numberColumnsX, numberRowsY = 361, 361
cellSizeX, cellSizeY = 25067.5, 25067.5
upperLeftCornerX = -4524683.8
upperLeftCornerY = -4524683.8

def read(gdatfile, ctlfile):
    '''Reads SnowModel data into an xarray.DataArray'''
    coordX = [upperLeftCornerX + ((i + 0.5) * cellSizeX)
              for i in range(numberColumnsX)]
    coordY = [upperLeftCornerY + ((i + 0.5) * cellSizeY)
              for i in range(numberRowsY)]

    dataArray = readers.grads.read(gdatfile, ctlfile=ctlfile).squeeze()
    dataArray.coords['x'] = coordX
    dataArray.coords['y'] = coordY

    return dataArray

