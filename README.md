# balto_gui
An Interactive GUI for BALTO in a Jupyter notebook

This respository creates a GUI (graphical user interface) for the BALTO (Brokered Alignment of Long-Tail Observations) project. BALTO is funded by the NSF EarthCube program. The GUI aims to provide a simplified and customizable method for users to access data sets of interest on servers that support the OpenDAP data access protocol. This interactive GUI runs within a Jupyter notebook and uses the Python packages: <b>ipywidgets</b> (for widget controls), <b>ipyleaflet</b> (for interactive maps), <b>pydap</b> (an OpenDAP client), <b>matplotlib</b> (for plotting functions) and <b>cartopy</b> (for map projections).

The Python source code to create the GUI and to process events is in a module called <b>balto_gui.py</b> that must be found in the same directory as this Jupyter notebook.  Python source code for visualization of downloaded data is given in a module called <b>balto_plot.py</b>.

This GUI consists of mulitiple panels, and supports both a <b>tab-style</b> and an <b>accordion-style</b>, which allows you to switch between GUI panels without scrolling in the notebook.

You can run the notebook in a browser window without installing anything on your computer, using something called Binder. Look for the Binder icon below and a link labeled "Launch Binder".  This sets up a server in the cloud that has all the required dependencies and lets you run the notebook on that server.  (Sometimes this takes a while, however.)

To run this Jupyter notebook without Binder, it is recommended to install Python 3.7 from an Anaconda distribution and to then create a conda environment called <b>balto</b>. Simple instructions for how to create a conda environment and install the software are given in Appendix 1 of version 2 (v2) of the notebook.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/peckhams/balto_gui/master?filepath=BALTO_GUI_v2.ipynb)
<br>

[![NSF-1740696](https://img.shields.io/badge/NSF-1740696-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1740696)
<br>


