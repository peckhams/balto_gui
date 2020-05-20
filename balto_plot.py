"""
This module defines some plotting functions that are used by the
BALTO GUI app.  It should be included in the same directory as
"balto_gui.py" and the corresponding Jupyter notebook.
"""
#------------------------------------------------------------------------
#
#  Copyright (C) 2020.  Scott D. Peckham
#
#------------------------------------------------------------------------

import matplotlib.pyplot as plt
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
def show_grid_as_image( grid, long_name, extent=None,
                        cmap='rainbow',
                        stretch_name='hist_equal',
                        stretch_a = 1.0,
                        stretch_b = 1.0,
                        stretch_p = 1.0,
                        nodata_value=None,
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
        grid2[ w1 ] = nodata_value

    #----------------------------
    # Set up and show the image
    #----------------------------
    # figure = plt.figure(1, figsize=(xsize, ysize))
    fig, ax = plt.subplots( figsize=(xsize, ysize), dpi=dpi)
    im_title = long_name.replace('_', ' ').title()
    ax.set_title( im_title )
    ax.set_xlabel('Longitude [deg]')
    ax.set_ylabel('Latitude [deg]')

    im = ax.imshow(grid2, interpolation='nearest', cmap=cmap,
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







