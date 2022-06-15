"""
This module defines a class called "balto_gui" that can be used to
create a graphical user interface (GUI) for downloading data from
OpenDAP servers from and into a Jupyter notebook.  If used with Binder,
this GUI runs in a browser window and does not require the user to
install anything on their computer.  However, this module should be
included in the same directory as the Jupyter notebook.
"""
#------------------------------------------------------------------------
#
#  Copyright (C) 2020-2022.  Scott D. Peckham
#
#------------------------------------------------------------------------

from ipyleaflet import Map, basemaps, FullScreenControl
from ipyleaflet import MeasureControl, Rectangle
## from ipyleaflet import ScaleControl  # (doesn't work)
from traitlets import Tuple
## import ipyleaflet as ipyl

import ipywidgets as widgets
from ipywidgets import Layout
from IPython.display import display, HTML
## from IPython.core.display import display
## from IPython.lib.display import display

import pydap.client  # (for open_url, etc.)
import requests      # (used by get_filenames() )
import json
import datetime      # (used by get_duration() )
import copy
import numpy as np
import balto_plot as bp

#------------------------------------------------------------------------
#
#  class balto_gui
#      __init__()
#      pix_str()
#      show_gui()
#      make_acc_gui()
#      make_tab_gui()
#      make_data_panel()
#      reset_data_panel()
#      make_map_panel()
#      make_dates_panel()
#      make_download_panel()
#      make_prefs_panel()
#      #--------------------------
#      get_map_bounds()
#      replace_map_bounds()
#      replace_map_bounds2()
#      update_map_bounds()
#      zoom_out_to_new_bounds()
#      --------------------------
#      get_url_dir_filenames()
#      update_filename_list()
#      get_opendap_file_url()
#      open_dataset()
#      update_data_panel()
#      --------------------------
#      update_var_info()
#      get_all_var_shortnames()
#      get_all_var_longnames()
#      get_all_var_units()
#      --------------------------
#      get_var_shortname()
#      get_var_longname()
#      get_var_units()
#      get_var_shape()
#      get_var_dimensions()
#      get_var_dtype()
#      get_var_attributes()
#      get_var_time_attributes()
#      -------------------------------
#      update_datetime_panel()
#      get_years_from_time_since()
#      clear_datetime_notes()
#      append_datetime_notes()
#      list_to_string()
#      -------------------------------
#      pad_with_zeros()
#      get_actual_time_units()
#      get_time_delta_str()
#      get_datetime_obj_from_str()
#      get_datetime_obj_from_one_str()
#      get_start_datetime_obj()
#      get_end_datetime_obj()
#      get_dt_from_datetime_str()
#      split_datetime_str()
#      split_date_str()
#      split_time_str()
#      get_datetime_from_time_since()
#      get_time_since_from_datetime()
#      get_month_difference()
#      -------------------------------
#      get_new_time_index_range()
#      get_new_lat_index_range()
#      get_new_lon_index_range()
#      -------------------------------
#      get_duration()  ## not used yet
#      ----------------------------
#      get_download_format()
#      clear_download_log()
#      append_download_log()
#      print_user_choices()
#      download_data()
#      show_grid()
#      -------------------------------
#      get_opendap_package()    # (in prefs panel)
#      ----------------------------
#      get_abbreviated_var_name()
#      get_possible_svo_names()
#
#------------------------------
# Example GES DISC opendap URL
#------------------------------
# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHHE.05/2014/091/
# 3B-HHR-E.MS.MRG.3IMERG.20140401-S000000-E002959.0000.V05B.HDF5.nc
# ?HQprecipitation[1999:2200][919:1049],lon[1999:2200],lat[919:1049]

#------------------------------------------------------------------------
class balto_gui:
    #--------------------------------------------------------------------
    def __init__(self):

        self.version  = '0.5'
        self.user_var = None
        self.default_url_dir = 'http://test.opendap.org/dap/data/nc/'
        self.timeout_secs = 60  # (seconds)
        #----------------------------------------------------------
        # "full_box_width" = (label_width + widget_width)
        # gui_width = left_label_width + mid_width + button_width 
        # The 2nd, label + widget box, is referred to as "next".
        # (2 * half_widget_width) + left_label + next_label = 540
        #----------------------------------------------------------       
        self.gui_width         = 680
        self.left_label_width  = 120
        self.next_label_width  = 50
        self.all_label_width   = 170
        self.full_box_width    = 540
        self.widget_width      = (self.full_box_width - self.left_label_width)
        # self.half_widget_width = (self.full_box_width - self.all_label_width)/2
        # self.half_widget_width = 183
        self.left_widget_width = 230
        self.next_widget_width = 136
        self.left_box_width    = (self.left_label_width + self.left_widget_width)
        self.next_box_width    = (self.next_label_width + self.next_widget_width)
        self.button_width      = 70   # big enough for "Reset"
        #-----------------------------------------------------
        self.map_width         = (self.gui_width - 40)
        self.map_height        = 230  # was 250
        self.map_center_init   = (20.0, 0)
        self.add_fullscreen_control = True
        self.add_scale_control      = False   # (doesn't work)
        self.add_measure_control    = True
        #-----------------------------------------------------
        self.gui_width_px  = self.pix_str( self.gui_width )
        self.map_width_px  = self.pix_str( self.map_width )
        self.map_height_px = self.pix_str( self.map_height )
        #-----------------------------------------------------                     
        self.date_width_px = '240px'
        self.time_width_px = '180px'
        self.hint_width_px = '120px'
        #---------------------------------------------------
        self.log_box_width_px  = self.pix_str( self.full_box_width )
        self.log_box_height_px = '200px'
        #---------------------------------------------------
        # These styles are used to control width of labels
        # self.init_label_style is the initial default.
        #---------------------------------------------------
        llw_px = self.pix_str( self.left_label_width )
        nlw_px = self.pix_str( self.next_label_width )
        self.init_label_style = {'description_width': 'initial'}
        self.left_label_style = {'description_width': llw_px}
        self.next_label_style = {'description_width': nlw_px}
        self.date_style       = {'description_width': '70px'}
        self.time_style       = {'description_width': '70px'}
        
    #   __init__()
    #--------------------------------------------------------------------
    def pix_str(self, num):
        return str(num) + 'px'
    #--------------------------------------------------------------------
    def show_gui(self, ACC_STYLE=False, SHOW_MAP=True):

        #------------------------------------------------------        
        # Encountered a problem where there was some problem
        # with ipyleaflets (used for the map panel) that
        # prevented any part of the GUI from being displayed.
        # The SHOW_MAP flag helps to test for this problem.
        #------------------------------------------------------

        #------------------------------------   
        # Create & display the complete GUI
        #-----------------------------------
        if (ACC_STYLE):
            self.make_acc_gui()
        else:
            # Use the TAB style
            self.make_tab_gui( SHOW_MAP=SHOW_MAP)

        gui_output = widgets.Output()
        display(self.gui, gui_output)
  
    #   show_gui()
    #--------------------------------------------------------------------
    def make_acc_gui(self):

        gui_width_px = self.gui_width_px
        
        self.make_data_panel()
        self.make_map_panel()
        self.make_datetime_panel()
        self.make_download_panel()
        self.make_prefs_panel()
        #---------------------------
        p0 = self.data_panel
        p1 = self.map_panel
        p2 = self.datetime_panel
        p3 = self.download_panel
        p4 = self.prefs_panel
        #---------------------------
        p0_title = 'Browse Data'
        p1_title = 'Spatial Extent'
        p2_title = 'Date Range'
        p3_title = 'Download Data'
        p4_title = 'Settings'
    
        #-------------------------------------------------------
        # selected_index=None causes all cells to be collapsed
        #-------------------------------------------------------        
        acc = widgets.Accordion( children=[p0, p1, p2, p3, p4],
                                 selected_index=None,
                                 layout=Layout(width=gui_width_px) )
        acc.set_title(0, p0_title)
        acc.set_title(1, p1_title)
        acc.set_title(2, p2_title)
        acc.set_title(3, p3_title)
        acc.set_title(4, p4_title)

        # title  = 'BALTO User Interface'
        # L_tags = "<b><font size=5>"
        # R_tags = "</font></b>"
        # heading = (L_tags + title + R_tags)
        pad  = self.get_padding(1, HORIZONTAL=False)  # 1 lines
        head = widgets.HTML(value=f"<b><font size=4>BALTO User Interface</font></b>")
        # head = widgets.Label('BALTO User Interface')
        # self.gui = widgets.VBox([pad, head, acc])  # (top padding
        self.gui = widgets.VBox([head, acc])   # (no top padding)
        
    #   make_acc_gui()
    #--------------------------------------------------------------------
    def make_tab_gui(self, SHOW_MAP=True):

        #---------------------------------------------------------
        # If there is a problem with ipyleaflet, it can prevent
        # any part of the GUI from being displayed.  You can
        # set SHOW_MAP=False to remove the map to test for this.
        #---------------------------------------------------------
        gui_width_px = self.gui_width_px
        
        self.make_data_panel()
        self.make_map_panel( SHOW_MAP=SHOW_MAP )
        self.make_datetime_panel()
        self.make_download_panel()
        self.make_prefs_panel()
        #---------------------------
        p0 = self.data_panel
        p1 = self.map_panel
        p2 = self.datetime_panel
        p3 = self.download_panel
        p4 = self.prefs_panel
        #---------------------------
        p0_title = 'Browse Data'
        p1_title = 'Spatial Extent'
        p2_title = 'Date Range'
        p3_title = 'Download Data'
        p4_title = 'Settings'
          
        #-------------------------------------------------------
        # selected_index=0 shows Browse Data panel
        #-------------------------------------------------------
        tab = widgets.Tab( children=[p0, p1, p2, p3, p4],        
                                 selected_index=0,
                                 layout=Layout(width=gui_width_px) )
        tab.set_title(0, p0_title)
        tab.set_title(1, p1_title)
        tab.set_title(2, p2_title)
        tab.set_title(3, p3_title)
        tab.set_title(4, p4_title)
        #### tab.titles = [str(i) for i in range(len(children))]
        
        # title  = 'BALTO User Interface'
        # L_tags = "<b><font size=5>"
        # R_tags = "</font></b>"
        # heading = (L_tags + title + R_tags)
        pad  = self.get_padding(1, HORIZONTAL=False)  # 1 lines
        head = widgets.HTML(value=f"<b><font size=5>BALTO User Interface</font></b>")
        # head = widgets.Label('BALTO User Interface')
        ## self.gui = widgets.VBox([pad, head, acc])
        self.gui = widgets.VBox([head, tab])   # (no padding above)

    #   make_tab_gui()
    #--------------------------------------------------------------------
    def get_padding(self, n, HORIZONTAL=True):
 
        #-------------------------------       
        # Get some white space padding
        #-------------------------------
        if (HORIZONTAL):
            #--------------------------------
            # Use overloaded multiplication
            #--------------------------------
            ## s  = (' ' * n)  # overloaded multiplication
            s  = "<p>" + ('&nbsp;' * n) + "</p>"
            pad = widgets.HTML( value=s )
        else:
            s = ("<br>" * n)
            pad = widgets.HTML( value=s )
        return pad
        
    #   get_padding()
    #--------------------------------------------------------------------
    def make_data_panel(self):

        #-----------------------------------
        # Browse data on an OpenDAP server
        #-----------------------------------
        left_style     = self.left_label_style
        next_style     = self.next_label_style
        full_width_px  = self.pix_str( self.full_box_width )
        left_width_px  = self.pix_str( self.left_box_width )
        next_width_px  = self.pix_str( self.next_box_width )
        btn_width_px   = self.pix_str( self.button_width )
        #---------------------------------------------------------
        o1 = widgets.Text(description='OpenDAP URL Dir:',
                          value=self.default_url_dir,
                          disabled=False, style=left_style,
                          layout=Layout(width=full_width_px))
        b1 = widgets.Button(description="Go", layout=Layout(width=btn_width_px))
        o2 = widgets.Dropdown( description='Filename:',
                               options=[''], value='',
                               disabled=False, style=left_style,
                               layout=Layout(width=full_width_px) )
        #------------------------------------------------------------------
        oL = widgets.Text(description='Long name:', style=left_style,
                          value='', layout=Layout(width=full_width_px) )
        ## o3 = widgets.Select( description='Variable:',
        o3 = widgets.Dropdown( description='Variable:',
                               options=[''], value='',
                               disabled=False, style=left_style,
                               layout=Layout(width=left_width_px) )
        o4 = widgets.Text(description='Units:', style=next_style,
                          value='', layout=Layout(width=next_width_px) )
        #------------------------------------------------------------------
        o5 = widgets.Text(description='Dimensions:', style=left_style,
                          value='', layout=Layout(width=left_width_px) )
        o6 = widgets.Text(description='Shape:', style=next_style,
                          value='', layout=Layout(width=next_width_px) )
        #------------------------------------------------------------------
        o7 = widgets.Text(description='Data type:', style=left_style,
                          value='', layout=Layout(width=full_width_px) )
        o8 = widgets.Dropdown( description='Attributes:',
                               options=[''], value='',
                               disabled=False, style=left_style,
                               layout=Layout(width=full_width_px) )
        o9 = widgets.Text(description='Status:', style=left_style,
                          value='Ready.', layout=Layout(width=full_width_px) )            
        b2 = widgets.Button(description="Reset", layout=Layout(width=btn_width_px))
        ## pd = widgets.HTML(('&nbsp;' * 1))  # for padding
        
        #-------------------------------
        # Arrange widgets in the panel
        #-------------------------------                                  
        url_box  = widgets.HBox([o1, b1])      # directory + Go button
        stat_box = widgets.HBox([o9, b2])      # status + Reset button
        name_box = widgets.VBox([o3, o5])
        ## pad_box  = widgets.VBox([pd, pd])
        unit_box = widgets.VBox([o4, o6])
        mid_box  = widgets.HBox([name_box, unit_box])
        ## mid_box  = widgets.HBox([name_box, pad_box, unit_box])
        panel    = widgets.VBox([url_box, o2, oL, mid_box, o7, o8, stat_box])
                
        self.data_url_dir   = o1   # on an OpenDAP server
        self.data_filename  = o2
        self.data_var_long_name = oL
        self.data_var_name  = o3     # short_name
        self.data_var_units = o4
        self.data_var_dims  = o5
        self.data_var_shape = o6
        self.data_var_type  = o7
        self.data_var_atts  = o8
        self.data_status    = o9
        self.data_panel     = panel

        #-----------------
        # Event handlers
        #-----------------------------------------------------
        # Note: NEED to set names='value' here.  If names
        #       keyword is omitted, only works intermittently.
        #------------------------------------------------------------
        # "on_click" handler function is passed b1 as argument.
        # "observe" handler function is passed "change", which
        # is a dictionary, as argument. See Traitlet events.
        #------------------------------------------------------------
        b1.on_click( self.update_filename_list )
        b2.on_click( self.reset_data_panel )
        o2.observe( self.update_data_panel, names=['options','value'] )
        o3.observe( self.update_var_info, names=['options', 'value'] )
        ## o3.observe( self.update_var_info, names='value' )
        ## o2.observe( self.update_data_panel, names='All' )
        ## o3.observe( self.update_var_info, names='All' )
 
        #-------------------------------------------------------    
        # It turned out this wasn't an issue, but interesting.
        #-------------------------------------------------------
        # Note: Method functions have type "method" instead
        #       of "function" and therefore can't be passed
        #       directly to widget handlers like "on_click".
        #       But we can use the "__func__" attribute.
        #-------------------------------------------------------           
