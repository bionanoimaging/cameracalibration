"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING
import tempfile
from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from cameracalibration.calreadnoise import cal_readnoise
import numpy as np 
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import napari


class CalReadnoiseQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Compute Readnoise/Gain")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        _layers = self.viewer.layers
        if len(_layers)>0:
            for layer in _layers:
                if layer.name == 'dark':
                    bg = layer.data
                if layer.name == 'bright':
                    fg = layer.data
            
            # compute calibration curves
            exportpath = tempfile.gettempdir()
            
            bg_total_mean, gain, Readnoise, mean_el_per_exposure, validmap, figures, Text = cal_readnoise(fg,bg,numBins=100, validRange=None, CameraName=None, correctBrightness=True,
                correctOffsetDrift=True, excludeHotPixels=True, crazyPixelPercentile=98, doPlot=True, exportpath=exportpath,
                brightness_blurring=True, plotWithBgOffset=True)
            
            # convert figures to numpy arrays and display them in napari
            tDriftFg = plt.imread(exportpath+'/correctOffsetDrift.png')
            tDriftBg = plt.imread(exportpath+'/Brightness_Fluctuation.png')
            CalibPlot = plt.imread(exportpath+'/Photon_Calibration.png')
            
            # this does not return the correct shape for some reason...
            #tDriftFg = np.frombuffer(figures[0].canvas.tostring_rgb(), dtype=np.uint8) 
            #tDriftFg = tDriftFg.reshape(figures[0].canvas.get_width_height()[::-1] + (3,))
            
            self.viewer.add_image(tDriftFg, name='tDriftFg')
            self.viewer.add_image(tDriftBg, name='tDriftBg')
            self.viewer.add_image(CalibPlot, name='CalibPlot')
            
        print("The camera has a gain of ", str(gain), " e-/ADU and a readnoise of ", str(Readnoise), " e-")


@magic_factory
def example_magic_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")


# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.
def example_function_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")
