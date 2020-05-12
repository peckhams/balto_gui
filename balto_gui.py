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

from ipyleaflet import Map
import ipywidgets as widgets
from ipywidgets import Layout
from IPython.display import display, HTML
## from IPython.core.display import display
## from IPython.lib.display import display

# import pydap
import pydap.client   # (for open_url, etc.)
import requests   # for get_filenames()
import time      # for sleep

#------------------------------------------------------------------------
#
#  class balto_gui
#      __init__()
#      show_gui()
#      make_gui()
#      make_data_panel()
#      make_var_panel()
#      make_map_panel()
#      make_dates_panel()
#      make_download_panel()
#      make_prefs_panel()
#      #--------------------------
#      get_map_bounds()
#      replace_map_bounds()
#      replace_map_bounds2()
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
#      get_var_longname()
#      get_var_units()
#      get_var_shape()
#      get_var_dimensions()
#      get_var_dtype()
#      get_var_attributes()
#      print_choices()
#      download_data()
#
#------------------------------------------------------------------------
class balto_gui:
    #--------------------------------------------------------------------
    def __init__(self):

        self.server_url_dir = 'http://test.opendap.org/dap/data/nc/'
        #---------------------------------        
        self.gui_width = 680  # number
        self.att_width = 560  # number
        self.map_width = (self.gui_width - 40)
        #---------------------------------------------------
        self.gui_width_px  = self.pix_str( self.gui_width )
        self.map_width_px  = self.pix_str( self.map_width )
        self.map_height_px = '250px'
        self.att_width_px  = self.pix_str( self.att_width )
        #---------------------------------------------------
        self.url_box_width_px = self.att_width_px                       
        self.date_width_px = '240px'
        self.time_width_px = '200px'
        self.hint_width_px = '90px'
        #---------------------------------------------------
        self.log_box_width_px = self.att_width_px
        self.log_box_height_px = '160px'
        #---------------------------------------------------          
        self.style0     = {'description_width': 'initial'}
        self.style1     = {'description_width': '130px'}
        self.style2     = {'description_width': '80px'}
        self.style3     = {'description_width': '50px'}
        self.date_style = {'description_width': '70px'}
        self.time_style = {'description_width': '70px'}

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
        pad  = widgets.HTML(value=f"<p></p> <p></p>")   # padding
        head = widgets.HTML(value=f"<b><font size=5>BALTO User Interface</font></b>")
        # head = widgets.Label('BALTO User Interface')
        self.gui = widgets.VBox([pad, pad, head, acc])
        
    #   make_gui()
    #--------------------------------------------------------------------
    def make_data_panel(self):

        #-----------------------------------
        # Browse data on an OpenDAP server
        #-----------------------------------
        style1 = self.style1
        att_width_px = self.att_width_px
        url_box_width_px = self.url_box_width_px

        o1 = widgets.Text(description='OpenDAP URL Dir:',
                          value=self.server_url_dir,
                          disabled=False, style=style1,
                          layout=Layout(width=url_box_width_px))
        b1 = widgets.Button(description="Go", layout=Layout(width='50px'))
        o2 = widgets.Dropdown( description='Filename:',
                               options=[''], value='',
                               disabled=False, style=style1,
                               layout=Layout(width=att_width_px) )
        ## o3 = widgets.Select( description='Variable:',
        o3 = widgets.Dropdown( description='Variable:',
                               options=[''], value='',
                               disabled=False, style=style1,
                               layout=Layout(width=att_width_px) )
        o4 = widgets.Text(description='Units:', style=style1,
                          value='', layout=Layout(width=att_width_px) )
        o5 = widgets.Text(description='Shape:', style=style1,
                          value='', layout=Layout(width=att_width_px) )
        o6 = widgets.Text(description='Dimensions:', style=style1,
                          value='', layout=Layout(width=att_width_px) )
        o7 = widgets.Text(description='Data type:', style=style1,
                          value='', layout=Layout(width=att_width_px) )

        url_box = widgets.HBox([o1, b1])  # directory + button
        panel   = widgets.VBox([url_box,o2,o3,o4,o5,o6,o7])       

        self.data_url_dir   = o1  # on an OpenDAP server
        self.data_filename  = o2
        self.data_var_name  = o3
        self.data_var_units = o4
        self.data_var_shape = o5
        self.data_var_dims  = o6
        self.data_var_type  = o7
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
        o2.observe( self.show_dataset_info, names=['options','value'] )
        o3.observe( self.show_var_info, names=['options', 'value'] )
        ## o3.observe( self.show_var_info, names='value' )
        ## o2.observe( self.show_dataset_info, names='All' )
        ## o3.observe( self.show_var_info, names='All' )
 
         #-----------------------------------------------------    
        # It turned out this wasn't an issue.
        #-----------------------------------------------------
        # Note: Method functions have type "method" instead
        #       of "function" and therefore can't be passed
        #       directly to widget handlers like "on_click".
        #       But we can use the "__func__" attribute.
        #-----------------------------------------------------           