#         b1.on_click( self.update_filename_list.__func__ )
#         o2.observe( self.update_data_panel.__func__ )
#         o3.observe( self.update_var_info.__func__, names='value' )
       
    #   make_data_panel()
    #--------------------------------------------------------------------
    def reset_data_panel(self, caller_obj=None, KEEP_DIR=False):

        #----------------------------------------------------
        # Note: This is called by the "on_click" method of
        # the "Reset" button beside the status box.
        # In this case, type(caller_obj) =
        # <class 'ipywidgets.widgets.widget_button.Button'>
        #----------------------------------------------------
        if not(KEEP_DIR):
            self.data_url_dir.value = self.default_url_dir
        self.data_filename.options    = ['']
        self.data_var_name.options    = ['']  # short names
        self.data_var_long_name.value = ''
        self.data_var_units.value     = ''
        self.data_var_shape.value     = ''
        self.data_var_dims.value      = ''
        self.data_var_type.value      = ''
        self.data_var_atts.options    = ['']
        self.data_status.value        = 'Ready.'   
        #------------------------------------------
        self.download_log.value = ''

    #   reset_data_panel() 
    #--------------------------------------------------------------------    
    def make_map_panel(self, SHOW_MAP=True):

        map_width_px  = self.map_width_px
        map_height_px = self.map_height_px
        btn_width_px  = self.pix_str( self.button_width )
        #--------------------------------------------------
        # bm_style   = {'description_width': '70px'}  # for top
        bbox_style = {'description_width': '100px'}
        bbox_width_px = '260px'
  
        #---------------------------------------        
        # Create the map width with ipyleaflet
        # Center lat 20 looks better than 0.
        #---------------------------------------
        map_center = self.map_center_init    # (lat, lon)                
        m = Map(center=map_center, zoom=1,
             layout=Layout(width=map_width_px, height=map_height_px))

        #----------------------                
        # Add more controls ?
        #----------------------
        if (self.add_fullscreen_control):
            m.add_control( FullScreenControl( position='topright' ) )
        #---------------------------------------------------------
        # Cannot be imported. (2020-05-18)
        # if (self.add_scale_control):
        #     m.add_control(ScaleControl( position='bottomleft' ))
        #---------------------------------------------------------
        if (self.add_measure_control):      
            measure = MeasureControl( position='bottomright',
                active_color = 'orange',
                primary_length_unit = 'kilometers')
            m.add_control(measure)
            measure.completed_color = 'red'
            ## measure.add_length_unit('yards', 1.09361, 4)
            ## measure.secondary_length_unit = 'yards'
            ## measure.add_area_unit('sqyards', 1.19599, 4)
            ## measure.secondary_area_unit = 'sqyards'
                        
        #-----------------------------------------------------
        # Does "step=0.01" restrict accuracy of selection ??
        #-----------------------------------------------------
        w1 = widgets.BoundedFloatText(
            value=-180, step=0.01, min=-360, max=360.0,
            description='West edge lon:',
            disabled=False, style=bbox_style,
            layout=Layout(width=bbox_width_px) )
    
        w2 = widgets.BoundedFloatText(
            value=180, step=0.01, min=-360, max=360.0,
            description='East edge lon:',
            disabled=False, style=bbox_style,
            layout=Layout(width=bbox_width_px) )
    
        w3 = widgets.BoundedFloatText(
            value=90, min=-90, max=90.0, step=0.01,
            # description='North latitude:',
            description='North edge lat:',
            disabled=False, style=bbox_style,
            layout=Layout(width=bbox_width_px) )
    
        w4 = widgets.BoundedFloatText(
            value=-90, min=-90, max=90.0, step=0.01,
            # description='South latitude:',
            description='South edge lat:',
            disabled=False, style=bbox_style,
            layout=Layout(width=bbox_width_px) )
 
        pd = widgets.HTML(('&nbsp;' * 2))  # for padding
        b1 = widgets.Button(description="Update",
                            layout=Layout(width=btn_width_px))
        b2 = widgets.Button(description="Reset",
                            layout=Layout(width=btn_width_px))

        #---------------------
        # Choose the basemap
        #---------------------
        options = self.get_basemap_list()
        bm = widgets.Dropdown( description='Base map:',
                               options=options, value=options[0],
                               disabled=False, style=bbox_style,
                               layout=Layout(width='360px') )

        #-----------------------------------   
        # Arrange the widgets in the panel
        #-----------------------------------
        lons  = widgets.VBox([w1, w2])
        lats  = widgets.VBox([w3, w4])
        pads  = widgets.VBox([pd, pd])
        btns  = widgets.VBox([b1, b2])
        bbox  = widgets.HBox( [lons, lats, pads, btns])

        #------------------------------------------------------        
        # Encountered a problem where there was some problem
        # with ipyleaflets (used for the map panel) that
        # prevented any part of the GUI from being displayed.
        # The SHOW_MAP flag helps to test for this problem.
        #------------------------------------------------------
        if (SHOW_MAP):
            panel = widgets.VBox( [m, bbox, bm] )
        else:
            panel = widgets.VBox( [bbox, bm] )
                
        self.map_window  = m
        self.map_minlon  = w1
        self.map_maxlon  = w2
        self.map_maxlat  = w3
        self.map_minlat  = w4
        self.map_basemap = bm
        self.map_panel   = panel
        
        ## self.map_bounds = (-180, -90, 180, 90)

        #-----------------
        # Event handlers
        #-----------------
        bm.observe( self.change_base_map, names=['options','value'] )
        m.on_interaction( self.replace_map_bounds )
        m.observe( self.zoom_out_to_new_bounds, 'bounds' )
        m.new_bounds = None  # (used for "zoom to fit")
        b1.on_click( self.update_map_bounds )
        b2.on_click( self.reset_map_panel )
                                   
    #   make_map_panel()
    #-------------------------------------------------------------------- 
    def get_basemap_list(self):
 
        basemap_list = [
        'OpenStreetMap.Mapnik', 'OpenStreetMap.HOT', 'OpenTopoMap',
        'Esri.WorldStreetMap', 'Esri.DeLorme', 'Esri.WorldTopoMap',
        'Esri.WorldImagery', 'Esri.NatGeoWorldMap',
        'NASAGIBS.ModisTerraTrueColorCR', 'NASAGIBS.ModisTerraBands367CR',
        'NASAGIBS.ModisTerraBands721CR',  'NASAGIBS.ModisAquaTrueColorCR',
        'NASAGIBS.ModisAquaBands721CR',   'NASAGIBS.ViirsTrueColorCR',
        'NASAGIBS.ViirsEarthAtNight2012',
        'Strava.All', 'Strava.Ride', 'Strava.Run', 'Strava.Water',
        'Strava.Winter', 'Stamen.Terrain', 'Stamen.Toner',
        'Stamen.Watercolor' ]
        #---------------------------------        
        # 'HikeBike.HikeBike', 'MtbMap'
        # 'OpenStreetMap.BlackAndWhite',
        # 'OpenStreetMap.France',
        #----------------------------------
        return basemap_list
          
    #   get_basemap_list()
    #--------------------------------------------------------------------  
    def change_base_map(self, caller_obj=None):

        #--------------------------------------------------------       
        # Cannot directly change the basemap for some reason.
        # self.map_window.basemap = basemaps.Esri.WorldStreetMap
        # Need to call clear_layers(), then add_layer().
        #---------------------------------------------------------
        map_choice = self.map_basemap.value
        self.map_window.clear_layers()
        basemap_layer = eval( 'basemaps.' + map_choice )
        self.map_window.add_layer( basemap_layer )
 
        # For testing
        # print('map_choice =', map_choice)
        # print('Changed the basemap.')
         
    #   change_base_map()
    #--------------------------------------------------------------------  
    def update_map_view(self, caller_obj=None):
    
        pass

    #   update_map_view()
    #--------------------------------------------------------------------  
    def reset_map_panel(self, caller_obj=None):
    
        self.map_window.center = self.map_center_init
        self.map_window.zoom   = 1
        self.map_minlon.value  = '-225.0'
        self.map_maxlon.value  = '225.0'
        self.map_minlat.value  = '-51.6'
        self.map_maxlat.value  = '70.6'
    
    #   reset_map_panel()
    #--------------------------------------------------------------------  
    def make_datetime_panel(self):

        full_box_width_px = self.pix_str( self.full_box_width )
        date_width_px = self.date_width_px
        time_width_px = self.time_width_px
        hint_width_px = self.hint_width_px
        #-----------------------------------
        date_style    = self.date_style
        time_style    = self.time_style        
        
        d1 = widgets.DatePicker( description='Start Date:',
                    disabled=False, style=date_style,
                    layout=Layout(width=date_width_px) )
        d2 = widgets.DatePicker( description='End Date:',
                    disabled=False, style=date_style,
                    layout=Layout(width=date_width_px) )
        d3 = widgets.Text( description='Start Time:',
                    disabled=False, style=time_style,
                    layout=Layout(width=time_width_px) )
        d4 = widgets.Text( description='End Time:',
                    disabled=False, style=time_style,
                    layout=Layout(width=time_width_px) )
        d3.value = '00:00:00'
        d4.value = '00:00:00'
        #-------------------------------
        # Add some padding on the left
        #-------------------------------
        ## margin = '0px 0px 2px 10px'  # top right bottom left
        pp = widgets.HTML(('&nbsp;' * 3))  # for padding
        d5 = widgets.Label( '(hh:mm:ss, 24-hr)',
                     layout=Layout(width=hint_width_px) )
                     ## layout=Layout(width=hint_width_px, margin=margin) )
                     ## disabled=False, style=hint_style )
        d6 = widgets.Label( '(hh:mm:ss, 24-hr)',
                     layout=Layout(width=hint_width_px) )
                     ## layout=Layout(width=hint_width_px, margin=margin) )
                     ## disabled=False, style=hint_style )
        d7 = widgets.Dropdown( description='Attributes:',
                               options=[''], value='',
                               disabled=False, style=date_style,
                               layout=Layout(width=full_box_width_px) )
