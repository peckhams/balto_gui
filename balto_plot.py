"""
This module defines some plotting functions that are used by the
BALTO GUI app.  It should be included in the same directory as
"balto_gui.py" and the corresponding Jupyter notebook.
"""
#------------------------------------------------------------------------
#
#  Copyright (C) 2020.  Scott D. Peckham
#
#  Added use of cartopy in 2020-11 to 2020-12.
#
#------------------------------------------------------------------------

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

#------------------------------------------------------------------------
#
# plot_data()       # for x vs. y plots
#-----------------
# hist_equal()
# power_stretch1()
# power_stretch2()
# power_stretch3()
# log_stretch()
# stretch_grid()
# show_grid_as_image()   (used for balto_gui.show_grid() method)
#
#------------------------------------------------------------------------
def plot_data( x, y, xmin=None, xmax=None, ymin=None, ymax=None,
               x_name='x', x_units='', marker=',', 
               y_name='y', y_units='',
               x_size=8,   y_size=4):

    figure = plt.figure(1, figsize=(x_size, y_size))
    # fig, ax = plt.subplots( figsize=(x_size, y_size))

    # Set the plot point marker
    # https://matplotlib.org/3.1.1/api/markers_api.html
    # marker = ','  # pixel
    # marker = '.'  # point (small circle)
    # marker = 'o'  # circle
    # marker = '+'
    # marker = 'x'

    #if (ymin is None):
    #    ymin = y.min()
    #if (ymax is None):
    #    ymax = y.max()
    #if (ymax - ymin < 0.1):
    #    ymin = ymin - 0.5
    #    ymax = ymin + 0.5

    # x_name2 = x_name.replace('_', ' ').title()
    # y_name2 = y_name.replace('_', ' ').title()
        
    plt.plot( x, y, marker=marker)
    plt.xlabel( x_name + ' [' + x_units + ']' )
    plt.ylabel( y_name + ' [' + y_units + ']' )
    
    plt.ylim( ymin, ymax )
    plt.xlim( xmin, xmax )
    #-------------------------------------
    # This may be necessary depending on
    # the data type of ymin, ymax
    #-------------------------------------
    ## plt.ylim( np.array([ymin, ymax]) )
    ## plt.xlim( np.array([xmin, xmax]) )
    plt.show()

#   plot_data()
#------------------------------------------------------------------------
def histogram_equalize( grid, PLOT_NCS=False):

    #  https://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
    (hist, bin_edges) = np.histogram( grid, bins=256)
    # hmin = hist.min()
    # hmax = hist.max()

    cs  = hist.cumsum()
    ncs = (cs - cs.min()) / (cs.max() - cs.min())
    ncs.astype('uint8');
    ############## ncs.astype('uint8') # no semi-colon at end ??????????
    if (PLOT_NCS):
        plt.plot( ncs )

    flat = grid.flatten()
    flat2 = np.uint8( 255 * (flat - flat.min()) / (flat.max() - flat.min()) )
    grid2 = ncs[ flat2 ].reshape( grid.shape )
    return grid2

#   histogram_equalize()
#------------------------------------------------------------------------
def power_stretch1( grid, p ):
    return grid**p
    
#   power_stretch1()
#------------------------------------------------------------------------
def power_stretch2( grid, a=1000, b=0.5):
    # Note: Try a=1000 and b=0.5
    gmin = grid.min()
    gmax = grid.max()
    norm = (grid - gmin) / (gmax - gmin)
    return (1 - (1 + a * norm)**(-b))
    
#   power_stretch2()
#------------------------------------------------------------------------
def power_stretch3( grid, a=1, b=2):
    # Note:  Try a=1, b=2 (shape of a quarter circle)
    gmin = grid.min()
    gmax = grid.max()
    norm = (grid - gmin) / (gmax - gmin)
    return (1 - (1 - norm**a)**b)**(1/b)
    
#   power_stretch3()
#------------------------------------------------------------------------
def log_stretch( grid, a=1 ):
    return np.log( (a * grid) + 1 )
    