#         b1.on_click( self.update_filename_list.__func__ )
#         o2.observe( self.show_dataset_info.__func__ )
#         o3.observe( self.show_var_info.__func__, names='value' )
       
    #   make_data_panel()
    #--------------------------------------------------------------------
#     def make_var_panel(self):
# 
#         n0 = widgets.HTML(value=f"<p> </p>")   # padding
#         n1 = widgets.Text(description='Variable name:',
#                           value='sea surface temperature',
#                           disabled=False, style=style0,
#                           layout=Layout(width='550px') )             

        #------------------------------
        # Example GES DISC opendap URL
        #------------------------------
        # https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHHE.05/2014/
        # 091/3B-HHR-E.MS.MRG.3IMERG.20140401-S000000-E002959.0000.V05B.HDF5.nc
        # ?HQprecipitation[1999:2200][919:1049],lon[1999:2200],lat[919:1049]

        #----------------------------------
        # Example OpenDAP URL for testing
        #----------------------------------
        # http://test.opendap.org/dap/data/nc/coads_climatology.nc

        ## value='http://test.opendap.org/dap/data/nc/coads_climatology.nc',
        ## value='https://gpm1.gesdisc.eosdis.nasa.gov/opendap/',
        
    #   make_var_panel() 
    #--------------------------------------------------------------------    
    def make_map_panel(self):

        map_width_px  = self.map_width_px
        map_height_px = self.map_height_px
        m = Map(center=(0.0, 0.0), zoom=1, 
                layout=Layout(width=map_width_px, height=map_height_px))
        m.on_interaction( self.replace_map_bounds )
        #-----------------------------------------------------
        
        # bbox_style = {'description_width': '130px'}
        bbox_style = {'description_width': '100px'}
        bbox_width_px = '270px'

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
    
        lons  = widgets.VBox([w1, w2])
        lats  = widgets.VBox([w3, w4])
        bbox  = widgets.HBox( [lons, lats])
        panel = widgets.VBox( [m, bbox] )
        
        self.map_window     = m
        self.map_minlon_box = w1
        self.map_maxlon_box = w2
        self.map_maxlat_box = w3
        self.map_minlat_box = w4
        self.map_panel      = panel
        
    #   make_map_panel()
    #--------------------------------------------------------------------  
    def make_datetime_panel(self):

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
        ## d5 = widgets.Label( description=' 00:00:00',
        d5 = widgets.Label( ' 00:00:00',
                     layout=Layout(width=hint_width_px) )
                     #disabled=False, style=hint_style )
        ## d6 = widgets.Label( description=' 00:00:00',
        d6 = widgets.Label( ' 00:00:00',
                     layout=Layout(width=hint_width_px) )
                     #disabled=False, style=hint_style )

                                        
        dates = widgets.VBox([d1, d2])
        times = widgets.VBox([d3, d4])
        hints = widgets.VBox([d5, d6])
        panel = widgets.HBox([dates, times, hints])
                   
        self.datetime_start_date_box = d1
        self.datetime_start_time_box = d3
        self.datetime_end_date_box   = d2
        self.datetime_end_time_box   = d4
        self.datetime_panel          = panel

    #   make_datetime_panel()
    #-------------------------------------------------------------------- 
    def make_download_panel(self):
      
        style0 = self.style0
        f1 = widgets.Dropdown( description='Download Format:',
                               options=['HDF', 'netCDF', 'netCDF4', 'ASCII'],
                               value='netCDF',
                               disabled=False, style=style0)
        pad = widgets.HTML(value=f"<p> </p>")   # padding
        b3  = widgets.Button(description="Download")
        h3  = widgets.HBox([f1, pad, b3])

        # Could use this for output