#         d8 = widgets.Text( description='Notes:',
#                      disabled=False, style=self.date_style,
#                      layout=Layout(width=full_box_width_px) ) 
                     
        d8 = widgets.Textarea( description='Notes:', value='',
                     disabled=False, style=self.date_style,
                     layout=Layout(width=full_box_width_px, height='140px')) 
                                                             
        dates = widgets.VBox([d1, d2])
        times = widgets.VBox([d3, d4])
        hints = widgets.VBox([d5, d6])
        pad   = widgets.VBox([pp, pp])
        top   = widgets.HBox([dates, times, pad, hints])
        panel = widgets.VBox([top, d7, d8])
        ## panel = widgets.VBox([top, pp, d7, d8])
                   
        self.datetime_start_date = d1
        self.datetime_start_time = d3
        self.datetime_end_date   = d2
        self.datetime_end_time   = d4
        self.datetime_attributes = d7
        self.datetime_notes      = d8
        self.datetime_panel      = panel

    #   make_datetime_panel()
    #-------------------------------------------------------------------- 
    def make_download_panel(self):
      
        init_style = self.init_label_style
        f1 = widgets.Dropdown( description='Download Format:',
                               options=['HDF', 'netCDF', 'netCDF4', 'ASCII'],
                               value='netCDF',
                               disabled=False, style=init_style)
        pad = widgets.HTML(value=f"<p> </p>")   # padding
        b3  = widgets.Button(description="Download")
        h3  = widgets.HBox([f1, pad, b3])

        #-----------------------------------
        # Could use this for info messages
        #-----------------------------------
        # status = widgets.Text(description=' Status:', style=self.style0,
        #                       layout=Layout(width='380px') )
       
        width_px  = self.log_box_width_px
        height_px = self.log_box_height_px                       
        log = widgets.Textarea( description='', value='',
                      disabled=False, style=init_style,
                      layout=Layout(width=width_px, height=height_px)) 
 
        ## panel = widgets.VBox([h3, status, log]) 
        panel = widgets.VBox([h3, log])
        
        self.download_format = f1
        self.download_button = b3
        self.download_log    = log                   
        self.download_panel = panel
        
        #-----------------
        # Event handlers
        #-----------------
        b3.on_click( self.download_data )
        
    #   make_download_panel()
    #-------------------------------------------------------------------- 
    def make_prefs_panel(self):
   
        full_box_width_px = self.pix_str( self.full_box_width ) 
        left_style = self.left_label_style
        
        w1 = widgets.Dropdown( description='OpenDAP package:',
                               options=['pydap', 'netcdf4'],
                               value='pydap',
                               disabled=False, style=left_style)
                       
        ts = self.timeout_secs   
        t1 = widgets.BoundedIntText( description='Timeout:',
                               value=ts, min=10, max=1000,
                               step=1, disabled=False,
                               style=left_style)
        t2 = widgets.Label( ' (seconds)',
                           layout=Layout(width='80px') )
        w2 = widgets.HBox([t1, t2])                       
        note = 'Under construction; preferences will go here.'
        w3 = widgets.Textarea( description='Notes:', value=note,
                     disabled=False, style=left_style,
                     layout=Layout(width=full_box_width_px, height='50px')) 
                     
        panel = widgets.VBox([w1, w2, w3])
        self.prefs_package = w1
        self.prefs_timeout = t1
        self.prefs_notes   = w2
        self.prefs_panel   = panel

    #   make_prefs_panel()
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    def get_map_bounds(self, FROM_MAP=True, style='sw_and_ne_corners'):

        #-------------------------------------------------------
        # Notes: ipyleaflet defines "bounds" as:
        #        [[minlat, maxlat], [minlon, maxlon]]
        #        matplotlib.imshow defines "extent" as:
        #        extent = [minlon, maxlon, minlat, maxlat]
        #-------------------------------------------------------
        #        Return value is a list, not a tuple, but
        #        ok to use it like this:
        # [minlon, minlat, maxlon, maxlat] = get_map_bounds().
        #-------------------------------------------------------
        if (FROM_MAP):
            #------------------------------------      
            # Get the visible map bounds, after
            # interaction such as pan or zoom
            #------------------------------------
#             bounds = self.map_window.bounds
#             minlat = bounds[0][0]
#             minlon = bounds[0][1]
#             maxlat = bounds[1][0]
#             maxlon = bounds[1][1]
            #------------------------------------
            # Is this more reliable ?
            #------------------------------------             
            minlon = self.map_window.west
            minlat = self.map_window.south
            maxlon = self.map_window.east
            maxlat = self.map_window.north
        else:
            #---------------------------------
            # Get map bounds from text boxes
            #---------------------------------
            minlon = self.map_minlon.value
            minlat = self.map_minlat.value
            maxlon = self.map_maxlon.value
            maxlat = self.map_maxlat.value
        
        #------------------------------------------
        # Return map bounds in different "styles"
        #------------------------------------------
        if (style == 'ipyleaflet'):
            bounds = [[minlat, maxlat], [minlon, maxlon]]
        elif (style == 'pyplot_imshow'):
            bounds = [minlon, maxlon, minlat, maxlat]
        elif (style == 'sw_and_ne_corner'):
            bounds = [minlon, minlat, maxlon, maxlat]
        else:
            bounds = [minlon, minlat, maxlon, maxlat]
        return bounds

    #   get_map_bounds()
    #--------------------------------------------------------------------
    def replace_map_bounds(self, event, type=None, coordinates=None):

        #-------------------------------------------
        # Get visible map bounds after interaction    
        # Called by m.on_interaction().
        # Don't need to process separate events?
        #-------------------------------------------
        [minlon, minlat, maxlon, maxlat] = self.get_map_bounds()

        #--------------------------------        
        # Save new values in text boxes
        # Format with 8 decimal places.
        #--------------------------------
        self.map_minlon.value = "{:.8f}".format( minlon )
        self.map_maxlon.value = "{:.8f}".format( maxlon )
        self.map_maxlat.value = "{:.8f}".format( maxlat )
        self.map_minlat.value = "{:.8f}".format( minlat )
    
    #   replace_map_bounds()    
    #--------------------------------------------------------------------
#     def replace_map_bounds2(self, event, type=None, coordinates=None):
# 
#         # events: mouseup, mousedown, mousemove, mouseover,
#         #         mouseout, click, dblclick, preclick
#         event = kwargs.get('type')
#         # print('event = ', event)
#         if (event == 'mouseup') or (event == 'mousemove') or \
#            (event == 'click') or (event == 'dblclick'):
#             w1.value = m.west
#             w2.value = m.east
#             w3.value = m.north
#             w4.value = m.south
#         
#         # status.value = event
#     
#         # with output2:
#         #   print( event )
#
    #--------------------------------------------------------------------
    def update_map_bounds(self, caller_obj=None):

        [bb_minlon, bb_minlat, bb_maxlon, bb_maxlat] = \
            self.get_map_bounds( FROM_MAP = False )
        bb_midlon = (bb_minlon + bb_maxlon) / 2
        bb_midlat = (bb_minlat + bb_maxlat) / 2 
        bb_center = ( bb_midlat, bb_midlon )
        # print('bb_minlon, bb_maxlon =', bb_minlon, bb_maxlon)
        # print('bb_minlat, bb_maxlat =', bb_minlat, bb_maxlat)
        #----------------------------------------------------------
        zoom = self.map_window.max_zoom  # (usually 18)
        self.map_window.center = bb_center        
        self.map_window.zoom   = zoom
        ## print('max_zoom =', self.map_window.max_zoom)
        ## print('map_window.bounds =', self.map_window.bounds )

        #------------------------------------
        # Add "new_bounds" attribute to map
        #------------------------------------
        new_bounds = ((bb_minlat, bb_minlon), (bb_maxlat, bb_maxlon))
        self.map_window.new_bounds = Tuple()
        self.map_window.new_bounds = new_bounds 

    #   update_map_bounds()
    #--------------------------------------------------------------------
    def zoom_out_to_new_bounds(self, change=None):
    
        # change owner is the widget that triggers the handler
        m = change.owner

        #-----------------------------------------
        # If not zoomed all the way out already,
        # and we have a target bounding box
        #-----------------------------------------
        if (m.zoom > 1 and m.new_bounds):
            b = m.new_bounds
            n = change.new
            if (n[0][0] < b[0][0] and n[0][1] < b[0][1] and
                n[1][0] > b[1][0] and n[1][1] > b[1][1]):
                #---------------------------------------
                # new_bounds are now within map window
                # Show bounding box as a rectangle ?
                # weight = line/stroke thickness
                #---------------------------------------
#                 rectangle = Rectangle( bounds=b, fill=False, weight=4)
#                             ## fill_opacity=0.0, \ fill_color="#0033FF" )
#                 m.add_layer(rectangle)
                #-----------------------
                m.new_bounds = None  # (remove target)
            else:
                # zoom out
                m.zoom = m.zoom - 1
    
    #   zoom_out_to_new_bounds()
    #--------------------------------------------------------------------
