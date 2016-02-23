"""
Utilities for regridding with Grids
"""

import sys

try:
    import numpy as np
except:
    raise ImportError('The Numpy library cannot be found!')

try:
    import ESMF
except:
    raise ImportError('The ESMF library cannot be found!')

def grid_create(xdom, ydom, nx, ny, corners=False, domask=False, doarea=False, ctk=ESMF.TypeKind.R8):
    """
    :param xdom: 2,1 list containing the x domain
    :param ydom: 2,1 list conatining the y domain
    :param nx: number of longitude values at cell centers
    :param ny: number of latitude values at cell centers
    :param corners: boolean to determine whether or not to add corner coordinates to this grid
    :param domask: boolean to determine whether to set an arbitrary mask or not
    :param doarea: boolean to determine whether to set an arbitrary area values or not
    :param ctk: the coordinate typekind
    :return: grid
    """
    [x, y] = [0, 1]

    # Create arrays of center and corner values to emulate what would be read from a standard CF-like file
    # +1 because corners have one more than center
    xs = np.linspace(xdom[0], xdom[1], nx + 1)
    xcorner = np.array([xs[0:-1], xs[1::]]).T
    xcenter = (xcorner[:, 1] + xcorner[:, 0]) / 2

    # +1 because corners have one more than center
    ys = np.linspace(ydom[0], ydom[1], ny + 1)
    ycorner = np.array([ys[0:-1], ys[1::]]).T
    ycenter = (ycorner[:, 1] + ycorner[:, 0]) / 2

    # create a grid given the number of grid cells in each dimension, the center stagger location is allocated, the
    # Cartesian coordinate system and type of the coordinates are specified
    max_index = np.array([nx, ny])
    grid = ESMF.Grid(max_index, staggerloc=[ESMF.StaggerLoc.CENTER], coord_sys=ESMF.CoordSys.CART, coord_typekind=ctk)

    # set the grid coordinates using numpy arrays, parallel case is handled using grid bounds
    gridXCenter = grid.get_coords(x)
    x_par = xcenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER][x]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][x]]
    gridXCenter[...] = x_par.reshape((x_par.size, 1))

    gridYCenter = grid.get_coords(y)
    y_par = ycenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER][y]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][y]]
    gridYCenter[...] = y_par.reshape((1, y_par.size))

    # create grid corners in a slightly different manner to account for the bounds format common in CF-like files
    if corners:
        grid.add_coords([ESMF.StaggerLoc.CORNER])
        lbx = grid.lower_bounds[ESMF.StaggerLoc.CORNER][x]
        ubx = grid.upper_bounds[ESMF.StaggerLoc.CORNER][x]
        lby = grid.lower_bounds[ESMF.StaggerLoc.CORNER][y]
        uby = grid.upper_bounds[ESMF.StaggerLoc.CORNER][y]

        gridXCorner = grid.get_coords(x, staggerloc=ESMF.StaggerLoc.CORNER)
        for i0 in range(ubx - lbx - 1):
            gridXCorner[i0, :] = xcorner[i0+lbx, 0]
        gridXCorner[i0 + 1, :] = xcorner[i0+lbx, 1]

        gridYCorner = grid.get_coords(y, staggerloc=ESMF.StaggerLoc.CORNER)
        for i1 in range(uby - lby - 1):
            gridYCorner[:, i1] = ycorner[i1+lby, 0]
        gridYCorner[:, i1 + 1] = ycorner[i1+lby, 1]

    # add an arbitrary mask
    if domask:
        mask = grid.add_item(ESMF.GridItem.MASK)
        mask[:] = 1
        mask[np.where((1.75 <= gridXCenter.data < 2.25) &
                      (1.75 <= gridYCenter.data < 2.25))] = 0

    # add arbitrary areas values
    if doarea:
        area = grid.add_item(ESMF.GridItem.AREA)
        area[:] = 5.0

    return grid

