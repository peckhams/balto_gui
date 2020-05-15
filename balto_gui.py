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
#  Copyright (C) 2020.  Scott D. Peckham
#
#------------------------------------------------------------------------

from ipyleaflet import Map, basemaps, FullScreenControl, Rectangle
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

# import balto_plot as bp

#------------------------------------------------------------------------
#
#  class balto_gui
#      __init__()
#      show_gui()
#      make_gui()
#      make_data_panel_v0()
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
#      get_start_datetime()
#      get_end_datetime()
#      get_variable_name()
#      get_opendap_package()
#      get_download_format()
#      pix_str()
#      list_to_string()   # for multi-line messages
#      get_url_dir_filenames()
#      update_filename_list()
#      get_opendap_file_url()
#      open_dataset()
#      show_dataset_info()
#      show_var_info()
#      get_all_var_shortnames()
#      get_all_var_longnames()
#      get_all_var_units()
#      --------------------------
#      get_var_longname()
#      get_var_units()
#      get_var_shape()
#      get_var_dimensions()
#      get_var_dtype()
#      get_var_attributes()
#      ----------------------------
#      get_abbreviated_var_name()
#      get_possible_svo_names()
#      ----------------------------
#      print_choices()
#      download_data()
#      show_grid()
#      -------------------------------
#      update_datetime_panel()
#      split_datetime_str()
#      split_date_str()
#      split_time_str()
#      get_datetime_from_days_since()
#      get_duration()
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
        self.map_height        = 250
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
    def show_gui(self):
    
        #------------------------------------   
        # Create & display the complete GUI
        #------------------------------------
        self.make_gui()
        gui_output = widgets.Output()
        display(self.gui, gui_output)
        
    #   show_gui()
    #--------------------------------------------------------------------
    def make_gui(self):

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
        head = widgets.HTML(value=f"<b><font size=5>BALTO User Interface</font></b>")
        # head = widgets.Label('BALTO User Interface')
        self.gui = widgets.VBox([pad, head, acc])
        
    #   make_gui()
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
#     def make_data_panel_v0(self):
# 
#         #-----------------------------------
#         # Browse data on an OpenDAP server
#         #-----------------------------------
#         style1 = self.left_label_style
#         att_width_px = self.att_width_px
#         url_box_width_px = self.url_box_width_px
# 
#         o1 = widgets.Text(description='OpenDAP URL Dir:',
#                           value=self.default_url_dir,
#                           disabled=False, style=style1,
#                           layout=Layout(width=url_box_width_px))
#         b1 = widgets.Button(description="Go", layout=Layout(width='50px'))
#         o2 = widgets.Dropdown( description='Filename:',
#                                options=[''], value='',
#                                disabled=False, style=style1,
#                                layout=Layout(width=att_width_px) )
#         ## o3 = widgets.Select( description='Variable:',
#         o3 = widgets.Dropdown( description='Variable:',
#                                options=[''], value='',
#                                disabled=False, style=style1,
#                                layout=Layout(width=att_width_px) )
#         o4 = widgets.Text(description='Units:', style=style1,
#                           value='', layout=Layout(width=att_width_px) )
#         o5 = widgets.Text(description='Shape:', style=style1,
#                           value='', layout=Layout(width=att_width_px) )
#         o6 = widgets.Text(description='Dimensions:', style=style1,
#                           value='', layout=Layout(width=att_width_px) )
#         o7 = widgets.Text(description='Data type:', style=style1,
#                           value='', layout=Layout(width=att_width_px) )
#         o8 = widgets.Text(description='Status:', style=style1,
#                           value='Ready.', layout=Layout(width=att_width_px) )
#         b2 = widgets.Button(description="Reset", layout=Layout(width='70px'))
# 
#         #-------------------------------
#         # Arrange widgets in the panel
#         #-------------------------------                                  
#         url_box  = widgets.HBox([o1, b1])   # directory + Go button
#         stat_box = widgets.HBox([o8, b2])   # status + Reset button
#         panel    = widgets.VBox([url_box,o2,o3,o4,o5,o6,o7,stat_box])
#         
#         self.data_url_dir   = o1   # on an OpenDAP server
#         self.data_filename  = o2
#         self.data_var_name  = o3
#         self.data_var_units = o4
#         self.data_var_shape = o5
#         self.data_var_dims  = o6
#         self.data_var_type  = o7
#         self.data_status    = o8
#         self.data_panel     = panel
#         #-----------------
#         # Event handlers
#         #-----------------------------------------------------
#         # Note: NEED to set names='value' here.  If names
#         #       keyword is omitted, only works intermittently.
#         #------------------------------------------------------------
#         # "on_click" handler function is passed b1 as argument.
#         # "observe" handler function is passed "change", which
#         # is a dictionary, as argument. See Traitlet events.
#         #------------------------------------------------------------
#         b1.on_click( self.update_filename_list )
#         b2.on_click( self.reset_data_panel )
#         o2.observe( self.show_dataset_info, names=['options','value'] )
#         o3.observe( self.show_var_info, names=['options', 'value'] )
#         ## o3.observe( self.show_var_info, names='value' )
#         ## o2.observe( self.show_dataset_info, names='All' )
#         ## o3.observe( self.show_var_info, names='All' )
#  
#         #-------------------------------------------------------    
#         # It turned out this wasn't an issue, but interesting.
#         #-------------------------------------------------------
#         # Note: Method functions have type "method" instead
#         #       of "function" and therefore can't be passed
#         #       directly to widget handlers like "on_click".
#         #       But we can use the "__func__" attribute.
#         #-------------------------------------------------------           
# #         b1.on_click( self.update_filename_list.__func__ )
# #         o2.observe( self.show_dataset_info.__func__ )
# #         o3.observe( self.show_var_info.__func__, names='value' )
#        
#     #   make_data_panel_v0()
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
        o2.observe( self.show_dataset_info, names=['options','value'] )
        o3.observe( self.show_var_info, names=['options', 'value'] )
        ## o3.observe( self.show_var_info, names='value' )
        ## o2.observe( self.show_dataset_info, names='All' )
        ## o3.observe( self.show_var_info, names='All' )
 
        #-------------------------------------------------------    
        # It turned out this wasn't an issue, but interesting.
        #-------------------------------------------------------
        # Note: Method functions have type "method" instead
        #       of "function" and therefore can't be passed
        #       directly to widget handlers like "on_click".
        #       But we can use the "__func__" attribute.
        #-------------------------------------------------------           