#     def zoom_out_to_new_bounds_v0(self, caller_obj=None):
#      
#         [bb_minlon, bb_minlat, bb_maxlon, bb_maxlat] = \
#             self.get_map_bounds( FROM_MAP = False )
#         bb_midlon = (bb_minlon + bb_maxlon) / 2
#         bb_midlat = (bb_minlat + bb_maxlat) / 2 
#         bb_center = ( bb_midlat, bb_midlon )
#         print('bb_minlon, bb_maxlon =', bb_minlon, bb_maxlon)
#         print('bb_minlat, bb_maxlat =', bb_minlat, bb_maxlat)
#         zoom = self.map_window.max_zoom  # (usually 18)
#         zoom = zoom - 1
#         ## print('max_zoom =', self.map_window.max_zoom)
#         
#         self.map_window.center = bb_center        
#         self.map_window.zoom   = zoom
#         print('map_window.bounds =', self.map_window.bounds )
#         # bounds is read-only
#         ## self.map_window.bounds = ((bb_midlat,bb_midlon),(bb_midlat,bb_midlon))
#         while (True):
#             # time.sleep(0.5)  ######
#             [minlon, minlat, maxlon, maxlat] = self.get_map_bounds()
#             print('minlon, maxlon =', minlon, maxlon )
#             print('minlat, maxlat =', minlat, maxlat )
#             if (minlon < bb_minlon) and (maxlon > bb_maxlon) and \
#                (minlat < bb_minlat) and (maxlat > bb_maxlat):
#                break
#             else:
#                zoom -= 1
#                if (zoom > 0):
#                    print('zoom =', zoom)
#                    self.map_window.zoom = zoom
#                else:
#                    break
# 
#             [minlon, minlat, maxlon, maxlat] = self.get_map_bounds()
#             print('minlon, maxlon =', minlon, maxlon )
#             print('minlat, maxlat =', minlat, maxlat )
#             if (minlon < bb_minlon) and (maxlon > bb_maxlon) and \
#                (minlat < bb_minlat) and (maxlat > bb_maxlat):
#                break
#             else:
#                zoom -= 1
#                if (zoom > 0):
#                    print('zoom =', zoom)
#                    self.map_window.zoom = zoom
#                else:
#                    break
#         
#     #   zoom_out_to_new_bounds_v0
    #--------------------------------------------------------------------
    def get_url_dir_filenames(self):
 
        #-----------------------------------------       
        # Construct a list of filenames that are
        # available in the opendap url directory
        #-----------------------------------------
        r = requests.get( self.data_url_dir.value )
        lines = r.text.splitlines()
        # n_lines = len(lines)
        filenames = list()
        for line in lines:
            if (".nc<" in line) or (".nc.gz<" in line):
                parts = line.split('"')
                filename = parts[1].replace('.dmr.html', '')
                filenames.append( filename )
        return filenames
    
    #   get_url_dir_filenames()
    #--------------------------------------------------------------------
    def get_url_dir_filenames_OLD(self):
 
        #-----------------------------------------       
        # Construct a list of filenames that are
        # available in the opendap url directory
        #-----------------------------------------
        r = requests.get( self.data_url_dir.value )
        lines = r.text.splitlines()
        # n_lines = len(lines)
        filenames = list()
        for line in lines:
            if ('"sameAs": "http://' in line) and ('www' not in line):
                line = line.replace('.html"', '')
                parts = line.split("/")
                filename = parts[-1]
                filenames.append( filename )
        return filenames
    
    #   get_url_dir_filenames_OLD()
    #--------------------------------------------------------------------
    def update_filename_list(self, caller_obj=None):

        #----------------------------------------------------
        # Note: This is called by the "on_click" method of
        # the "Go" button beside the Dropdown of filenames.
        # In this case, type(caller_obj) =
        # <class 'ipywidgets.widgets.widget_button.Button'>
        #----------------------------------------------------
        ## default_url_dir = 'http://test.opendap.org/dap/data/nc/'

        self.data_status.value = 'Retrieving filenames in URL dir...'         
        filenames = self.get_url_dir_filenames()
        
        if (len(filenames) == 0):
            self.reset_data_panel( KEEP_DIR=True )
            msg = 'Error:  No data files found in URL dir.'
            self.data_status.value = msg
            return
        #-----------------------------------
        # Update filename list & selection
        #-----------------------------------
        self.data_filename.options = filenames
        self.data_filename.value   = filenames[0]
        self.data_status.value = 'Ready.'

    #   update_filename_list()
    #--------------------------------------------------------------------
    def get_opendap_file_url(self):
  
        directory = self.data_url_dir.value
        if (directory[-1] != '/'):
            directory += '/'
        #------------------------------------
        filename = self.data_filename.value
        self.opendap_file_url = (directory + filename)

    #   get_opendap_file_url()
    #--------------------------------------------------------------------
    def open_dataset(self):

        timeout = self.timeout_secs
        opendap_url = self.opendap_file_url
        dataset = pydap.client.open_url( opendap_url, timeout=timeout )

        self.dataset = dataset

    #   open_dataset()
    #--------------------------------------------------------------------
    def update_data_panel(self, change=None):

        #-------------------------------------------------------
        # Note: When used as a callback/handler function for a
        #       widget's "observe" method, a dictionary called
        #       "change" is passed to this function.  This
        #       callback fails without the "change=None".
        #       The type of "change" is:
        #       <class 'traitlets.utils.bunch.Bunch'>
        #-------------------------------------------------------
        # print('type(change) =', type(change))

        if (self.data_filename.value == ''):
            ## self.update_filename_list()   # (try this?)
            return
  
        self.get_opendap_file_url()
        self.open_dataset()
        self.get_all_var_shortnames()
        self.get_all_var_longnames()
        self.get_all_var_units()

        #------------------------------------------
        # Create map between long and short names
        #------------------------------------------
        long_names  = self.var_long_names
        short_names = self.var_short_names
        units_names = self.var_units_names

        self.short_name_map = dict(zip(long_names, short_names ))
        self.units_map  = dict(zip(long_names, units_names ))
        
        #-------------------------------------------
        # Update variable list and selected value.
        #-------------------------------------------
        self.data_var_name.options = short_names
        self.data_var_name.value   = short_names[0]    

        #------------------------------------
        # Show other info for this variable
        #------------------------------------
        self.update_var_info()
        self.clear_download_log()  #####
 
        #-------------------------------------------
        # Try to show map extent in map panel
        #-------------------------------------------
        #### self.update_map_panel()
        
        #-------------------------------------------
        # Try to show date range in datetime panel
        #-------------------------------------------
        self.update_datetime_panel()  # clears notes, too
                  
    #   update_data_panel() 
    #--------------------------------------------------------------------
    def update_var_info(self, change=None):

        #-------------------------------------------------------
        # Note: When used as a callback/handler function for a
        #       widget's "observe" method, a dictionary called
        #       "change" is passed to this function.  This
        #       callback fails without the "change=None".
        #       The type of "change" is:
        #       <class 'traitlets.utils.bunch.Bunch'>
        #-------------------------------------------------------
        short_name = self.get_var_shortname()
        if (short_name == ''):
            return
         
        #-----------------------------------------------      
        # Maybe later wrap this block in "try, except"
        #----------------------------------------------
        # Note: short_name is selected from Dropdown.  
        # var = dataset[ short_name ]
        #----------------------------------------------  
        long_name = self.get_var_longname( short_name )
        units = self.get_var_units( short_name )
        shape = self.get_var_shape( short_name )
        dims  = self.get_var_dimensions( short_name )
        dtype = self.get_var_dtype( short_name )
        atts  = self.get_var_attributes( short_name )
        #---------------------------------------------
        self.data_var_long_name.value = long_name
        self.data_var_units.value     = units
        self.data_var_shape.value     = shape
        self.data_var_dims.value      = dims
        self.data_var_type.value      = dtype
        self.data_var_atts.options    = atts
    
    #   update_var_info()
    #--------------------------------------------------------------------  
    def get_all_var_shortnames(self):

        self.var_short_names = list( self.dataset.keys() )

    #   get_all_var_shortnames()
    #-------------------------------------------------------------------- 
    def get_all_var_longnames(self):

        if not(hasattr(self, 'var_short_names')):
            self.get_all_var_shortnames()
   
        long_names = list()
        for name in self.var_short_names:
            try:
                long_name = get_var_longname( name )
                long_names.append( long_name )
            except:
                # Use short name if there is no long_name.
                long_names.append( name )
                # print('No long name found for:', name)
                
        self.var_long_names = long_names

    #   get_all_var_longnames()
    #--------------------------------------------------------------------  
    def get_all_var_units(self):

        if not(hasattr(self, 'var_short_names')):
            self.get_all_var_shortnames()
               
        units_names = list()
        for name in self.var_short_names:
            try:
                units = self.get_var_units( name )
                units_names.append( units )
            except:
                units_names.append( 'unknown' )
                # print('No units name found for:', name)

        self.var_units_names = units_names

    #   get_all_var_units()
    #--------------------------------------------------------------------
    def get_var_shortname(self):
    
        short_name = self.data_var_name.value
        if (short_name == ''):
            pass
            ## print('Short name is not set.')
        return short_name
            
    #   get_var_shortname()
    #--------------------------------------------------------------------
    def get_var_longname( self, short_name ):

        var = self.dataset[ short_name ]
        if hasattr(var, 'long_name'):
            return var.long_name
        else:
            return 'Long name not found.'
            ## return short_name

    #   get_var_longname()
    #--------------------------------------------------------------------
    def get_var_units( self, short_name ):

        var = self.dataset[ short_name ]
        if hasattr(var, 'units'):
            return var.units
        else:
            return 'unknown'

    #   get_var_units()
    #--------------------------------------------------------------------
    def get_var_shape( self, short_name ):

        var = self.dataset[ short_name ]
        return str(var.shape)

    #   get_var_shape()
    #--------------------------------------------------------------------
    def get_var_dimensions( self, short_name ):
    
        var = self.dataset[ short_name ]
        if hasattr(var, 'dimensions'):
            return str(var.dimensions)
        else:
            return 'No dimensions found.'

    #   get_var_dimensions()
    #--------------------------------------------------------------------
    def get_var_dtype( self, short_name ):

#         The old Numeric single-character typecodes:
#            ('f','d','h', 's','b','B','c','i','l'),
#         corresponding to:
#            ('f4','f8','i2','i2','i1','i1','S1','i4','i4'),
#         are not yet supported.

        type_map = {
        'i1' : '1-byte signed integer',
        'i2' : '2-byte signed integer',
        'i4' : '4-byte signed integer',
        'i8' : '8-byte signed integer',
        'f4' : '4-byte floating point',
        'f8' : '8-byte floating point',
        'u1' : '1-byte unsigned integer',
        'u2' : '2-byte unsigned integer',
        'u4' : '4-byte unsigned integer',
        'u8' : '8-byte unsigned integer' }
        type_list = list( type_map.keys() )
                    
        var = self.dataset[ short_name ]
        type_str = str( var.dtype )
        #----------------------------------------
        # The ">" & "<" indicate big and little
        # endian byte order (i.e. MSB or LSB)
        #----------------------------------------
        endian = ''
        if (type_str[0] == '>'):
            type_str = type_str[1:]
            endian   = '  (big endian)'
            ## endian   = '  (MSB)'
        if (type_str[0] == '<'):
            type_str = type_str[1:]
            endian   = '  (little endian)'
            ## endian   = '  (LSB)'
        #---------------------------------        
        if (type_str in type_list): 
            return type_map[ type_str ] + endian
        elif (type_str[:2] == '|S'):
            try:
                num  = int( type_str[2:] )
                return ('string (' + str(num) + '-character max)')
            except:
                return type_str
        elif (type_str[0] == 'S'):
            try:
                num  = int( type_str[1:] )
                return ('string (' + str(num) + '-character max)')
            except:
                return type_str       
        else:
            return type_str
    
    #   get_var_dtype()
    #--------------------------------------------------------------------
    def get_var_attributes( self, short_name ):

        var = self.dataset[ short_name ]
        if hasattr(var, 'attributes'):
            #----------------------------------------
            # Convert dictionary to list of strings
            # to be displayed in a droplist.
            #----------------------------------------
            att_list = []
            for key, val in var.attributes.items():
                att_list.append( str(key) + ': ' + str(val) )
            return att_list
            #-------------------------------------------
            # Return all attributes as one long string
            #-------------------------------------------
            ### return str( var.attributes )    #### use str()
        else:
            return 'No attributes found.'
    
    #   get_var_attributes()
    #--------------------------------------------------------------------
    def get_time_attributes( self):

        if (hasattr(self.dataset, 'time')):
            time = self.dataset.time
        elif (hasattr(self.dataset, 'TIME')):
            time = self.dataset.TIME
        
        if hasattr(time, 'attributes'):
            #----------------------------------------
            # Convert dictionary to list of strings
            # to be displayed in a droplist.
            #----------------------------------------
            att_list = []
            for key, val in time.attributes.items():
                att_list.append( str(key) + ': ' + str(val) )
            return att_list
            #-------------------------------------------
            # Return all attributes as one long string
            #-------------------------------------------
            ### return str( time.attributes )    #### use str()
        else:
            return 'No time attributes found.'
    
    #   get_time_attributes()
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    def update_datetime_panel(self):
 
        self.clear_datetime_notes()  # erase notes

        #-----------------------------------------
        # Are there any times for this dataset ?
        #-----------------------------------------
        short_names = self.var_short_names   # self.dataset.keys()
        if ('time' in short_names):
            self.time_obj = self.dataset.time
            self.time_var = self.time_obj.data[:]
        elif ('TIME' in short_names):
            self.time_obj = self.dataset.TIME
            self.time_var = self.time_obj.data[:]
        else:
            msg = 'Unable to find times for this dataset.'
            self.append_datetime_notes( msg )
            return

        #-----------------------------------------            
        # Show all time attributes in a droplist
        #-----------------------------------------
        time_att_list = self.get_time_attributes()
        if (time_att_list is not None):
            self.datetime_attributes.options = time_att_list

        #----------------------------------------------------
        # Compute the min and max times; save as time_range
        #----------------------------------------------------
        min_time = self.time_var.min()
        max_time = self.time_var.max()
        self.time_range = [min_time, max_time]
        msg = 'Time range for this dataset = '
        msg += '(' + str(min_time) + ', ' + str(max_time) + ')'
        self.append_datetime_notes( msg )

        #------------------------------------------------
        # Is there an attribute called "actual_range" ?
        #------------------------------------------------      