def grid_create_periodic(nlon, nlat, corners=False, domask=False):
    """
    :param nlons: number of longitude values at cell centers
    :param nlats: number of latitude values at cell centers
    :param corners: boolean to determine whether or not to add corner coordinates to this grid
    :param domask: boolean to determine whether to set an arbitrary mask or not
    :return: grid
    """
    [lon, lat] = [0, 1]

    # Create arrays of center and corner values to emulate what would be read from a standard CF-like file
    # +1 because corners have one more than center
    lons = np.linspace(-180, 180, nlon + 1)
    loncorner = np.array([lons[0:-1], lons[1::]]).T
    loncenter = (loncorner[:, 1] + loncorner[:, 0]) / 2

    # +1 because corners have one more than center
    lats = np.linspace(-90, 90, nlat + 1)
    latcorner = np.array([lats[0:-1], lats[1::]]).T
    latcenter = (latcorner[:, 1] + latcorner[:, 0]) / 2

    # create a grid given the number of grid cells in each dimension the center stagger location is allocated
    max_index = np.array([nlon, nlat])
    grid = ESMF.Grid(max_index, num_peri_dims=1, staggerloc=[ESMF.StaggerLoc.CENTER])

    # set the grid coordinates using numpy arrays, parallel case is handled using grid bounds
    gridXCenter = grid.get_coords(lon)
    lon_par = loncenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER][lon]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][lon]]
    gridXCenter[...] = lon_par.reshape((lon_par.size, 1))

    gridYCenter = grid.get_coords(lat)
    lat_par = latcenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER][lat]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][lat]]
    gridYCenter[...] = lat_par.reshape((1, lat_par.size))

    # create grid corners in a slightly different manner to account for the bounds format common in CF-like files
    if corners:
        grid.add_coords([ESMF.StaggerLoc.CORNER])
        lbx = grid.lower_bounds[ESMF.StaggerLoc.CORNER][lon]
        ubx = grid.upper_bounds[ESMF.StaggerLoc.CORNER][lon]
        lby = grid.lower_bounds[ESMF.StaggerLoc.CORNER][lat]
        uby = grid.upper_bounds[ESMF.StaggerLoc.CORNER][lat]

        gridXCorner = grid.get_coords(lon, staggerloc=ESMF.StaggerLoc.CORNER)
        for i0 in range(ubx - lbx - 1):
            gridXCorner[i0, :] = loncorner[i0+lbx, 0]
        gridXCorner[i0 + 1, :] = loncorner[i0+lbx, 1]

        gridYCorner = grid.get_coords(lat, staggerloc=ESMF.StaggerLoc.CORNER)
        for i1 in range(uby - lby - 1):
            gridYCorner[:, i1] = latcorner[i1+lby, 0]
        gridYCorner[:, i1 + 1] = latcorner[i1+lby, 1]

    # add an arbitrary mask
    if domask:
        mask = grid.add_item(ESMF.GridItem.MASK)
        mask[:] = 1
        mask[np.where((1.75 <= gridXCenter.data < 2.25) &
                      (1.75 <= gridYCenter.data < 2.25))] = 0

    return grid