#         status = widgets.Text(description=' Status:', style=self.style3,
#                               layout=Layout(width='380px') )
       
        width_px  = self.log_box_width_px
        height_px = self.log_box_height_px                       
        log = widgets.Textarea( description='', value='',
                      disabled=False, style=self.style0,
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
    
        s1 = widgets.Dropdown( description='OpenDAP package:',
                               options=['pydap', 'netcdf4'],
                               value='pydap',
                               disabled=False, style=self.style1)
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
            minlon = self.map_window.west
            minlat = self.map_window.south
            maxlon = self.map_window.east
            maxlat = self.map_window.north
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
    def get_start_datetime(self):

        # Need the str()
        d1 = self.datetime_start_date_box
        d3 = self.datetime_start_time_box    
        s1 = str(d1.value) if (d1.value is not None) else 'None'
        s2 = str(d3.value) if (d3.value is not None) else 'None'
        return (s1, s2)

    #--------------------------------------------------------------------
    def get_end_datetime(self):

        d2 = self.datetime_end_date_box 
        d4 = self.datetime_end_time_box
        s1 = str(d2.value) if (d2.value is not None) else 'None'
        s2 = str(d4.value) if (d4.value is not None) else 'None'
        return (s1, s2)

    #--------------------------------------------------------------------
    def get_variable_name(self):

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
        ## opendap_dir = 'http://test.opendap.org/dap/data/nc/'
        
        filenames = self.get_url_dir_filenames()
        
        # This all looks fine.  List of strings.
#         print('len(filenames)  =', len(filenames) )
#         print('type(filenames) =', type(filenames) )
#         print('filenames =', filenames)   ##################
#         return
        
        if (len(filenames) == 0):
            print('Error:  No data files found.')
            return
        #-----------------------------------
        # Update filename list & selection
        #-----------------------------------
        self.data_filename.options = filenames
        self.data_filename.value   = filenames[0]
        ## caller_obj.options = filenames
        ## caller_obj.value   = filenames[0]

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
        self.data_var_name.options = long_names
        self.data_var_name.value   = long_names[0]

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
        var_name = self.data_var_name.value
        if (var_name == ''):
            return
 
        #-----------------------------------------------      
        # Maybe later wrap this block in "try, except"
        #-----------------------------------------------
        # Note: long_name is selected from Dropdown.  
        # var = dataset[ short_name ]
        #----------------------------------------------  
        short_name = self.short_name_map[ var_name ]
        # print('#### short_name =', short_name)
        #----------------------------------------------
        units = self.get_var_units( short_name )
        shape = self.get_var_shape( short_name )
        dims  = self.get_var_dimensions( short_name )
        dtype = self.get_var_dtype( short_name )
        #---------------------------------------------
        self.data_var_units.value = units
        self.data_var_shape.value = shape
        self.data_var_dims.value  = dims
        self.data_var_type.value  = dtype

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
            return short_name

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
        if (type_str[0] == '>'):  type_str = type_str[1:]
        
        if (type_str in type_list): 
            return type_map[ type_str ]
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
            return var.attributes
        else:
            return 'No attributes found.'
    
    #   get_var_attributes()
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------   
    def print_choices(self):

        (start_date, start_time) = self.get_start_datetime()
        (end_date, end_time)     = self.get_end_datetime()
        
        msg = [
        'download format = ' + self.get_download_format(),
        'bounds = ' + str(self.get_map_bounds()),
        'opendap package = ' + self.get_opendap_package(),
        'start date = ' + start_date,
        'start time = ' + start_time,
        'end date = ' + end_date,
        'end time = ' + end_time,
        'variable = ' + self.get_variable_name() ]

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
        log_box = self.download_log_box
        ## status  = self.download_status_box
        log_box.value = 'Download button clicked.'
        self.print_choices()

        #-----------------------------------
        # Actually download the data here
        # to a variable in the notebook
        #-----------------------------------
        
        
    #   download_data()    
    #--------------------------------------------------------------------
        