#         if not(hasattr(self.time_obj, 'actual_range')):
#             msg = 'Unable to find "actual range" for times.'
#             self.datetime_notes.value = msg
#             return
#         else:
#             self.time_range = self.time_obj.actual_range

        #-----------------------------------------
        # Is there an attribute called "units" ?
        #-----------------------------------------
        # The full string may be something like:
        #   hour since 0000-01-01 00:00:00
        # Save both full string and just units.
        #-----------------------------------------
        if (hasattr(self.time_obj, 'units')):
            self.time_units_str = self.time_obj.units
            self.get_actual_time_units() # (set self.time_units)
        else:
            msg = 'Unable to find "units" for time.'
            self.append_datetime_notes( msg )
            return

        #-------------------------------------------
        # Is there an attribute called "delta_t" ?
        # If so, assume it is in "datetime" form,
        # such as 00-01-00 00:00:00" for 1 month.
        #-------------------------------------------
        HAS_DELTA_T = hasattr(self.time_obj, 'delta_t')
        if (HAS_DELTA_T):
            self.time_delta = self.time_obj.delta_t
        else:
            self.get_time_delta_str()
        # For testing:
        # print('In update_datetime_panel():' )
        # print('self.time_delta =', self.time_delta )
        # print('HAS_DELTA_T =', HAS_DELTA_T )

        #---------------------------------------------------
        # Are time units given as "time since" some date ?
        #---------------------------------------------------
        # Sample data has cases with:
        # 'days since', 'hour since' (vs hours), 'seconds since'
        #--------------------------------------------------------
        # Already saved "time_units_str" AND "time_units" above.
        # strip() removes leading and trailing whitespace
        #--------------------------------------------------------        
        time_units_str = self.time_units_str
        if ('since' not in time_units_str):
            msg = 'Time units string has no "since" part.'
            self.append_datetime_notes( msg )
            return

        #-------------------------------------
        # Process the "origin" date and time
        #-------------------------------------
        parts = time_units_str.split('since')
        odt   = parts[1].strip()
        self.origin_datetime_str = odt
        (date_str, time_str) = self.split_datetime_str( odt )
        if (date_str.startswith('0000')):
            msg = 'Warning: "Since" year must be > 0, changing to 1.'
            self.append_datetime_notes( msg )
            date_str = date_str[:3] + '1' + date_str[4:]
        self.origin_datetime_obj = self.get_datetime_obj_from_str( date_str, time_str)
        #---------------------------------------------
        # Now process time_since for start and end
        #---------------------------------------------
        time_since1    = self.time_range[0]
        time_since2    = self.time_range[1]
        start_datetime_obj = self.get_datetime_from_time_since(time_since1)
        end_datetime_obj   = self.get_datetime_from_time_since(time_since2)
        start_datetime_str = str(start_datetime_obj)
        end_datetime_str   = str(end_datetime_obj)
        (start_date, start_time) = self.split_datetime_str( start_datetime_str )
        (end_date, end_time)     = self.split_datetime_str( end_datetime_str )
        #-------------------------------
        # Save these also, as numbers.
        #-------------------------------
        self.start_year = start_datetime_obj.year
        self.end_year   = end_datetime_obj.year
        # (y1,m1,d1) = self.split_date_str( start_date )
        # (y2,m2,d2) = self.split_date_str( end_date )
        # self.start_year  = y1
        # self.end_year    = y2
        #-----------------------------------------------------------
        # Be sure to set date values as date_obj, not datetime_obj
        #-----------------------------------------------------------
        self.datetime_start_date.value = start_datetime_obj.date()
        self.datetime_end_date.value   = end_datetime_obj.date()
        self.datetime_start_time.value = start_time
        self.datetime_end_time.value   = end_time
        #----------------------------------
        # This also works, but more steps
        #----------------------------------
        # (y1,m1,d1) = self.split_date_str( start_date )
        # (y2,m2,d2) = self.split_date_str( end_date )
        # self.datetime_start_date.value = datetime.date(y1, m1, d1)
        # self.datetime_end_date.value   = datetime.date(y2, m2, d2)  
        
    #   update_datetime_panel()
    #-------------------------------------------------------------------- 
    def get_years_from_time_since(self, data_time_since): 

        #----------------------------------------------------         
        # Notes:  self.time_var contains "times since" some
        #         origin time, in days, hours or seconds,
        #         unrestricted by user start/end times.
        #         self.time_range[0] = self.time_var.min()
        #         self.time_range[1] = self.time_var.max()
        #----------------------------------------------------
        #         For plots, want to convert these time
        #         offsets to decimal years, keeping in mind
        #         that user may have restricted the time
        #         range further.
        #----------------------------------------------------
        units_per_year = {
        'years':1.0, 'days':365.0, 'hours':8760.0,
        'minutes':525600.0, 'seconds':31536000.0 }
        min_data_time_since = self.time_range[0]
        time_since_start    = (data_time_since - min_data_time_since)
        #----------------------------------------------------
        units = self.time_units
        if (units in units_per_year.keys()):
            factor = units_per_year[ units ]
            years_since_start = (time_since_start / factor)
        else:
            print('ERROR, Unsupported units:', units)
            return None
        #----------------------------------------------------
        start_year = self.start_year
        dec_years  = (years_since_start + start_year)
        return dec_years

    #   get_years_from_time_since()
    #--------------------------------------------------------------------    
    def clear_datetime_notes(self):

        self.datetime_notes.value = ''

    #   clear_datetime_notes()
    #--------------------------------------------------------------------    
    def append_datetime_notes(self, msg):

        self.datetime_notes.value += (msg + '\n')

    #   append_datetime_notes()
    #--------------------------------------------------------------------
#     def list_to_string( self, array ):
# 
#         s = ''
#         for item in array:
#             s = s + item + '\n'
#         return s
# 
#     #   list_to_string()
    #--------------------------------------------------------------------
    def pad_with_zeros(self, num, target_len):
      
        num_string = str( int(num) )  # int removes decimal part
        n = len( num_string )
        m = (target_len - n)
        num_string = ('0'*m) + num_string
        return num_string
 
    #   pad_with_zeros()
    #--------------------------------------------------------------------
    def get_actual_time_units(self):

#         secs_per_unit_list = [1, 60.0, 3600.0, 86400, 31536000.0, -1]
#         next_unit_factor = [60.0, 60.0, 24.0, 365.0, -1, -1]

        units_list = ['second', 'minute', 'hour',
                       'day', 'year', 'None']   # ascending, skip month

        for units in units_list:
             if (self.time_units_str.startswith(units)):
                 break
        if (units != None):
            units += 's'   # (make units plural now; not before)
        else:
            print('ERROR: No match found for units.')
            return
        self.time_units = units

    #   get_actual_time_units()
    #--------------------------------------------------------------------
    def get_time_delta_str(self):

        ## print('### self.time_var.size =', self.time_var.size )
        ## print('###')
        
        #-----------------------------------
        # Check size of the time_var array
        #-----------------------------------
        if (self.time_var.size == 1):
            dt = 0
            self.time_delta = '0000-00-00 00:00:00'
            # print('At top of get_time_delta_str():')
            # print('self.time_var.size =', self.time_var.size )
            # print('self.time_delta =', self.time_delta )
            return
        if (self.time_var.size > 1):  
            dt  = (self.time_var[1] - self.time_var[0])
            print('dt1 =', dt)
        if (self.time_var.size > 3):
            dt2 = (self.time_var[2] - self.time_var[1])  ###
            dt3 = (self.time_var[3] - self.time_var[2])  ###
            print('dt2 =', dt2)  # check if evenly spaced
            print('dt3 =', dt3)
                
        #---------------------------------------------------        
        # Note: Actual time units were stripped from units
        #       string and saved as self.time_units.
        #       A full units attribute string may be:
        #        'hour since 0000-00-00 00:00:00'
        #---------------------------------------------------
        units_list = ['seconds', 'minutes', 'hours',
                      'days', 'years', 'None']  # ascending, skip month
        secs_per_unit_list = [1, 60.0, 3600.0, 86400, 31536000.0, -1]
        next_unit_factor   = [60.0, 60.0, 24.0, 365.0, -1, -1]
        units       = self.time_units
        units_index = units_list.index( units )
        #----------------------------------------
        if (units == 'years'):
            s = self.pad_with_zeros(dt,4)
        else:
            if (len(str(dt)) <= 2):
                s = self.pad_with_zeros(dt,2)
            else:
                #-------------------------------
                # Must convert units to get dt
                # down to 1 or 2 digits.
                #-------------------------------
                old_dt    = dt
                old_units = units
                k = units_index
                n = len( str(int(dt)) )
                while (n > 2) and (units != 'None'):
                    k     = k + 1
                    dt    = (dt / next_unit_factor[k-1])
                    units = units_list[k]
                    n     = len( str(int(dt)) )
                if (units == 'None'):
                    print('#####################################')
                    print('ERROR in get_time_delta_str():')
                    print('      dt has too many digits.')
                    print('#####################################')
                    return
                else:
                    # Note that any remainder has been dropped.
                    s = self.pad_with_zeros(dt,2)
                    print('Old dt and units =', old_dt, old_units)
                    print('New dt and units =', dt, units)
                    print('Remainder not retained yet.')
        #----------------------------------------------
        if (units == 'years'):
            td = (s + '-00-00 00:00:00')
#         if (units == 'months'):
#             td= ('0000-' + s + '-00 00:00:00')
        if (units == 'days'):
            td = ('0000-00-' + s + ' 00:00:00')
        if (units == 'hours'):
            td = ('0000-00-00 ' + s + ':00:00')
        if (units == 'minutes'):
            td = ('0000-00-00 00:' + s + ':00')
        if (units == 'seconds'):
            td = ('0000-00-00 00:00:' + s)
        #------------------------------------------------
        self.time_delta = td
        # print('At bottom of get_time_delta_str():')
        # print('self.time_delta =', td)
        # print()

    #   get_time_delta_str()
    #--------------------------------------------------------------------
    def get_datetime_obj_from_str(self, date_str, time_str='00:00:00'):

        #---------------------------------------------------
        # date_str = 'YYYY-MM-DD', time_str = 'HH:MM:SS'
        #---------------------------------------------------
        ## e.g. d1 = str(self.datetime_end_date.value)
        ## e.g. t1 = self.datetime_end_time.value
   
        (y, m1, d) = self.split_date_str(date_str)
        (h, m2, s) = self.split_time_str(time_str)
        if( y <= 0 ):
            # msg  = 'Year cannot be < 1 in start date.\n'
            # msg += 'Changed year from ' + str(y) + ' to 1.'
            # self.datetime_notes.value = msg
            print('Year cannot be < 1 in start date.')
            print('Changed year from ' + str(y) + ' to 1.')
            print()
            y = 1
        datetime_obj = datetime.datetime(y, m1, d, h, m2, s) 
        return datetime_obj
        
    #   get_datetime_obj_from_str()
    #--------------------------------------------------------------------                       
    def get_datetime_obj_from_one_str(self, datetime_str):
    
        (date, time) = self.split_datetime_str( datetime_str )
        (y, m1,  d)  = self.split_date_str( date )
        (h, m2, s)   = self.split_time_str( time )
        datetime_obj = datetime.datetime(y, m1, d, h, m2, s)
        return datetime_obj

    #   get_datetime_obj_from_one_str()
    #--------------------------------------------------------------------
    def get_start_datetime_obj(self):

        #---------------------------------------
        # d1.value is a datetime "date object"
        # t1.value is a time string: 00:00:00
        #---------------------------------------
        d1 = self.datetime_start_date
        t1 = self.datetime_start_time
        if (d1.value is None):
            return None
        date_str = str(d1.value)
        time_str = t1.value   # (already string)
        ## print('In get_start_datetime_obj():')
        ## print('date_str =', date_str)
        ## print('time_str =', time_str)
        
        datetime_obj = self.get_datetime_obj_from_str(date_str, time_str)
        return datetime_obj
    
    #   get_start_datetime_obj()
    #--------------------------------------------------------------------
    def get_end_datetime_obj(self):

        #---------------------------------------
        # d1.value is a datetime "date object"
        # t1.value is a time string: 00:00:00
        #---------------------------------------
        d1 = self.datetime_end_date
        t1 = self.datetime_end_time
        if (d1.value is None):
            return None
        date_str = str(d1.value)
        time_str = t1.value   # (already string)
        ## print('In get_end_datetime_obj():')
        ## print('date_str =', date_str)
        ## print('time_str =', time_str)
        
        datetime_obj = self.get_datetime_obj_from_str(date_str, time_str)
        return datetime_obj

    #   get_end_datetime_obj()
    #--------------------------------------------------------------------  
    def split_datetime_str(self, datetime_obj, datetime_sep=' ',
                           ALL=False):
 
        #-----------------------------------------------     
        # Note: Still works if datetime_obj is string.
        #-----------------------------------------------
        datetime_str = str(datetime_obj)
        parts = datetime_str.split( datetime_sep )
        ## print('## datetime_str =', datetime_str )
        ## print('## parts =', str(parts) )
        
        date_str = parts[0]
        time_str = parts[1]
        if not(ALL):
            return (date_str, time_str)
        else:
            (y,m1,d) = self.split_date_str( date_str )
            (h,m2,s) = self.split_time_str( time_str )
            return (y,m1,d,h,m2,s)

    #   split_datetime_str()
    #--------------------------------------------------------------------  
    def split_date_str(self, date_str, date_sep='-'):

        date_parts = date_str.split( date_sep )
        year  = int(date_parts[0])
        month = int(date_parts[1])   # NOTE:  int('08') = 8
        day   = int(date_parts[2])
        return (year, month, day)
         
    #   split_date_str()
    #--------------------------------------------------------------------  
    def split_time_str(self, time_str, time_sep=':'):

        time_parts = time_str.split( time_sep )
        hour   = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2])
        return (hour, minute, second)

    #   split_time_str()
    #--------------------------------------------------------------------                      
    def get_datetime_from_time_since(self, time_since):
                                         
        # For testing
    #         print('## type(times_since) =', type(time_since) )
    #         print('## time_since =', time_since )
    #         print('## int(time_since) =', int(time_since) )
    
        #---------------------------------------------------   
        # Note: datetime.timedelta() can take integer or
        #       float arguments, and the arguments can be
        #       very large numbers.  However, it does not
        #       accept any numpy types, whether float or
        #       int (e.g. np.int16, np.float32).
        # https://docs.python.org/3/library/datetime.html
        #---------------------------------------------------
        units = self.time_units  # ('days', 'hours', etc.)
        delta = None
        time_since2 = float(time_since)  ## No numpy types
        #------------------------------------------------------    
        if (units == 'days'):
            delta = datetime.timedelta( days=time_since2 )
        if (units == 'hours'):
            delta = datetime.timedelta( hours=time_since2 )
        if (units == 'minutes'):
            delta = datetime.timedelta( minutes=time_since2 )
        if (units == 'seconds'):
            delta = datetime.timedelta( seconds=time_since2 )
        #------------------------------------------------------
        if (delta is None):
            msg = 'ERROR: Units: ' + units + ' not supported.'
            self.append_datetime_notes( msg )
            return

        # For testing
        ## print('#### delta =', delta)
    
        #---------------------------------------------        
        # Create new datetime object from time_since
        #---------------------------------------------
        origin_obj = self.origin_datetime_obj
        new_dt_obj = (origin_obj + delta)
        return new_dt_obj

    #   get_datetime_from_time_since()
    #--------------------------------------------------------------------                       
