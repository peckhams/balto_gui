# balto_gui
Interactive GUI for BALTO in a Jupyter notebook

This respository creates a GUI (graphical user interface) for the BALTO (Brokered Alignment of Long-Tail Observations) project. BALTO is funded by the NSF EarthCube program. The GUI aims to provide a simplified and customizable method for users to access data sets of interest on servers that support the OpenDAP data access protocol. This interactive GUI runs within a Jupyter notebook and uses the Python packages: <b>ipywidgets</b>, <b>ipyleaflet</b> and <b>pydap</b>.

The Python source code to create the GUI and to process events is in a module called <b>balto_gui.py</b> that must be found in the same directory as this Jupyter notebook.

This is an accordion-style GUI, which allows you to switch between GUI panels without scrolling in the notebook.

You can run the notebook in a browser window without installing anything on your computer, using something called Binder. Look for the Binder icon and a link labeled "Launch Binder".

To run this Jupyter notebook without Binder, it is recommended to install Python 3.7 from an Anaconda distribution and to then create a conda environment called balto. Instructions for how to create a conda environment are given in Appendix 1 of version 2 of the notebook.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mariutzica/balto_gui/83d7700936c6236b3f890a231664855bea97fe83)