#         b1.on_click( self.update_filename_list.__func__ )
#         o2.observe( self.show_dataset_info.__func__ )
#         o3.observe( self.show_var_info.__func__, names='value' )
       
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

    #   reset_data_panel() 
    #--------------------------------------------------------------------    
    def make_map_panel(self):

        map_width_px  = self.map_width_px
        map_height_px = self.map_height_px
        btn_width_px  = self.pix_str( self.button_width )
        #--------------------------------------------------
        bm_style   = {'description_width': '70px'}
        bbox_style = {'description_width': '100px'}
        bbox_width_px = '260px'
 
        #---------------------
        # Choose the basemap
        #---------------------
        options = self.get_basemap_list()
        bm = widgets.Dropdown( description='Base map:',
                               options=options, value=options[0],
                               disabled=False, style=bm_style,
                               layout=Layout(width='400px') )
        
        #---------------------------------------        
        # Create the map width with ipyleaflet
        #---------------------------------------                
        m = Map(center=(0.0, 0.0), zoom=1,
                layout=Layout(width=map_width_px, height=map_height_px))
        ## m.add_control( FullScreenControl(), position='bottomright' )
        m.add_control( FullScreenControl( position='topright' ) )
        
        #-----------------------------------------------------
        # Does "step=0.01" restrict accuracy of selection ??
        #-----------------------------------------------------
        w1 = widgets.BoundedFloatText(
            value=-180, min=-180, max=180.0, step=0.01,
            # description='West longitude:',
            description='West edge lon:',
            disabled=False, style=bbox_style,
            layout=Layout(width=bbox_width_px) )
    
        w2 = widgets.BoundedFloatText(
            value=180, min=-180, max=180.0, step=0.01,
            # description='East longitude:',
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

        #-----------------------------------   
        # Arrange the widgets in the panel
        #-----------------------------------
        lons  = widgets.VBox([w1, w2])
        lats  = widgets.VBox([w3, w4])
        pads  = widgets.VBox([pd, pd])
        btns  = widgets.VBox([b1, b2])
        bbox  = widgets.HBox( [lons, lats, pads, btns])
        panel = widgets.VBox( [bm, m, bbox] )
        
        self.map_basemap    = bm
        self.map_window     = m
        self.map_minlon_box = w1
        self.map_maxlon_box = w2
        self.map_maxlat_box = w3
        self.map_minlat_box = w4
        self.map_panel      = panel
        ## self.map_bounds     = (-180, -90, 180, 90)

        #-----------------     
        # Event handlers
        #-----------------
        bm.observe( self.change_base_map, names=['options','value'] )
        m.on_interaction( self.replace_map_bounds )
        m.observe( self.zoom_out_to_new_bounds, 'bounds' )
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
    
        self.map_window.center = (0.0, 0.0)
        self.map_window.zoom = 1
        self.map_minlon_box.value = '-180.0'
        self.map_maxlon_box.value = '180.0'
        self.map_minlat_box.value = '-90.0'
        self.map_maxlat_box.value = '90.0'
    
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
#         d7 = widgets.Text( description='Notes:',
#                      disabled=False, style=self.date_style,
#                      layout=Layout(width=full_box_width_px) )                      
        d7 = widgets.Textarea( description='Notes:', value='',
                     disabled=False, style=self.date_style,
                     layout=Layout(width=full_box_width_px, height='80px')) 
                                                             
        dates = widgets.VBox([d1, d2])
        times = widgets.VBox([d3, d4])
        hints = widgets.VBox([d5, d6])
        pad   = widgets.VBox([pp, pp])
        top   = widgets.HBox([dates, times, pad, hints])
        panel = widgets.VBox([top, d7])
        ## panel = widgets.VBox([top, pp, d7])
                   
        self.datetime_start_date = d1
        self.datetime_start_time = d3
        self.datetime_end_date   = d2
        self.datetime_end_time   = d4
        self.datetime_notes      = d7
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
        
        self.download_format  = f1
        self.download_button  = b3
        self.download_log_box = log                   
        self.download_panel = panel
        
        #-----------------
        # Event handlers
        #-----------------
        b3.on_click( self.download_data )
        
    #   make_download_panel()
    #-------------------------------------------------------------------- 
    def make_prefs_panel(self):
    
        left_style = self.left_label_style
        s1 = widgets.Dropdown( description='OpenDAP package:',
                               options=['pydap', 'netcdf4'],
                               value='pydap',
                               disabled=False, style=left_style)
        panel = widgets.VBox([s1])
        self.prefs_panel = panel
        self.prefs_package = s1

    #   make_prefs_panel()
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    def get_map_bounds(self, FROM_MAP=True):

        if (FROM_MAP):
            #------------------------------------      
            # Get the visible map bounds, after
            # interaction such as pan or zoom
            #------------------------------------
            bounds = self.map_window.bounds
            minlat = bounds[0][0]
            minlon = bounds[0][1]
            maxlat = bounds[1][0]
            maxlon = bounds[1][1]  
#             minlon = self.map_window.west
#             minlat = self.map_window.south
#             maxlon = self.map_window.east
#             maxlat = self.map_window.north
            return (minlon, minlat, maxlon, maxlat)
        else:
            #---------------------------------
            # Get map bounds from text boxes
            #---------------------------------
            minlon = self.map_minlon_box.value
            minlat = self.map_minlat_box.value
            maxlon = self.map_maxlon_box.value
            maxlat = self.map_maxlat_box.value
            return (minlon, minlat, maxlon, maxlat)

    #   get_map_bounds()
    #--------------------------------------------------------------------
    def replace_map_bounds(self, event, type=None, coordinates=None):

        #-------------------------------------------
        # Get visible map bounds after interaction    
        # Called by m.on_interaction().
        # Don't need to process separate events?
        #-------------------------------------------
        (minlon, minlat, maxlon, maxlat) = self.get_map_bounds()

        #--------------------------------        
        # Save new values in text boxes
        #--------------------------------
        self.map_minlon_box.value = minlon
        self.map_maxlon_box.value = maxlon
        self.map_maxlat_box.value = maxlat
        self.map_minlat_box.value = minlat
    
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

        (bb_minlon, bb_minlat, bb_maxlon, bb_maxlat) = \
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
    def zoom_out_to_new_bounds_v0(self, caller_obj=None):
     
        (bb_minlon, bb_minlat, bb_maxlon, bb_maxlat) = \
            self.get_map_bounds( FROM_MAP = False )
        bb_midlon = (bb_minlon + bb_maxlon) / 2
        bb_midlat = (bb_minlat + bb_maxlat) / 2 
        bb_center = ( bb_midlat, bb_midlon )
        print('bb_minlon, bb_maxlon =', bb_minlon, bb_maxlon)
        print('bb_minlat, bb_maxlat =', bb_minlat, bb_maxlat)
        zoom = self.map_window.max_zoom  # (usually 18)
        zoom = zoom - 1
        ## print('max_zoom =', self.map_window.max_zoom)
        
        self.map_window.center = bb_center        
        self.map_window.zoom   = zoom
        print('map_window.bounds =', self.map_window.bounds )
        # bounds is read-only
        ## self.map_window.bounds = ((bb_midlat,bb_midlon),(bb_midlat,bb_midlon))
        while (True):
            # time.sleep(0.5)  ######
            (minlon, minlat, maxlon, maxlat) = self.get_map_bounds()
            print('minlon, maxlon =', minlon, maxlon )
            print('minlat, maxlat =', minlat, maxlat )
            if (minlon < bb_minlon) and (maxlon > bb_maxlon) and \
               (minlat < bb_minlat) and (maxlat > bb_maxlat):
               break
            else:
               zoom -= 1
               if (zoom > 0):
                   print('zoom =', zoom)
                   self.map_window.zoom = zoom
               else:
                   break

            (minlon, minlat, maxlon, maxlat) = self.get_map_bounds()
            print('minlon, maxlon =', minlon, maxlon )
            print('minlat, maxlat =', minlat, maxlat )
            if (minlon < bb_minlon) and (maxlon > bb_maxlon) and \
               (minlat < bb_minlat) and (maxlat > bb_maxlat):
               break
            else:
               zoom -= 1
               if (zoom > 0):
                   print('zoom =', zoom)
                   self.map_window.zoom = zoom
               else:
                   break
        
    #   zoom_out_to_new_bounds_v0
    #--------------------------------------------------------------------
    def get_start_datetime(self):

        # Need the str() here
        d1 = self.datetime_start_date
        d3 = self.datetime_start_time
        s1 = str(d1.value) if (d1.value is not None) else 'Not set'
        s2 = str(d3.value) if (d3.value is not None) else 'Not set'
        return (s1, s2)

    #--------------------------------------------------------------------
    def get_end_datetime(self):

        # Need the str() here
        d2 = self.datetime_end_date 
        d4 = self.datetime_end_time
        s1 = str(d2.value) if (d2.value is not None) else 'Not set'
        s2 = str(d4.value) if (d4.value is not None) else 'Not set'
        return (s1, s2)

    #--------------------------------------------------------------------
    def get_variable_short_name(self):

        return self.data_var_name.value

    #--------------------------------------------------------------------
    def get_opendap_package(self):
    
        return self.prefs_package.value

    #--------------------------------------------------------------------
    def get_download_format(self):
    
        return self.download_format.value

    #--------------------------------------------------------------------
    def pix_str(self, num):

        return str(num) + 'px'

    #--------------------------------------------------------------------
    def list_to_string( self, array ):

        s = ''
        for item in array:
            s = s + item + '\n'
        return s

    #   list_to_string()
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
            if ('"sameAs": "http://' in line) and ('www' not in line):
                line = line.replace('.html"', '')
                parts = line.split("/")
                filename = parts[-1]
                filenames.append( filename )
        return filenames
    
    #   get_url_dir_filenames()
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

        opendap_url = self.opendap_file_url
        dataset = pydap.client.open_url( opendap_url )
        
        self.dataset = dataset

    #   open_dataset()
    #--------------------------------------------------------------------
    def show_dataset_info(self, change=None):

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
#         self.data_var_name.options = long_names
#         self.data_var_name.value   = long_names[0]

        #------------------------------------
        # Show other info for this variable
        #------------------------------------
        self.show_var_info()
   
    #   show_dataset_info() 
    #--------------------------------------------------------------------
    def show_var_info(self, change=None):

        #-------------------------------------------------------
        # Note: When used as a callback/handler function for a
        #       widget's "observe" method, a dictionary called
        #       "change" is passed to this function.  This
        #       callback fails without the "change=None".
        #       The type of "change" is:
        #       <class 'traitlets.utils.bunch.Bunch'>
        #-------------------------------------------------------
        short_name = self.data_var_name.value
        if (short_name == ''):
            return
         
        #-----------------------------------------------      
        # Maybe later wrap this block in "try, except"
        #-----------------------------------------------
        # Note: long_name is selected from Dropdown.  
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

        #-------------------------------------------
        # Try to show date range in datetime panel
        #-------------------------------------------
        self.update_datetime_panel()
        
    #   show_var_info()
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
        match_phrase_svc = 'http://34.73.227.230:8000/match_phrase/'    
        match_phrase_url = match_phrase_svc + var_name + '/'
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
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------   
    def print_choices(self):

        if (hasattr(self, 'dataset')):
           msg0 = []
        else:
           msg0 = ['ERROR: No dataset has been selected.']
       
        (start_date, start_time) = self.get_start_datetime()
        (end_date, end_time)     = self.get_end_datetime()
        
        msg = [
        'var short name  = ' + self.get_variable_short_name(),
        'download format = ' + self.get_download_format(),
        'map bounds = ' + str(self.get_map_bounds( FROM_MAP=False )),
        ## 'bounds = ' + str(self.get_map_bounds()),
        'start date = ' + start_date,
        'start time = ' + start_time,
        'end date = ' + end_date,
        'end time = ' + end_time ]
        ## 'opendap package = ' + self.get_opendap_package(),
        msg = msg0 + msg

        #------------------------------------------        
        # Show message in downloads panel log box
        #------------------------------------------
        msg_str = self.list_to_string( msg )
        self.download_log_box.value = msg_str

    #   print_choices()
    #--------------------------------------------------------------------
    def download_data(self, caller_obj=None):

 
        #----------------------------------------------------
        # Note: This is called by the "on_click" method of
        # the "Go" button beside the Dropdown of filenames.
        # In this case, type(caller_obj) =
        # <class 'ipywidgets.widgets.widget_button.Button'>
        #----------------------------------------------------
        ## status  = self.download_status_box
        ## log_box = self.download_log_box
        ## log_box.value = 'Download button clicked.'
        self.print_choices()
        #----------------------------------------------
        # print_choices() already displayed error msg
        #----------------------------------------------
        if not(hasattr(self, 'dataset')):
            return
            
        #--------------------------------------------
        # Is there a lat variable ?  If so, use lat
        # range selected in GUI to clip the data.
        #--------------------------------------------

        #--------------------------------------------
        # Is there a lon variable ?  If so, use lon
        # range selected in GUI to clip the data.
        #--------------------------------------------

        #----------------------------------------------
        # Is there a time variable ?  If so, use time
        # range selected in GUI to clip the data.
        #----------------------------------------------
             
        #--------------------------------------        
        # Did user set a spatial resolution ?
        #--------------------------------------
                
        #-----------------------------------
        # Actually download the data here
        # to a variable in the notebook
        #-----------------------------------      
        short_name = self.data_var_name.value
        print()
        print('Downloading variable:', short_name, '...' )
        # Asynchronous download. How do we know its here?
        print('Variable saved in: balto.user_var')
        
        #---------------------------------------------        
        # Convert reference to actual numpy variable
        # which causes it to be downloaded, and then
        # store it into balto.user_var.
        #---------------------------------------------
        data_ref  = self.dataset[ short_name ]
        data_dims = data_ref.dimensions
        ndim      = len( data_dims )
        var = data_ref.array[:].data  ## (all indices of data)
        ### var = data_ref[:].array[:].data         
        self.user_var = var 

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
            (minlon, minlat, maxlon, maxlat) = self.get_map_bounds()
            extent = [minlon, maxlon, minlat, maxlat]
        
        bp.show_grid_as_image( grid, var_name, extent=extent,
                        cmap='rainbow', xsize=xsize, ysize=ysize )
                        ## stretch='hist_equal')
                        ## NO_SHOW=False, im_file=None,

    #   show_grid()
    #--------------------------------------------------------------------
    def update_datetime_panel(self):
 
        ## short_names = self.dataset.keys()
        info = []   
        short_names = self.var_short_names
        if ('time' in short_names):
            self.time_obj = self.dataset.time
            self.time_var = self.time_obj.data[:]
        elif ('TIME' in short_names):
            self.time_obj = self.dataset.TIME
            self.time_var = self.time_obj.data[:]
        else:
            msg = 'Unable to find times for this dataset.'
            self.datetime_notes.value = msg
            return
        #----------------------------------------------------
        # Use min and max times, vs. "actual_range" ??
        min_time = self.time_var.min()
        max_time = self.time_var.max()
        self.time_range = [min_time, max_time]
        msg = 'Time range for this dataset = '
        msg += '(' + str(min_time) + ', ' + str(max_time) + ')'
        info.append( msg )
        #----------------------------------------------------        
        if (hasattr(self.time_obj, 'actual_range')):
            range_str = str( self.time_obj.actual_range )
            msg = 'Time "actual_range" is: ' + range_str
            info.append( msg )
            ### self.time_range = self.time_obj.actual_range
        else:
            msg = 'Unable to find "actual range" for times.'
            self.datetime_notes.value = msg
            return
        #----------------------------------------------------
        if (hasattr(self.time_obj, 'units')):
            self.time_units = self.time_obj.units
            msg = 'Time "units" are: ' + self.time_units
            info.append( msg )
        else:
            msg = 'Unable to find "units" for times.'
            self.datetime_notes.value = msg
            return
        #----------------------------------------------------
        s = self.time_units
        if (s.startswith('days since ')):
            n = len('days since ')
            origin_datetime = s[n:]
            odt = origin_datetime
            days_since1    = self.time_range[0]
            days_since2    = self.time_range[1]
            start_datetime = self.get_datetime_from_days_since(days_since1, odt)
            end_datetime   = self.get_datetime_from_days_since(days_since2, odt)
            (start_date, start_time) = self.split_datetime_str( start_datetime )
            (end_date, end_time)     = self.split_datetime_str( end_datetime )
            self.datetime_start_date.value = start_datetime
            self.datetime_end_date.value   = end_datetime
            self.datetime_start_time.value = str(start_time)
            self.datetime_end_time.value   = str(end_time)
            #----------------------------------
            # This also works, but more steps
            #----------------------------------
            # (y1,m1,d1) = self.split_date_str( start_date )
            # (y2,m2,d2) = self.split_date_str( end_date )
            # self.datetime_start_date.value = datetime.date(y1, m1, d1)
            # self.datetime_end_date.value   = datetime.date(y2, m2, d2)  

        self.datetime_notes.value = self.list_to_string( info )

    #   update_datetime_panel()
    #--------------------------------------------------------------------  
    def split_datetime_str(self, datetime_obj, datetime_sep=' '):
      
        datetime_str = str(datetime_obj)
        parts = datetime_str.split( datetime_sep )
        date_str = parts[0]
        time_str = parts[1]
        return (date_str, time_str)

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
    def get_datetime_from_days_since(self, days_since, origin_datetime):

        #--------------------------------------------- 
        # e.g. origin_datetime = '1800-1-1 00:00:00'
        #--------------------------------------------- 
        (origin_date, origin_time) = self.split_datetime_str( origin_datetime )
        (y, m,  d) = self.split_date_str( origin_date )
        (h, m2, s) = self.split_time_str( origin_time )
        origin_obj = datetime.datetime(y, m, d, h, m2, s)

        #---------------------------------------------        
        # Create new datetime object from days_since
        #---------------------------------------------
        delta      = datetime.timedelta( days_since )
        new_dt_obj = (origin_obj + delta)
        # print('new_dt_obj =', new_dt_obj)
        # print('type(new_dt_obj) =', type(new_dt_obj))
        # print('new_dt_obj =', net_dt_obj.strftime('%Y-%m-%d %H:%M:%S'))

        return new_dt_obj

    #   get_datetime_from_days_since()
    #--------------------------------------------------------------------
    def get_duration(start_date=None, start_time=None,
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
    #-------------------------------------------------------------------     