#     def get_datetime_from_time_since_OLD(self, time_since):
#         
#         #---------------------------------------------------
#         # datetime.timedelta has limits on inputs, e.g.
#         # numpy.int32 is unsupported time for seconds arg.
#         # So here we adjust big numbers for timedelta.
#         # The days argument can handle really big numbers.     
#         #---------------------------------------------------
#         maxint = 32767    
#         units = self.time_units  # ('days', 'hours', etc.)
#         n_per_day = {'seconds':86400.0, 'minutes':1440.0,
#                      'hours':24.0, 'days':1.0}
#         if (time_since > maxint):
#             time_since = time_since / n_per_day[ units ]
#             units = 'days'  # (new units)
# 
#         #-------------------------------------------------
#         # Note: We now save self.time_units_str separate
#         #       from self.time_units.
#         #-------------------------------------------------
#         delta = None
#         if (units == 'days'):
#             delta = datetime.timedelta( days=time_since )
#         if (units == 'hours'):
#             delta = datetime.timedelta( hours=time_since )
#         if (units == 'minutes'):
#             delta = datetime.timedelta( minutes=time_since )
#         if (units == 'seconds'):
#             delta = datetime.timedelta( seconds=time_since )
#         #-----------------------------------------------------
#         if (delta is None):
#             msg = 'ERROR: Units: ' + units + ' not supported.'
#             self.append_datetime_notes( msg )
#             return
# 
#         #---------------------------------------------        
#         # Create new datetime object from time_since
#         #---------------------------------------------
#         origin_obj = self.origin_datetime_obj
#         new_dt_obj = (origin_obj + delta)
#         return new_dt_obj
#         
#         # For testing
#         ## print('origin_datetime_obj =', str(origin_obj) )
#         ## print('time_since delta    =', str(delta) )
#         ## print('new_dt_obj          =', str(new_dt_obj) ) 
#         ## return new_dt_obj
# 
#     #   get_datetime_from_time_since()
    #--------------------------------------------------------------------                       
    def get_time_since_from_datetime(self, datetime_obj, units='days'):

        #-------------------------------------------------
        # Compute time duration between datetime objects
        #-------------------------------------------------
        origin_obj    = self.origin_datetime_obj
        duration_obj  = (datetime_obj - origin_obj)
        duration_secs = duration_obj.total_seconds()
        #---------------------------------------------------
        # There is not a fixed number of seconds per month
        # Also 52 (weeks/year) * 7 (days/week) = 364.
        #---------------------------------------------------
        secs_per_unit_map = {
        'years':31536000.0, 'weeks':604800.0, 'days':86400.0,
        'hours':3600.0, 'minutes':60.0, 'seconds':1 }          
        secs_per_unit = secs_per_unit_map[ units ]      
        duration = (duration_secs / secs_per_unit )
        time_since = duration  # (in units provided)

        return time_since
            
    #   get_time_since_from_datetime()
    #--------------------------------------------------------------------  
    def get_month_difference(self, start_datetime_obj, end_datetime_obj ):
 
        #-------------------------------------------
        # Example 0: 2017-09 to 2017-09
        # months = (2017-2017)*12 = 0
        # months = (months - 9) = (0-9) = -0
        # months = (months + 9) = 0   (as index)
        #-------------------------------------------           
        # Example 1: 2017-09 to 2018-02
        # 9:10, 10:11, 11:12, 12:1, 1:2 = 5 (if same days)
        # months = (2018-2017)*12  = 12
        # months = (months - 9) = 3
        # months = (months + 2) = 3 + 2 = 5
        #-------------------------------------------
        start_year = start_datetime_obj.year
        end_year   = end_datetime_obj.year
        months     = (end_year - start_year) * 12
        #-------------------------------------------
        start_month = start_datetime_obj.month
        end_month   = end_datetime_obj.month
        months = months - start_month
        months = months + end_month
        ## months = months + 1  # (no: get 1 if dates same)
        ## print('month difference =', months)
        return months

    #   get_month_difference()
    #--------------------------------------------------------------------    
    def get_new_time_index_range(self, REPORT=True):

        if not(hasattr(self, 'origin_datetime_str')):
            msg = 'Sorry, origin datetime is not set.'
            self.append_download_log( [msg, ' '] )
            if (hasattr(self, 'time_var')):
                nt = len(self.time_var)
                return (0, nt - 1)  # (unrestricted by choices) 
            else:
                return (None, None)

        #----------------------------------------------------
        # Get min possible datetime, from time_vars.min().
        # Every time_var value is measured from an "origin"
        # such as: '1800-01-01 00:00:00'
        #----------------------------------------------------
        ## origin_datetime_obj = self.origin_datetime_obj
        time_since_min   = self.time_var.min()
        min_datetime_obj = self.get_datetime_from_time_since( time_since_min )
        
        #-----------------------------------------------        
        # Get current settings from the datetime panel
        #-----------------------------------------------
        start_datetime_obj = self.get_start_datetime_obj()
        end_datetime_obj   = self.get_end_datetime_obj()

        #---------------------------------------------------     
        # Convert dt datetime string to "timedelta" object
        # e.g. 00-01-00 00:00:00
        #---------------------------------------------------
        # Note: datetime.timedelta() does not do "months",
        #       since they're not a fixed number of days,
        #       so we use "get_month_difference()".  Also
        #       it does not have a "years" argument.
        #---------------------------------------------------
        ## print('In get_new_time_index_range():')
        ## print('self.time_delta =', self.time_delta)
        USE_LOOPS = True
        (y,m1,d,h,m2,s) = self.split_datetime_str(self.time_delta, ALL=True)
        ## print('time_delta =', self.time_delta )
        ## print('y, m1, d, h, m2, s =', y, m1, d, h, m2, s )
        if (m1 == 0):
            d = (y*365) + d   # python int(), not 2-byte int.
            # print('days =', d)
            dt_timedelta_obj = datetime.timedelta(days=d, hours=h, minutes=m2, seconds=s)
        elif (m1 > 0 and (y+d+h+m2+s == 0)):
            n_months1 = self.get_month_difference( min_datetime_obj, start_datetime_obj  )
            n_months2 = self.get_month_difference( min_datetime_obj, end_datetime_obj  )
            start_index = int(n_months1 / m1)
            end_index   = int(n_months2 / m1)
            USE_LOOPS   = False
        else:
            # Note: I think there is a "monthdelta" package ?
            #       Or we may be able to use dateutils.
            print('ERROR: Cannot handle this dt case yet.')
            return None

        #-------------------------------------------------        
        # Compute start and end index into time array.
        # General method, if delta_t is datetime string.
        #-------------------------------------------------
        if (USE_LOOPS):
            start_index = 0
            # print('min_datetime_str =', str(min_datetime_obj) )
            # print('dt_timedelta_str =', str(dt_timedelta_obj) )
            next = copy.copy( min_datetime_obj )
            while (True):
                next = (next + dt_timedelta_obj)
                ## print('next =', str(next))
                if (next < start_datetime_obj):
                    start_index += 1
                else: break
            #-------------------------------------------------
            end_index = 0
            next = copy.copy( min_datetime_obj )
            while (True):
                next = (next + dt_timedelta_obj)
                if (next < end_datetime_obj):
                    end_index += 1
                else: break
                
        #---------------------------------
        # Make sure indices are in range
        #---------------------------------                  
        nt = len( self.time_var )
        start_index = max(0, start_index)
        end_index   = min(end_index, nt-1)
        #---------------------------------------
        # User time period may be smaller than
        # time spacing (dt).
        #----------------------------------------------------
        # We are using these indices like this:
        #   a[ t_i1:t_i2, lat_i1:lat_i2, lon_i1:lon_i2]
        # So if indices are equal, result will be empty.
        # If indices differ by 1, get 1 value for that dim.
        #----------------------------------------------------        
        if (start_index == end_index):
            end_index = start_index + 1
        
        if (REPORT):
            # print('n_times =', nt)
            # print('New time indices =', start_index, ',', end_index)
            # print()
            #--------------------------
            i1s  = str(start_index)
            i2s  = str(end_index)
            msg1 = 'n_times = ' + str(nt)
            msg2 = 'New time indices = ' + i1s + ',' + i2s
            self.append_download_log( [msg1, msg2, ' '] )

        return (start_index, end_index)
                     
        # Not needed for current problem.
        # days_since1 = self.get_days_since_from_datetime(start_datetime_obj)
        # days_since2 = self.get_days_since_from_datetime(end_datetime_obj)
       
        # For testing
        # print('type(start_index) =', type(start_index) )
        # print('type(end_index)   =', type(end_index) )
        # print('start_index =', start_index)
        # print('end_index   =', end_index)
        # print('n_times     =', nt)
        # return (start_index, end_index)
        
    #   get_new_time_index_range()
    #--------------------------------------------------------------------
    def get_new_lat_index_range(self, REPORT=True):
       
        short_name = self.get_var_shortname()
        #-------------------------------------------------
        # Note: dimensions can be things like 'ni', 'nj'
        #       so its better to use the list of all
        #       variable short names, stored earlier.
        #       They are valid keys to self.dataset.
        #-------------------------------------------------
        ## dim_list = self.dataset[ short_name ].dimensions
        ## dim_list = self.dataset[ short_name ].attributes.keys()
        dim_list = self.var_short_names       
        lat_name_list = ['lat', 'LAT', 'coadsy', 'COADSY',
                         'latitude', 'LATITUDE', 'None']
        for lat_name in lat_name_list:
            if (lat_name in dim_list):
                break
        if (lat_name == 'None'):
            msg1 = 'Sorry, could not find a "latitude" variable.'
            msg2 = 'Checked: lat, LAT, coadsy, COADSY,'
            msg3 = '   latitude and LATITUDE.'
            self.append_download_log( [msg1, msg2, msg3] )
            return (None, None)

        #-------------------------------------------- 
        # Are lats for grid cell edges or centers ?
        #-------------------------------------------- 
        att_dict = self.dataset[ lat_name ].attributes
        CENTERS = False
        if ('coordinate_defines' in att_dict.keys() ):
            if (att_dict['coordinate_defines'] == 'center'):
                CENTERS = True

        #------------------------------------
        # Get user-select minlat and maxlat
        #------------------------------------
        user_minlat = self.map_minlat.value
        user_maxlat = self.map_maxlat.value

        #----------------------------------       
        # Get the array of lats, and info
        #-----------------------------------------
        # <class 'pydap.model.BaseType'>' object
        #    has no attribute 'array'
        #--------------------------------------------------
        # Next line type:  <class 'pydap.model.BaseType'>
        # and has no attribute "array".
        #--------------------------------------------------
        # lats = self.dataset[ lat_name ]
        # lats = self.dataset[ lat_name ].array
        #----------------------------------------------------------
        # Next line type:  <class 'pydap.handlers.dap.BaseProxy'>
        # and has no attribute "size".
        #----------------------------------------------------------
        # lats = self.dataset[ lat_name ].data
        #----------------------------------------------------------
        # Next line type:  <class 'pydap.model.BaseType'>
        # and data is downloaded from server.
        #----------------------------------------------------------
        # lats = self.dataset[ lat_name ][:]
        #----------------------------------------------------------
        # Next line type:  <class 'numpy.ndarray'>
        #----------------------------------------------------------                      
        lats = self.dataset[ lat_name ][:].data

        if (lats.ndim > 1):
            msg1 = 'Sorry, cannot yet restrict latitude indices'
            msg2 = '   when lat array has more than 1 dimension.'
            self.append_download_log( [msg1, msg2] )
            return (None, None)
            
        # print('## type(lats) =', type(lats) )
        # print('## lats.shape =', lats.shape )
        # print('## lats =', lats )

        #------------------------------------------------        
        # It seems that values may be reverse sorted to 
        # indicate that the origin is upper left corner
        # Don't sort them, need indices into original.
        #------------------------------------------------
        if (lats[0] > lats[-1]):
            origin = 'upper'
        else:
            origin = 'lower'
            
        #------------------------------------------
        # Compute the latitude spacing, dlat
        #------------------------------------------
        # This only works if lats are a 1D list.
        # If a "list of lists", len() will be for
        # the outer list and min() won't work.
        # Also, no "size" attribute, etc.
        #------------------------------------------
        nlats  = lats.size
        minlat = lats.min()
        maxlat = lats.max()
        dlat   = np.abs(lats[1] - lats[0])
        #--------------
        # Another way
        #--------------