def grid_create_3d(xdom, ydom, zdom, nx, ny, nz, corners=False, domask=False, doarea=False):
    """
    :param xdom: 2,1 list containing the x domain
    :param ydom: 2,1 list conatining the y domain
    :param zdom: 2,1 list conatining the z domain
    :param nx: number of x values at cell centers
    :param ny: number of y values at cell centers
    :param nz: number of z values at cell centers
    :param corners: boolean to determine whether or not to add corner coordinates to this grid
    :param domask: boolean to determine whether to set an arbitrary mask or not
    :param doarea: boolean to determine whether to set an arbitrary area values or not
    :return: grid
    """
    [x, y, z] = [0, 1, 2]

    # Create arrays of center and corner values to emulate what would be read from a standard CF-like file
    # +1 because corners have one more than center
    xs = np.linspace(xdom[0], xdom[1], nx + 1)
    xcorner = np.array([xs[0:-1], xs[1::]]).T
    xcenter = (xcorner[:, 1] + xcorner[:, 0]) / 2

    # +1 because corners have one more than center
    ys = np.linspace(ydom[0], ydom[1], ny + 1)
    ycorner = np.array([ys[0:-1], ys[1::]]).T
    ycenter = (ycorner[:, 1] + ycorner[:, 0]) / 2

    # +1 because corners have one more than center
    zs = np.linspace(zdom[0], zdom[1], nz + 1)
    zcorner = np.array([zs[0:-1], zs[1::]]).T
    zcenter = (zcorner[:, 1] + zcorner[:, 0]) / 2

    # create a grid given the number of grid cells in each dimension, the center stagger location is allocated and the
    # Cartesian coordinate system is specified
    max_index = np.array([nx, ny, nz])
    grid = ESMF.Grid(max_index, staggerloc=[ESMF.StaggerLoc.CENTER_VCENTER], coord_sys=ESMF.CoordSys.CART)

    # set the grid coordinates using numpy arrays, parallel case is handled using grid bounds
    gridXCenter = grid.get_coords(x)
    x_par = xcenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER_VCENTER][x]:grid.upper_bounds[ESMF.StaggerLoc.CENTER_VCENTER][x]]
    gridXCenter[...] = x_par.reshape(x_par.size, 1, 1)

    gridYCenter = grid.get_coords(y)
    y_par = ycenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER_VCENTER][y]:grid.upper_bounds[ESMF.StaggerLoc.CENTER_VCENTER][y]]
    gridYCenter[...] = y_par.reshape(1, y_par.size, 1)

    gridZCenter = grid.get_coords(z)
    z_par = zcenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER_VCENTER][z]:grid.upper_bounds[ESMF.StaggerLoc.CENTER_VCENTER][z]]
    gridZCenter[...] = z_par.reshape(1, 1, z_par.size)

    # create grid corners in a slightly different manner to account for the bounds format common in CF-like files
    if corners:
        grid.add_coords([ESMF.StaggerLoc.CORNER_VFACE])
        lbx = grid.lower_bounds[ESMF.StaggerLoc.CORNER_VFACE][x]
        ubx = grid.upper_bounds[ESMF.StaggerLoc.CORNER_VFACE][x]
        lby = grid.lower_bounds[ESMF.StaggerLoc.CORNER_VFACE][y]
        uby = grid.upper_bounds[ESMF.StaggerLoc.CORNER_VFACE][y]
        lbz = grid.lower_bounds[ESMF.StaggerLoc.CORNER_VFACE][z]
        ubz = grid.upper_bounds[ESMF.StaggerLoc.CORNER_VFACE][z]

        gridXCorner = grid.get_coords(x, staggerloc=ESMF.StaggerLoc.CORNER_VFACE)
        for i0 in range(ubx - lbx - 1):
            gridXCorner[i0, :, :] = xcorner[i0+lbx, 0]
        gridXCorner[i0 + 1, :, :] = xcorner[i0+lbx, 1]

        gridYCorner = grid.get_coords(y, staggerloc=ESMF.StaggerLoc.CORNER_VFACE)
        for i1 in range(uby - lby - 1):
            gridYCorner[:, i1, :] = ycorner[i1+lby, 0]
        gridYCorner[:, i1 + 1, :] = ycorner[i1+lby, 1]

        gridZCorner = grid.get_coords(z, staggerloc=ESMF.StaggerLoc.CORNER_VFACE)
        for i2 in range(ubz - lbz - 1):
            gridZCorner[:, :, i2] = zcorner[i2+lbz, 0]
        gridZCorner[:, :, i2 + 1] = zcorner[i2+lbz, 1]

    # add an arbitrary mask
    if domask:
        mask = grid.add_item(ESMF.GridItem.MASK)
        mask[:] = 1
        mask[np.where((1.75 < gridXCenter.data < 2.25) &
                      (1.75 < gridYCenter.data < 2.25) &
                      (1.75 < gridZCenter.data < 2.25))] = 0

    # add arbitrary areas values
    if doarea:
        area = grid.add_item(ESMF.GridItem.AREA)
        area[:] = 5.0

    return grid