#   log_stretch()
#------------------------------------------------------------------------
def stretch_grid( grid, stretch, a=1, b=2, p=0.5 ):

    if   (stretch == 'power_stretch1'):
        # Try:  p = 0.3   
        grid2 = power_stretch1( grid, p)
    elif (stretch == 'power_stretch2'):
        # Try:  a=1000, b=0.5.
        grid2 = power_stretch2( grid, a=a, b=b )
    elif (stretch == 'power_stretch3'):
        # Try:  a=1, b=2.
        grid2 = power_stretch3( grid, a=a, b=b)    
    elif (stretch == 'log_stretch'):
        grid2 = log_stretch( grid, a=a )
    elif (stretch == 'hist_equal'):
        grid2 = histogram_equalize( grid, PLOT_NCS=False)
    else:
        print('SORRY, Unknown stretch =', stretch)
        return None

    return grid2
 
#   stretch_grid()
#------------------------------------------------------------------------
def get_map_projection( proj_name,
        central_longitude=0.0, central_latitude=0.0,
        false_easting=0.0, false_northing=0.0, globe=None,
        standard_parallels=(20.0, 50.0),
        scale_factor=None,
        min_latitude=-80.0, max_latitude=84.0,
        true_scale_latitude=None, latitude_true_scale=None,  ### BOTH
        secant_latitudes=None,
        pole_longitude=0.0, pole_latitude=90.0,
        central_rotated_longitude=0.0, sweep_axis='y',
        satellite_height=35785831, cutoff=-30, approx=None,
        southern_hemisphere=False, zone=15):   #### numeric UTM zone

    proj_name = proj_name.lower()
    
    if (proj_name == 'albersequalarea'):
        proj = ccrs.AlbersEqualArea(central_longitude=central_longitude,
                    central_latitude=central_latitude, 
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe,
                    standard_parallels=standard_parallels)
    elif (proj_name == 'azimuthalequidistant'):
        proj = ccrs.AzimuthalEquidistant(central_longitude=central_longitude,
                    central_latitude=central_latitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)
    elif (proj_name == 'equidistantconic'):
        proj = ccrs.EquidistantConic(central_longitude=central_longitude,
                    central_latitude=central_latitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe,
                    standard_parallels=standard_parallels)
    elif (proj_name == 'lambertconformal'):
        proj = ccrs.LambertConformal(central_longitude=-96.0,      ##########
                    central_latitude=39.0,                         ##########
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe,
                    secant_latitudes=None,
                    standard_parallels=None,   ## default: (33,45)
                    cutoff=cutoff)
    elif (proj_name == 'lambertcylindrical'):
        proj = ccrs.LambertCylindrical(central_longitude=central_longitude)
    elif (proj_name == 'mercator'):
        proj = ccrs.Mercator(central_longitude=central_longitude,
                    min_latitude=min_latitude, max_latitude=max_latitude,
                    latitude_true_scale=latitude_true_scale,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe,
                    scale_factor=None)   #########
    elif (proj_name == 'miller'):
        proj = ccrs.Miller(central_longitude=central_longitude, globe=globe)    
    elif (proj_name == 'mollweide'):
        proj = ccrs.Mollweide(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)
    elif (proj_name == 'orthographic'):
        proj = ccrs.Orthographic(central_longitude=central_longitude,
                    central_latitude=central_latitude, globe=globe)
    elif (proj_name == 'robinson'):
        proj = ccrs.Robinson(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)    
    elif (proj_name == 'sinusoidal'):
        proj = ccrs.Sinusoidal(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)
    elif (proj_name == 'stereographic'):    
        proj = ccrs.Stereographic(central_latitude=central_latitude,
                    central_longitude=central_longitude, 
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe,
                    true_scale_latitude=true_scale_latitude,
                    scale_factor=scale_factor)
    elif (proj_name == 'transversemercator'):
        proj = ccrs.TransverseMercator(central_longitude=central_longitude,
                    central_latitude=central_latitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe,
                    scale_factor=1.0,  ##########
                    approx=approx)
    elif (proj_name == 'utm'):
        proj = ccrs.UTM(zone, southern_hemisphere=southern_hemisphere, globe=globe)
    elif (proj_name == 'interruptedgoodehomolosine'):
        proj = ccrs.InterruptedGoodeHomolosine(central_longitude=central_longitude,
                    globe=globe)    
    elif (proj_name == 'rotatedpole'):
        proj = ccrs.RotatedPole(pole_longitude=pole_longitude,
                    pole_latitude=pole_latitude, globe=globe,
                    central_rotated_longitude=central_rotated_longitude)     
    elif (proj_name == 'osgb'):
        proj = ccrs.OSGB(approx=approx)    
    elif (proj_name == 'europp'):
        proj = ccrs.EuroPP    
    elif (proj_name == 'geostationary'):
        proj = ccrs.Geostationary(central_longitude=central_longitude,
                    satellite_height=satellite_height,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe,
                    sweep_axis=sweep_axis)
    elif (proj_name == 'nearsideperspective'):
        proj = ccrs.NearsidePerspective(central_longitude=central_longitude,
                    central_latitude=central_latitude,
                    satellite_height=satellite_height,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)       
    elif (proj_name == 'eckerti'):
        proj = ccrs.EckertI(central_longitude=central_longitude, 
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)    
    elif (proj_name == 'eckertii'):
        proj = ccrs.EckertII(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)
    elif (proj_name == 'eckertiii'):
        proj = ccrs.EckertIII(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)
    elif (proj_name == 'eckertiv'):
        proj = ccrs.EckertIV(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)
    elif (proj_name == 'eckertv'):
        proj = ccrs.EckertV(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)    
    elif (proj_name == 'eckertvi'):
        proj = ccrs.EckertVI(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe) 
    elif (proj_name == 'equalearth'):
        proj = ccrs.EqualEarth(central_longitude=central_longitude,
                    false_easting=false_easting,
                    false_northing=false_northing, globe=globe)    
    elif (proj_name == 'gnomonic'):
        proj = ccrs.Gnomonic(central_latitude=central_latitude,
                    central_longitude=central_longitude, globe=globe)
    elif (proj_name == 'lambertazimuthalequalarea'):
        proj = ccrs.LambertAzimuthalEqualArea(central_longitude=central_longitude,
                    central_latitude=central_latitude, globe=globe,
                    false_easting=false_easting,
                    false_northing=false_northing)
    elif (proj_name == 'northpolarstereo'):
        proj = ccrs.NorthPolarStereo(central_longitude=central_longitude,
                    true_scale_latitude=true_scale_latitude, globe=globe)  
    elif (proj_name == 'osni'):
        proj = ccrs.OSNI(approx=approx)    
    elif (proj_name == 'southpolarstereo'):
        proj = ccrs.SouthPolarStereo(central_longitude=central_longitude,
                    true_scale_latitude=true_scale_latitude, globe=globe)
    else:
        # This is same as "Geographic coordinates"
        proj = ccrs.PlateCarree(central_longitude=central_longitude,
                    globe=globe)
                                             
    return proj    