#         latdif = (maxlat - minlat)
#         if (CENTERS):
#             dlat = (latdif / (nlats - 1))
#         else:
#             dlat = (latdif / nlats)

        #--------------------------------------
        # Compute the new, restricted indices
        # New method:  (2020-12-12)
        #--------------------------------------
        all_indices = np.arange( nlats )
        w = np.logical_and(lats > user_minlat, lats < user_maxlat)  # boolean array
        indices = all_indices[w]
        if (indices.size > 0):
            lat_i1 = indices[0]
            lat_i2 = indices[-1]
        else:
            lat_i1 = 0
            lat_i2 = nlats-1
              
        #--------------------------------------
        # Compute the new, restricted indices
        #--------------------------------------
        # Here, int() behaves like "floor()".
        # So maybe add 1 to lat_i2 ???
        #--------------------------------------
#         lat_i1 = int( (user_minlat - minlat) / dlat )
#         lat_i2 = int( (user_maxlat - minlat) / dlat )
#         lat_i2 = (lat_i2 + 1)  ########
        #---------------------------------
        # Make sure indices are in range
        #---------------------------------------- 
#         lat_i1 = min( max(lat_i1, 0), nlats-1 )
#         lat_i2 = min( max(lat_i2, 0), nlats-1 )
        #------------------------------------------
        # User region may be smaller than v_dlat,
        # as is the case with Puerto Rico, where
        # data grid cells are 1 deg x 1 deg or so.
        #------------------------------------------        
#         if (lat_i1 == lat_i2):  # (still possible?)
#             lat_i2 = lat_i1 + 1
 
        if (REPORT):
            print('lat_name =', lat_name)
            print('minlat   =', minlat, '(var)' )
            print('maxlat   =', maxlat, '(var)' )
            print('dlat     =', dlat)
            print('u_minlat =', user_minlat, '(user)' )
            print('u_maxlat =', user_maxlat, '(user)' )        
            print('lat_i1   =', lat_i1, '(new index)')
            print('lat_i2   =', lat_i2, '(new index)')
            # print('nlats    =', nlats)
            # print('New latitude indices =', lat_i1, ',', lat_i2)
            # print()
            #-------------------------------
            i1s  = str(lat_i1)
            i2s  = str(lat_i2)
            msg1 = 'lat_name = ' + lat_name
            msg2 = 'dlat     = ' + str(dlat)
            msg3 = 'nlats    = ' + str(nlats)
            msg4 = 'min, max = ' + str(minlat) + ', ' + str(maxlat) + ' (data)'
            msg5 = 'min, max = ' + str(user_minlat) + ', ' + str(user_maxlat) + ' (user)'
            msg6 = 'New latitude indices = ' + i1s + ', ' + i2s
            self.append_download_log([msg1, msg2, msg3, msg4, msg5, msg6, ' '])
                        
        return (lat_i1, lat_i2)

    #   get_new_lat_index_range()
    #--------------------------------------------------------------------
    def get_new_lon_index_range(self, REPORT=True):

        short_name = self.get_var_shortname()
        #-------------------------------------------------
        # Note: dimensions can be things like 'ni', 'nj'
        #       so its better to use the list of all
        #       variable short names, stored earlier.
        #       They are valid keys to self.dataset.
        #-------------------------------------------------
        ## dim_list = self.dataset[ short_name ].dimensions
        ## dim_list = self.dataset[ short_name ].attributes.keys()
        dim_list = self.var_short_names
        lon_name_list = ['lon', 'LON', 'coadsx', 'COADSX',
                         'longitude', 'LONGITUDE', 'None']
        for lon_name in lon_name_list:
            if (lon_name in dim_list):
                break
        if (lon_name == 'None'):
            msg1 = 'Sorry, could not find a "longitude" variable.'
            msg2 = 'Checked: lon, LON, coadsx, COADSX,'
            msg3 = '   longitude and LONGITUDE.'
            self.append_download_log( [msg1, msg2, msg3] )
            return (None, None)

        #-------------------------------------------- 
        # Are lons for grid cell edges or centers ?
        #-------------------------------------------- 
        att_dict = self.dataset[ lon_name ].attributes
        CENTERS = False
        if ('coordinate_defines' in att_dict.keys() ):
            if (att_dict['coordinate_defines'] == 'center'):
                CENTERS = True

        #------------------------------------------------
        # Are data longitudes in [-180,180] or [0,360]?
        #------------------------------------------------
        NO_NEGATIVE_LONS = True  # default
        if ('actual_range' in att_dict.keys() ):
            lon_range = att_dict['actual_range']
            NO_NEGATIVE_LONS = (lon_range[0] >= 0)

        #------------------------------------
        # Get user-select minlat and maxlat
        #------------------------------------
        user_minlon = self.map_minlon.value
        user_maxlon = self.map_maxlon.value

        #----------------------------------       
        # Get the array of lons, and info
        #----------------------------------
        lons = self.dataset[ lon_name ][:].data
       
        if (lons.ndim > 1):
            msg1 = 'Sorry, cannot yet restrict longitude indices'
            msg2 = '   when lon array has more than 1 dimension.'
            self.append_download_log( [msg1, msg2] )
            return (None, None)

        # print('## type(lons) =', type(lons) )
        # print('## lons.shape =', lons.shape )
        # print('## lons.ndim  =', lons.ndim )

        #------------------------------------------      
        # Compute the longitude spacing, dlon  
        #------------------------------------------
        # This only works if lons are a 1D list.
        # If a "list of lists", len() will be for
        # the outer list and min() won't work.
        # Also, no "size" attribute, etc.
        #------------------------------------------
        nlons  = lons.size
        minlon = lons.min()
        maxlon = lons.max()
        dlon   = np.abs(lons[1] - lons[0])
        #--------------
        # Another way
        #--------------
#         londif = (maxlon - minlon)
#         if (CENTERS):
#             dlon = (londif / (nlons - 1))
#         else:
#             dlon = (londif / nlons)

        #-----------------------------------------        
        # Convert lons to have range [-180,180]?
        #-----------------------------------------
#         lons = ((lons + 180.0) % 360) - 180
#         user_maxlon = ((user_maxlon + 180.0) % 360) - 180
#         user_minlon = ((user_minlon + 180.0) % 360) - 180

        #-------------------------------------------        
        # Convert user lons to have range [0,360]?
        #-------------------------------------------
        ### if (minlon >= 0) and (maxlon <= 360):
        if (NO_NEGATIVE_LONS):
            user_minlon = (user_minlon + 360.0) % 360
            user_maxlon = (user_maxlon + 360.0) % 360

        #--------------------------------------
        # Compute the new, restricted indices
        # New method:  (2020-12-12)
        #--------------------------------------
        all_indices = np.arange( nlons )
        w = np.logical_and(lons > user_minlon, lons < user_maxlon)  # boolean array
        indices = all_indices[w]
        if (indices.size > 0):
            lon_i1 = indices[0]
            lon_i2 = indices[-1]
        else:
            lon_i1 = 0
            lon_i2 = nlons-1
                  
        #--------------------------------------
        # Compute the new, restricted indices
        #--------------------------------------
        # Here, int() behaves like "floor()".
        # So maybe add 1 to lon_i2 ???
        #-------------------------------------- 
#         lon_i1 = int( (user_minlon - minlon) / dlon )
#         lon_i2 = int( (user_maxlon - minlon) / dlon )
#         lon_i2 = lon_i2 + 1   #######

        #---------------------------------
        # Make sure indices are in range
        #---------------------------------------- 
#         lon_i1 = min( max(lon_i1, 0), nlons-1 )
#         lon_i2 = min( max(lon_i2, 0), nlons-1 )
        #------------------------------------------
        # User region may be smaller than v_dlat,
        # as is the case with Puerto Rico, where
        # data grid cells are 1 deg x 1 deg or so.
        #------------------------------------------        
#         if (lon_i1 == lon_i2):   # (still needed?)
#             lon_i2 = lon_i1 + 1

        if (REPORT):
            print()
            print('lon_name =', lon_name)
            print('minlon   =', minlon, '(var)')
            print('maxlon   =', maxlon, '(var)')
            print('dlon     =', dlon)
            print('u_minlon =', user_minlon, '(user)')
            print('u_maxlon =', user_maxlon, '(user)')
            print('lon_i1   =', lon_i1, '(new index)')
            print('lon_i2   =', lon_i2, '(new index)')