def grid_create_periodic_3d(nlon, nlat, nz, corners=False, domask=False):
    """
    :param nlons: number of longitude values at cell centers
    :param nlats: number of latitude values at cell centers
    :param nz: number of height values at cell centers
    :param corners: boolean to determine whether or not to add corner coordinates to this grid
    :param domask: boolean to determine whether to set an arbitrary mask or not
    :return: grid
    """
    [lon, lat, z] = [0, 1, 2]

    # Create arrays of center and corner values to emulate what would be read from a standard CF-like file
    # +1 because corners have one more than center
    lons = np.linspace(-180, 180, nlon + 1)
    loncorner = np.array([lons[0:-1], lons[1::]]).T
    loncenter = (loncorner[:, 1] + loncorner[:, 0]) / 2

    # +1 because corners have one more than center
    lats = np.linspace(-90, 90, nlat + 1)
    latcorner = np.array([lats[0:-1], lats[1::]]).T
    latcenter = (latcorner[:, 1] + latcorner[:, 0]) / 2

    # +1 because corners have one more than center
    zs = np.linspace(0, 10, nz + 1)
    zcorner = np.array([zs[0:-1], zs[1::]]).T
    zcenter = (zcorner[:, 1] + zcorner[:, 0]) / 2

    # create a grid given the number of grid cells in each dimension the center stagger location is allocated
    max_index = np.array([nlon, nlat, nz])
    grid = ESMF.Grid(max_index, num_peri_dims=1, staggerloc=[ESMF.StaggerLoc.CENTER])

    # set the grid coordinates using numpy arrays, parallel case is handled using grid bounds
    gridXCenter = grid.get_coords(lon)
    lon_par = loncenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER][lon]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][lon]]
    gridXCenter[...] = lon_par.reshape((lon_par.size, 1, 1))

    gridYCenter = grid.get_coords(lat)
    lat_par = latcenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER][lat]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][lat]]
    gridYCenter[...] = lat_par.reshape((1, lat_par.size, 1))

    gridZCenter = grid.get_coords(z)
    z_par = zcenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER][z]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][z]]
    gridZCenter[...] = z_par.reshape((1, 1, z_par.size))

    # create grid corners in a slightly different manner to account for the bounds format common in CF-like files
    if corners:
        grid.add_coords([ESMF.StaggerLoc.CORNER])
        lbx = grid.lower_bounds[ESMF.StaggerLoc.CORNER][lon]
        ubx = grid.upper_bounds[ESMF.StaggerLoc.CORNER][lon]
        lby = grid.lower_bounds[ESMF.StaggerLoc.CORNER][lat]
        uby = grid.upper_bounds[ESMF.StaggerLoc.CORNER][lat]
        lbz = grid.lower_bounds[ESMF.StaggerLoc.CORNER][z]
        ubz = grid.upper_bounds[ESMF.StaggerLoc.CORNER][z]

        gridXCorner = grid.get_coords(lon, staggerloc=ESMF.StaggerLoc.CORNER)
        for i0 in range(ubx - lbx - 1):
            gridXCorner[i0, :, :] = loncorner[i0+lbx, 0]
        gridXCorner[i0 + 1, :, :] = loncorner[i0+lbx, 1]

        gridYCorner = grid.get_coords(lat, staggerloc=ESMF.StaggerLoc.CORNER)
        for i1 in range(uby - lby - 1):
            gridYCorner[:, i1, :] = latcorner[i1+lby, 0]
        gridYCorner[:, i1 + 1, :] = latcorner[i1+lby, 1]

        gridZCorner = grid.get_coords(z, staggerloc=ESMF.StaggerLoc.CORNER)
        for i2 in range(ubz - lbz - 1):
            gridZCorner[:, :, i2] = zcorner[i2+lbz, 0]
        gridZCorner[:, :, i2 + 1] = zcorner[i2+lbz, 1]

    # add an arbitrary mask
    if domask:
        mask = grid.add_item(ESMF.GridItem.MASK)
        mask[:] = 1
        mask[np.where((1.75 <= gridXCenter.data < 2.25) &
                      (1.75 <= gridYCenter.data < 2.25) &
                      (1.75 <= gridZCenter.data < 2.25))] = 0

    return grid