#   get_map_projection()
#------------------------------------------------------------------------
def show_grid_as_image( grid, long_name, extent=None,
                        cmap='rainbow',
                        stretch_name='hist_equal',
                        stretch_a = 1.0,
                        stretch_b = 1.0,
                        stretch_p = 1.0,
                        nodata_value=None,
                        interp_method='nearest',
                        ## crs='platecarree',  # for Geographic coordinates
                        proj_name='mercator',
                        projection=None,
                        NO_SHOW=False, im_file=None,
                        ## stretch='power_stretch3',
                        xsize=8, ysize=8, dpi=None): 

    # Note:  extent = [minlon, maxlon, minlat, maxlat]
    #        See get_map_bounds() in balto_gui.py.

    #-------------------------
    # Other color map names
    #--------------------------------------------
    # hsv, jet, gist_rainbow (reverse rainbow),
    # gist_ncar, gist_stern
    #--------------------------------------------    

    #------------------------------------------
    # Replace nodata value before the stretch
    #------------------------------------------
    grid2 = grid.copy()
    if (nodata_value is not None):
        w1    = (grid2 == nodata_value)
        w2    = np.invert( w1 )
        gmin  = min(grid2[w2])
        grid2[ w1 ] = gmin
    
    #---------------------------------------------
    # Apply stretch function to enhance contrast
    #---------------------------------------------
    # grid2 = stretch_grid( grid, stretch='power_stretch1', p=0.4)
    # grid2 = stretch_grid( grid, stretch='power_stretch2', a=1000, b=0.5)
    # grid2 = stretch_grid( grid, stretch='power_stretch3', a=1, b=2)
    # grid2 = stretch_grid( grid, stretch='log_stretch', a=1)    
    grid2 = stretch_grid( grid2, stretch=stretch_name, a=stretch_a,
                          b=stretch_b, p=stretch_p) 

    #-----------------------------------------------
    # Get new min and max, before replacing nodata
    #-----------------------------------------------
    gmin = grid2.min()
    gmax = grid2.max()
    # print('gmin =', gmin)
    # print('gmax =', gmax)
    # print('shape =', grid2.shape)

    #------------------------------------------
    # Replace the nodata values after stretch
    #------------------------------------------
    if (nodata_value is not None):
        grid2[ w1 ] = np.nan   # 2020-12-11
        ### grid2[ w1 ] = nodata_value

    #-------------------------------------------
    # Create figure and axes (without cartopy)
    #--------------------------------------------
    # balto_crs  = None
    # fig, ax = plt.subplots( figsize=(xsize, ysize), dpi=dpi )
    #----------------------------------------------------------
    # balto_crs  = None
    # balto_proj = None
    # fig = plt.figure( figsize=(xsize, ysize), dpi=dpi )
    # ax  = fig.add_subplot(1,1,1, projection=balto_proj)
    ## ax.set_extent( extent, crs=balto_crs )  ##### NOT WORKING

    #--------------------------------------------
    # Set the CRS (Coordinate Reference System)
    #-------------------------------------------------------
    # See:  https://scitools.org.uk/cartopy/docs/latest/
    #               tutorials/understanding_transform.html
    #-------------------------------------------------------
    use_cartopy = False
    if (use_cartopy):
        balto_crs = ccrs.PlateCarree()   # For Geographic lon/lat coordinates.
    
        #-------------------------
        # Set the map projection
        #--------------------------------------------
        # extent = [minlon, maxlon, minlat, maxlat]
        #--------------------------------------------
        center_lon = (extent[0] + extent[1]) / 2.0
        center_lat = (extent[2] + extent[3]) / 2.0
        min_lat    = extent[2]
        max_lat    = extent[3]
        print('Extent =', extent )

        if (projection is not None):
            balto_proj = projection
        else:
            #------------------------------------------------
            # This option requires using parameter defaults
            #------------------------------------------------
            proj_name = proj_name.lower()
            balto_proj = get_map_projection(proj_name, globe=None,
                             central_longitude=center_lon,
                             central_latitude=center_lat,
                             false_easting=0.0, false_northing=0.0,
                             standard_parallels=(20.0, 50.0), scale_factor=None,
                             min_latitude=-80.0, max_latitude=84.0,
                             true_scale_latitude=None, latitude_true_scale=None,  ### BOTH
                             secant_latitudes=None,
                             pole_longitude=0.0, pole_latitude=90.0,
                             central_rotated_longitude=0.0, sweep_axis='y',
                             satellite_height=35785831, cutoff=-30, approx=None,
                             southern_hemisphere=False, zone=15)  ######
                             
        #------------------------------------------------
        # Create figure and axes (matplotlib + cartopy)
        #------------------------------------------------
        # First 3 args to subplot: ncols, nrows, index for the subplots
        fig = plt.figure( figsize=(xsize, ysize), dpi=dpi )
        ax  = fig.add_subplot(1,1,1, projection=balto_proj)
        ax.set_extent( extent, crs=balto_crs )
        ## ax.set_xlim([extent[0], extent[1]])
        ## ax.set_ylim([extent[2], extent[3]])
    else:  
        #------------------------------------------------
        # Create figure and axes (matplotlib + cartopy)
        #------------------------------------------------
        # First 3 args to subplot: ncols, nrows, index for the subplots
        fig = plt.figure( figsize=(xsize, ysize), dpi=dpi )
        ax  = fig.add_subplot(1,1,1)
        ## ax.set_extent( extent)
        ax.set_xlim([extent[0], extent[1]])
        ax.set_ylim([extent[2], extent[3]])
        
    GRIDLINES = use_cartopy  ######
    if (GRIDLINES):
        ## DRAW_LABELS = (projection == 'platecarree')  # (unsupported otherwise)
        DRAW_LABELS = False   # Now done by other means
        gl = ax.gridlines(crs=balto_crs, draw_labels=DRAW_LABELS, linewidth=2,
                          color='gray', alpha=0.5, linestyle='--')
    # ax.add_feature(cfeature.COASTLINE)  # placed wrong ###########
    # ax.add_feature(cfeature.COASTLINE, extent=extent) # no extent keyword  
    # ax.add_feature(cfeature.BORDERS)
    # ax.add_feature(cfeature.RIVERS)
    # ax.add_feature(cfeature.LAND)    # (raster?)
    # ax.add_feature(cfeature.OCEAN)   # (raster?)
    # ax.add_feature(cfeature.LAKES)   # (raster?)
              
    #----------------------------
    # Set title and axis labels
    #----------------------------
    im_title = long_name.replace('_', ' ').title()
    ax.set_title( im_title )
    ax.set_xlabel('Longitude [deg]')
    ax.set_ylabel('Latitude [deg]')
    #----------------------------------------------------
    # Need next 2 lines as work-around for cartopy bug
    # that prevents axis labels from showing.
    # https://stackoverflow.com/questions/35479508/
    # cartopy-set-xlabel-set-ylabel-not-ticklabels
    #----------------------------------------------------
    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())
    ## ax.set_xticks(ax.get_xticks()[abs(ax.get_xticks())<=360])
    ## ax.set_yticks(ax.get_yticks()[abs(ax.get_yticks())<=90])

    #------------------------------------
    # New code to use cartopy (2020-11)
    #------------------------------------
    ## balto_crs = ccrs.PlateCarree()
    ## balto_crs = ccrs.PlateCarree(central_longitude=center_lon)