#             print('nlons    =', nlons)
#             print('New longitude indices =', lon_i1, ',', lon_i2 )
#             print()
            #--------------------------------------------------
            i1s  = str(lon_i1)
            i2s  = str(lon_i2)
            msg1 = 'lon_name = ' + lon_name
            msg2 = 'dlon     = ' + str(dlon)
            msg3 = 'nlons    = ' + str(nlons)
            msg4 = 'min, max = ' + str(minlon) + ', ' + str(maxlon) + ' (data)'
            msg5 = 'min, max = ' + str(user_minlon) + ', ' + str(user_maxlon) + ' (user)'
            msg6 = 'New longitude indices = ' + i1s + ', ' + i2s
            self.append_download_log([msg1, msg2, msg3, msg4, msg5, msg6, ' '])

        return (lon_i1, lon_i2)

    #   get_new_lon_index_range()
    #--------------------------------------------------------------------
    def get_duration(self, start_date=None, start_time=None,
                     end_date=None, end_time=None,
                     dur_units=None, REPORT=False):
                 
        #------------------------------------------------    
        # Note:  Compute time span between 2 datetimes.
        #------------------------------------------------
        ## date_sep = '/'
        date_sep = '-'
        time_sep = ':'
        #-------------------------------------
        # Get parts of the start date & time
        #-------------------------------------
        (y1, m1,  d1) = self.split_date_str( start_date )
        (h1, mm1, s1) = self.split_time_str( start_time )

        #-----------------------------------
        # Get parts of the end date & time
        #-----------------------------------
        (y2, m2,  d2) = self.split_date_str( end_date )
        (h2, mm2, s2) = self.split_time_str( end_time )

        #------------------------------
        # Convert to datetime objects
        #------------------------------
        start_obj = datetime.datetime(y1, m1, d1, h1, mm1, s1)
        end_obj   = datetime.datetime(y2, m2, d2, h2, mm2, s2)
        
        #---------------------------------------------
        # Comput time duration between start and end
        #---------------------------------------------
        duration_obj  = (end_obj - start_obj)
        duration_secs = duration_obj.total_seconds()

        #-----------------------------------------    
        # Convert duration to dur_units provided
        #-----------------------------------------
        if (dur_units == 'seconds'):
            duration = duration_secs
        elif (dur_units == 'minutes'):
            duration = (duration_secs / 60.0)
        elif (dur_units == 'hours'):
            duration = (duration_secs / 3600.0)
        elif (dur_units == 'days'):
            duration = (duration_secs / 86400.0)
        elif (dur_units == 'years'):
            duration = (duration_secs / 31536000.0)
        else:
            print('Unknown duration units = ' + dur_units + '.')
            print('Returning duration in hours.')
            duration = (duration_secs / 3600.0)
        
        if (REPORT):
            print( 'duration =', duration, '[' + dur_units + ']' )

        return duration
    
        #-----------------------------------------      
        # Alternate approach, where dur_units is
        # determined and then returned
        #-----------------------------------------   
    #     if (duration_secs < 60):
    #         duration  = duration_secs
    #         dur_units = 'seconds'
    #     elif (duration_secs < 3600):
    #         duration  = divmod( duration_secs, 60 )[0]
    #         dur_units = 'minutes'
    #     elif (duration_secs < 86400):
    #         duration  = divmod( duration_secs, 3600 )[0]
    #         dur_units = 'hours'
    #     elif (duration_secs <  31536000):          
    #         duration = divmod( duration_secs, 86400 )[0]
    #         dur_units = 'days'
    #     else:
    #         duration = divmod( duration_secs, 86400 )[0]
    #         dur_units = 'days'
    #               
    #     return (duration, dur_units)
     
    #   get_duration()
    #--------------------------------------------------------------------
    def get_download_format(self):
    
        return self.download_format.value
        
    #   get_download_format()
    #--------------------------------------------------------------------
    def clear_download_log(self):
    
        self.download_log.value = ''

    #   clear_download_log()
    #--------------------------------------------------------------------
    def append_download_log(self, msg):
    
        ## type_str = str( type(msg) )
        ## if (type_str == "<class 'list'>"):
        
        if (isinstance( msg, list)):
            for string in msg:
                self.download_log.value += (string + '\n')
        else:
            self.download_log.value += (msg + '\n')

    #   append_download_log()
    #--------------------------------------------------------------------   
    def print_user_choices(self):

        if not(hasattr(self, 'dataset')):
           msg = 'ERROR: No dataset has been selected.'
           self.append_download_log( msg )
           return  ############
       
        start_datetime_obj = self.get_start_datetime_obj()
        if (start_datetime_obj is not None):
            start_date = str( start_datetime_obj.date() )
            start_time = str( start_datetime_obj.time() )
        else:
            start_date = 'unknown'
            start_time = 'unknown'
        
        end_datetime_obj = self.get_end_datetime_obj()
        if (end_datetime_obj is not None):
            end_date = str( end_datetime_obj.date() )
            end_time = str( end_datetime_obj.time() )
        else:
            end_date = 'unknown'
            end_time = 'unknown'
            
        #------------------------------------------        
        # Show message in downloads panel log box
        #------------------------------------------       
        msg1 = 'var short name  = ' + self.get_var_shortname()
        msg2 = 'download format = ' + self.get_download_format()
        msg3 = 'map bounds = ' + str(self.get_map_bounds( FROM_MAP=False ))
        msg4 = 'start date and time = ' + start_date + ' ' + start_time
        msg5 = 'end date and time   = ' + end_date   + ' ' + end_time
        ## msg6 = 'opendap package = ' + self.get_opendap_package()
        msgs = [msg1, msg2, msg3, msg4, msg5]
        self.append_download_log( msgs )

    #   print_user_choices()
    #--------------------------------------------------------------------
    def download_data(self, caller_obj=None):

        #-------------------------------------------------
        # Note: After a reset, self still has a dataset,
        #       but short_name was reset to ''.
        #-------------------------------------------------
        short_name = self.get_var_shortname()
        if (short_name == ''):
            msg = 'Sorry, no variable has been selected.'
            self.download_log.value = msg
            return

        #----------------------------------------------------
        # Note: This is called by the "on_click" method of
        # the "Go" button beside the Dropdown of filenames.
        # In this case, type(caller_obj) =
        # <class 'ipywidgets.widgets.widget_button.Button'>
        #----------------------------------------------------
        ## status = self.download_status
        self.print_user_choices()
        #--------------------------------------------------
        # print_user_choices() already displayed error msg
        #--------------------------------------------------
        if not(hasattr(self, 'dataset')):
            return
 
        #----------------------------------------           
        # Get names of the variables dimensions
        #----------------------------------------
        dim_list = self.dataset[ short_name ].dimensions

        #--------------------------------------
        # Uncomment to test other time_deltas
        #------------------------------------------
        # If test time_delta is too small, we'll
        # get a start_index that is out of range.
        # Next 3 worked in some SST tests.
        #------------------------------------------
        # self.time_delta = '0000-02-00 00:00:00'
        # self.time_delta = '0000-00-30 12:00:00'
        # self.time_delta = '0001-00-00 00:00:00'

        #----------------------------------------------
        # Is there a time variable ?  If so, use time
        # range selected in GUI to clip the data.
        #---------------------------------------------- 
        (t_i1, t_i2) = self.get_new_time_index_range( REPORT=True)
           
        #--------------------------------------------
        # Is there a lat variable ?  If so, use lat
        # range selected in GUI to clip the data.
        # Default is the full range.
        #--------------------------------------------
        (lat_i1, lat_i2) = self.get_new_lat_index_range( REPORT=True)
            
        #--------------------------------------------
        # Is there a lon variable ?  If so, use lon
        # range selected in GUI to clip the data.
        # Default is the full range.
        #--------------------------------------------
        (lon_i1, lon_i2) = self.get_new_lon_index_range( REPORT=True)

        #--------------------------------------        
        # Did user set a spatial resolution ?
        #--------------------------------------
                

        # Asynchronous download. How do we know its here?
        # print('Downloading variable:', short_name, '...' )
        # print('Variable saved in: balto.user_var')
        # print()
        
        msg1 = 'Downloading variable: ' + short_name + '...'   
        msg2 = 'Variable saved in:  balto.user_var'
        msg3 = ' '
        self.append_download_log( [msg1, msg2, msg3] )

        #---------------------------------------------        
        # Convert reference to actual numpy variable
        # which causes it to be downloaded, and then
        # store it into balto.user_var.
        #---------------------------------------------------
        # This grid includes var and its dimension vectors.
        # Note:  type(pydap_grid) = pydap.model.GridType
        #---------------------------------------------------
        pydap_grid = self.dataset[ short_name ]
        ndims = len( pydap_grid.dimensions ) # (e.g. time, lat, lon)
        ## data_obj  = self.dataset[ short_name ]
        ## data_dims = data_obj.dimensions
        ## ndim      = len( data_dims )

        #------------------------------------------------
        # Actually download the data here to a variable
        # in the notebook, but restrict indices first,
        # to only download the required data.
        #------------------------------------------------
        if (ndims == 3):
            #-------------------------------------
            # Assume dims are:  (time, lat, lon)
            #------------------------------------------
            # After subscripting, grid still has type:
            #    pydap.model.GridType
            #------------------------------------------
            if (lat_i1 is None) or (lon_i1 is None):
                if (t_i1 is None):
                    grid = pydap_grid[:]
                else:
                    grid = pydap_grid[t_i1:t_i2, :, :]
            else:
                if (t_i1 is None):
                    grid = pydap_grid[:, lat_i1:lat_i2, lon_i1:lon_i2]
                else: 
                    grid = pydap_grid[t_i1:t_i2, lat_i1:lat_i2, lon_i1:lon_i2]
        #----------------------------------------
        elif (ndims == 1):  # time series
            if (t_i1 is None):
                grid = pydap_grid[:]
            else:
                grid = pydap_grid[t_i1:t_i2]
        #-----------------------------------
        elif (ndims == 2):  # spatial grid
            #-------------------------------
            # Assume dims are:  (lat, lon)
            #-------------------------------
            if (lat_i1 is None) or (lon_i1 is None):
                grid = pydap_grid[:]
            else:
                grid = pydap_grid[lat_i1:lat_i2, lon_i1:lon_i2]
        #------------------------------------
        else:
            grid = pydap_grid[:]

        #--------------------------------------------------
        # Note: type(pydap_grid)   = pydap.model.gridtype
        #       type(grid)         = pydap.model.gridtype
        #       type(grid[:].data) = list
        #       type(grid.data)    = list
        #--------------------------------------------------
        # Subscript by *ranges* doesn't change data type.
        #--------------------------------------------------        
        grid_list = grid.data   ########
        n_list    = len(grid_list)
        var = grid_list[0]
        
        # For testing
        # print('## type(grid) =', type(grid) )
        # print('## type(grid.data) =', type(grid_list) )
        # print('## len(grid.data)  =', n_list )
        # print('## type(var) =', type(var) )
        # print()
    
        times = None   # (defaults)
        lats  = None
        lons  = None
        if (n_list > 1):
            times = grid_list[1]
        if (n_list > 2):
            lats = grid_list[2]
        if (n_list > 3):
            lons = grid_list[3]

        #----------------------------------------------
        # Are lats in reverse order ?  (2020-12-12)
        # MUST DO THIS BEFORE SUBSETTING WITH INDICES
        #----------------------------------------------
#         origin = None
#         if (lats is not None):
#             if (lats[0] > lats[-1]):
#                 origin = 'upper'    # (row major?)
#                 lats.sort()    #############################
#             else:
#                 origin = 'lower'

        #----------------------------------------------      
        # Adjust the longitudes ?
        # MUST DO THIS BEFORE SUBSETTING WITH INDICES
        #----------------------------------------------
#         if (n_list > 3):
#             SIGNED_LONS = True
#             if (SIGNED_LONS):
#                 #----------------------------------------        
#                 # Convert lons to have range [-180,180]
#                 #----------------------------------------
#                 lons = ((lons + 180.0) % 360) - 180
#                 lons.sort()    #################
               
        #-----------------------------      
        # Is there a missing value ?
        # Is there a fill value ?
        #-----------------------------
        atts = pydap_grid.attributes
        REPLACE_MISSING = False
        if ('missing_value' in atts.keys()):
             REPLACE_MISSING = True
             missing_value = pydap_grid.attributes['missing_value']
             w = (var == missing_value)
                  
        #---------------------------------------      
        # Is there a scale factor and offset ?
        #---------------------------------------
        if ('scale_factor' in atts.keys()):
            #---------------------------------------------------
            # Note: var may have type ">i2" while scale_factor
            #       may have type "float64", so need to upcast
            #       var and can't use "*="
            #---------------------------------------------------
            factor = pydap_grid.attributes['scale_factor']
            ## print('type(var) =', type(var))
            ## print('type(factor) =', type(factor))
            var = var * factor
        if ('add_offset' in atts.keys()):
            offset = pydap_grid.attributes['add_offset']
            ## print('type(var) =', type(var))
            ## print('type(offset) =', type(offset))
            var = var + offset
 
        #-----------------------------------------
        # Restore missing values after scaling ?
        #-----------------------------------------  
        if (REPLACE_MISSING):
            var[w] = missing_value

        #-----------------------------------------           
        # Save var into balto object as user_var
        #-----------------------------------------        
        self.user_var = var
        self.user_var_times = times   # (maybe None)
        self.user_var_lats  = lats    # (maybe None)
        self.user_var_lons  = lons    # (maybe None)
        
        #----------------------------------------------------        
        # Could define self.user_var as a list, and append
        # new variables to the list as downloaded.
        # Could also put them into a dictionary.
        #----------------------------------------------------
        

    #   download_data()    
    #--------------------------------------------------------------------
    def show_grid(self, grid, var_name=None, extent=None,
                  cmap='rainbow', xsize=8, ysize=8 ):

        #---------------------------------------------------
        # Note:  extent = [minlon, maxlon, minlat, maxlat]
        #        But get_map_bounds() returns:
        #           (minlon, minlat, maxlon, maxlat)
        #---------------------------------------------------
        if (grid.ndim != 2):
            print('Sorry, show_grid() only works for 2D arrays.')
            return
        
        if (var_name is None):
            var_name = self.data_var_long_name.value
            ## var_name = self.data_var_name.value
        if (extent is None):
            extent = self.get_map_bounds(style='plt.imshow')
            ## (minlon, minlat, maxlon, maxlat) = self.get_map_bounds()
            ## extent = [minlon, maxlon, minlat, maxlat]
        
        bp.show_grid_as_image( grid, var_name, extent=extent,
                        cmap='rainbow', stretch='hist_equal',
                        xsize=xsize, ysize=ysize,
                        nodata_value=None )
                        ## NO_SHOW=False, im_file=None,

    #   show_grid()
    #--------------------------------------------------------------------
    def get_opendap_package(self):
    
        return self.prefs_package.value

    #--------------------------------------------------------------------
    def get_abbreviated_var_name(self, abbreviation ):
    
        map = {
        'lat' : ['geodetic_latitude',  'quantity'],
        'lon' : ['geodetic_longitude', 'quantity'],
        'sst' : ['sea_surface__temperature', 'variable'],
        'temp': ['temperature',  'quantity'],
        'x'   : ['x-coordinate', 'quantity'],
        'y'   : ['y-coordinate', 'quantity'],
        'z'   : ['z-coordinate', 'quantity'] }

        try:
           return map[ abbreviation ]
        except:
           print('Sorry, no matches found for abbreviation.')
           
    #   get_abbreviated_var_name()
    #--------------------------------------------------------------------
    def get_possible_svo_names(self, var_name, SHOW_IRI=False):

        #-----------------------------------------------------      
        # Use the SVO "match phrase" service to get a
        # ranked list of possible SVO variable name matches.
        #-----------------------------------------------------
        # var_name should be a list of words, as a single
        # string, separated by underscores.
        #-----------------------------------------------------
        var_name2 = var_name.replace(' ', '_')
        match_phrase_svc = 'http://34.73.227.230:8000/match_phrase/'    
        match_phrase_url = match_phrase_svc + var_name2 + '/'
        print('Working...')
        
        #-----------------------------------------------------------------       
        # The result is in JSON format, for example:
        # result = { "results": [
        # {"IRI":"result1_IRI", "label":"result1_label", "matchrank": "result1_rank"},
        # {"IRI":"result2_IRI", "label":"result2_label", "matchrank": "result2_rank"} ] }
        #------------------------------------------------------------------        
        result = requests.get( match_phrase_url )
        print('Finished.')
        print()
        json_str = result.text
        # print( json_str )

        json_data  = json.loads( json_str )
        match_list = json_data['results']
        
        for item in match_list:
            ## print('item  =', item)
            if (SHOW_IRI):
                print('IRI   =', item['IRI'])
            print('label =', item['label'])
            print('rank  =', item['matchrank'])
            print()
    
    #   get_possible_svo_names()
    #-------------------------------------------------------------------
    
    
    
         