def initialize_field_grid(field, domask=False, doarea=False):
    '''
    PRECONDITIONS: A Field has been created.
    POSTCONDITIONS: The 'field' has been initialized to an analytic 
                    field.
    RETURN VALUES: \n Field :: field \n
    '''
    if domask:
        mask = field.grid.get_item(ESMF.GridItem.MASK)

    # get the coordinate pointers and set the coordinates
    [x,y] = [0, 1]
    gridXCoord = field.grid.get_coords(0, ESMF.StaggerLoc.CENTER)
    gridYCoord = field.grid.get_coords(1, ESMF.StaggerLoc.CENTER)

    field.data[:] = 20.0 + gridXCoord**2 + gridXCoord*gridYCoord + gridYCoord**2

    if domask:
        field.data[mask == 0] = 0

    return field

def initialize_field_grid_periodic(field):
    '''
    PRECONDITIONS: A Field has been created as 'field' with a 'grid'
                   where coordinates have been set on both 
                   the center and corner stagger locations. \n
    POSTCONDITIONS: The 'field' has been initialized to an analytic 
                    field.\n
    RETURN VALUES: \n Field :: field \n
    '''
    DEG2RAD = 3.141592653589793/180.0

    # get the coordinate pointers and set the coordinates
    [x,y] = [0, 1]
    gridXCoord = field.grid.get_coords(x, ESMF.StaggerLoc.CENTER)
    gridYCoord = field.grid.get_coords(y, ESMF.StaggerLoc.CENTER)

    field.data[:] = 2.0 + np.cos(DEG2RAD*gridXCoord)**2 * \
                          np.cos(2.0*DEG2RAD*(90.0 - gridYCoord))

    return field

def initialize_field_grid_periodic_3d(field):
    '''
    PRECONDITIONS: A Field has been created as 'field' with a 'grid'
                   where coordinates have been set on both
                   the center and corner stagger locations. \n
    POSTCONDITIONS: The 'field' has been initialized to an analytic
                    field.\n
    RETURN VALUES: \n Field :: field \n
    '''
    DEG2RAD = 3.141592653589793/180.0

    # get the coordinate pointers and set the coordinates
    [x,y,z] = [0, 1, 2]
    gridXCoord = field.grid.get_coords(x, ESMF.StaggerLoc.CENTER)
    gridYCoord = field.grid.get_coords(y, ESMF.StaggerLoc.CENTER)
    gridZCoord = field.grid.get_coords(z, ESMF.StaggerLoc.CENTER)

    field.data[:] = 2.0 + np.cos(DEG2RAD*gridXCoord)**2 * \
                          np.cos(2.0*DEG2RAD*(90.0 - gridYCoord)) + \
                          gridZCoord*5.0

    return field

def initialize_field_grid_3d(field, domask=False):
    '''
    PRECONDITIONS: A Field has been created.
    POSTCONDITIONS: The 'field' has been initialized to an analytic 
                    field.
    RETURN VALUES: \n Field :: field \n
    '''
    if domask:
        mask = field.grid.get_item(ESMF.GridItem.MASK)

    # get the coordinate pointers and set the coordinates
    [x,y,z] = [0,1,2]
    gridXCoord = field.grid.get_coords(x, ESMF.StaggerLoc.CENTER_VCENTER)
    gridYCoord = field.grid.get_coords(y, ESMF.StaggerLoc.CENTER_VCENTER)
    gridZCoord = field.grid.get_coords(z, ESMF.StaggerLoc.CENTER_VCENTER)

    field.data[:]=20.0 + gridXCoord**2 + gridXCoord*gridYCoord + gridZCoord**2

    if domask:
        field.data[mask == 0] = 0

    return field

def compute_mass_grid(valuefield, dofrac=False, fracfield=None,
                      uninitval=422397696.):
    '''
    PRECONDITIONS: 'fracfield' contains the fractions of each cell
                   which contributed to a regridding operation involving
                   'valuefield.  'dofrac' is a boolean value that gives 
                   the option to not use the 'fracfield'.\n
    POSTCONDITIONS: The mass of the data field is computed.\n
    RETURN VALUES: float :: mass \n
    '''
    mass = 0.0
    areafield = ESMF.Field(valuefield.grid, name='areafield')
    areafield.get_area()

    ind = np.where(valuefield.data != uninitval)

    if dofrac:
        mass = np.sum(areafield.data[ind] * valuefield.data[ind] * fracfield.data[ind])
    else:
        mass = np.sum(areafield.data[ind] * valuefield.data[ind])

    return mass