#     im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
#                    vmin=gmin, vmax=gmax, extent=extent)
#------------------------------------------------------------------------------
# USE THIS BLOCK
#     if (use_cartopy):
#        im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
#                       vmin=gmin, vmax=gmax, extent=extent, transform=balto_crs)
#------------------------------------------------------------------------------
#     im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
#                    vmin=gmin, vmax=gmax, transform=balto_crs)
                       
    #----------------------------------     
    # Old code, before use of cartopy
    #----------------------------------
    # im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
    #                vmin=gmin, vmax=gmax)                   
    # im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
    #                vmin=gmin, vmax=gmax, extent=extent)

    if (use_cartopy):
       im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
                      vmin=gmin, vmax=gmax, extent=extent, transform=balto_crs)
    else:
        im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
                       vmin=gmin, vmax=gmax, extent=extent)
   
    #--------------------------------------------------------        
    # NOTE!  Must save before "showing" or get blank image.
    #        File format is inferred from extension.
    #        e.g. TMP_Image.png, TMP_Image.jpg.
    #--------------------------------------------------------
    if (im_file is not None):  
        plt.savefig( im_file )
    if not(NO_SHOW):
        plt.show()
 
    plt.close()

#   show_grid_as_image()
#------------------------------------------------------------------------
def show_grid_as_image_OLD( grid, long_name, extent=None,
                        cmap='rainbow',
                        stretch_name='hist_equal',
                        stretch_a = 1.0,
                        stretch_b = 1.0,
                        stretch_p = 1.0,
                        nodata_value=None,
                        interp_method='nearest',
                        ## crs='platecarree',  # for Geographic coordinates
                        proj_name='mercator',
                        projection=None,
                        NO_SHOW=False, im_file=None,
                        ## stretch='power_stretch3',
                        xsize=8, ysize=8, dpi=None): 

    # Note:  extent = [minlon, maxlon, minlat, maxlat]
    #        See get_map_bounds() in balto_gui.py.

    #-------------------------
    # Other color map names
    #--------------------------------------------
    # hsv, jet, gist_rainbow (reverse rainbow),
    # gist_ncar, gist_stern
    #--------------------------------------------    

    #------------------------------------------
    # Replace nodata value before the stretch
    #------------------------------------------
    grid2 = grid.copy()
    if (nodata_value is not None):
        w1    = (grid2 == nodata_value)
        w2    = np.invert( w1 )
        gmin  = min(grid2[w2])
        grid2[ w1 ] = gmin
    
    #---------------------------------------------
    # Apply stretch function to enhance contrast
    #---------------------------------------------
    # grid2 = stretch_grid( grid, stretch='power_stretch1', p=0.4)
    # grid2 = stretch_grid( grid, stretch='power_stretch2', a=1000, b=0.5)
    # grid2 = stretch_grid( grid, stretch='power_stretch3', a=1, b=2)
    # grid2 = stretch_grid( grid, stretch='log_stretch', a=1)    
    grid2 = stretch_grid( grid2, stretch=stretch_name, a=stretch_a,
                          b=stretch_b, p=stretch_p) 

    #-----------------------------------------------
    # Get new min and max, before replacing nodata
    #-----------------------------------------------
    gmin = grid2.min()
    gmax = grid2.max()
    
    #------------------------------------------
    # Replace the nodata values after stretch
    #------------------------------------------
    if (nodata_value is not None):
        grid2[ w1 ] = np.nan   # 2020-12-11
        ### grid2[ w1 ] = nodata_value

    #-------------------------------------------
    # Create figure and axes (without cartopy)
    #--------------------------------------------
    # balto_crs  = None
    # fig, ax = plt.subplots( figsize=(xsize, ysize), dpi=dpi )
    #----------------------------------------------------------
    # balto_crs  = None
    # balto_proj = None
    # fig = plt.figure( figsize=(xsize, ysize), dpi=dpi )
    # ax  = fig.add_subplot(1,1,1, projection=balto_proj)
    ## ax.set_extent( extent, crs=balto_crs )  ##### NOT WORKING

    #--------------------------------------------
    # Set the CRS (Coordinate Reference System)
    #-------------------------------------------------------
    # See:  https://scitools.org.uk/cartopy/docs/latest/
    #               tutorials/understanding_transform.html
    #-------------------------------------------------------
    balto_crs = ccrs.PlateCarree()   # For Geographic lon/lat coordinates.
    
    #-------------------------
    # Set the map projection
    #--------------------------------------------
    # extent = [minlon, maxlon, minlat, maxlat]
    #--------------------------------------------
    center_lon = (extent[0] + extent[1]) / 2.0
    center_lat = (extent[2] + extent[3]) / 2.0
    min_lat    = extent[2]
    max_lat    = extent[3]
    print('Extent =', extent )

    if (projection is not None):
        balto_proj = projection
    else:
        #------------------------------------------------
        # This option requires using parameter defaults
        #------------------------------------------------
        proj_name = proj_name.lower()
        balto_proj = get_map_projection(proj_name, globe=None,
                         central_longitude=center_lon,
                         central_latitude=center_lat,
                         false_easting=0.0, false_northing=0.0,
                         standard_parallels=(20.0, 50.0), scale_factor=None,
                         min_latitude=-80.0, max_latitude=84.0,
                         true_scale_latitude=None, latitude_true_scale=None,  ### BOTH
                         secant_latitudes=None,
                         pole_longitude=0.0, pole_latitude=90.0,
                         central_rotated_longitude=0.0, sweep_axis='y',
                         satellite_height=35785831, cutoff=-30, approx=None,
                         southern_hemisphere=False, zone=15)  ######

    #------------------------------------------------
    # Create figure and axes (matplotlib + cartopy)
    #------------------------------------------------
    # First 3 args to subplot: ncols, nrows, index for the subplots
    fig = plt.figure( figsize=(xsize, ysize), dpi=dpi )
    ax  = fig.add_subplot(1,1,1, projection=balto_proj)
    ax.set_extent( extent, crs=balto_crs )
    ## ax.set_xlim([extent[0], extent[1]])
    ## ax.set_ylim([extent[2], extent[3]])

    GRIDLINES = True  ######
    if (GRIDLINES):
        ## DRAW_LABELS = (projection == 'platecarree')  # (unsupported otherwise)
        DRAW_LABELS = False   # Now done by other means
        gl = ax.gridlines(crs=balto_crs, draw_labels=DRAW_LABELS, linewidth=2,
                          color='gray', alpha=0.5, linestyle='--')
    # ax.add_feature(cfeature.COASTLINE)  # placed wrong ###########
    # ax.add_feature(cfeature.COASTLINE, extent=extent) # no extent keyword  
    # ax.add_feature(cfeature.BORDERS)
    # ax.add_feature(cfeature.RIVERS)
    # ax.add_feature(cfeature.LAND)    # (raster?)
    # ax.add_feature(cfeature.OCEAN)   # (raster?)
    # ax.add_feature(cfeature.LAKES)   # (raster?)
              
    #----------------------------
    # Set title and axis labels
    #----------------------------
    im_title = long_name.replace('_', ' ').title()
    ax.set_title( im_title )
    ax.set_xlabel('Longitude [deg]')
    ax.set_ylabel('Latitude [deg]')
    #----------------------------------------------------
    # Need next 2 lines as work-around for cartopy bug
    # that prevents axis labels from showing.
    # https://stackoverflow.com/questions/35479508/
    # cartopy-set-xlabel-set-ylabel-not-ticklabels
    #----------------------------------------------------
    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())
    ## ax.set_xticks(ax.get_xticks()[abs(ax.get_xticks())<=360])
    ## ax.set_yticks(ax.get_yticks()[abs(ax.get_yticks())<=90])

    #------------------------------------
    # New code to use cartopy (2020-11)
    #------------------------------------
    ## balto_crs = ccrs.PlateCarree()
    ## balto_crs = ccrs.PlateCarree(central_longitude=center_lon)
#     im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
#                    vmin=gmin, vmax=gmax, extent=extent)
#------------------------------------------------------------------------------
#    im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
#                   vmin=gmin, vmax=gmax, extent=extent, transform=balto_crs)
#------------------------------------------------------------------------------
#     im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
#                    vmin=gmin, vmax=gmax, transform=balto_crs)
                       
    #----------------------------------     
    # Old code, before use of cartopy
    #----------------------------------
    # im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
    #                vmin=gmin, vmax=gmax)                   
    im = ax.imshow(grid2, interpolation=interp_method, cmap=cmap,
                   vmin=gmin, vmax=gmax, extent=extent)

    #--------------------------------------------------------        
    # NOTE!  Must save before "showing" or get blank image.
    #        File format is inferred from extension.
    #        e.g. TMP_Image.png, TMP_Image.jpg.
    #--------------------------------------------------------
    if (im_file is not None):  
        plt.savefig( im_file )
    if not(NO_SHOW):
        plt.show()
 
    plt.close()

#   show_grid_as_image_OLD()
#------------------------------------------------------------------------






