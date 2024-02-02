from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


class ColorMap(QWidget):
    def __init__(self, minv, maxv, parent=None):
        self.max = maxv
        self.min = minv
        super(ColorMap, self).__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.draw_colormap()

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def draw_colormap(self):
        # axes
        ax = self.figure.add_axes([0.05, 0.10, 0.2, 0.8])
        cmap = mpl.cm.jet
        norm = mpl.colors.Normalize(vmin=self.min, vmax=self.max)
        ticks_cm = np.linspace(self.min, self.max, 10, endpoint=True)
        cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                        norm=norm,
                                        ticks=ticks_cm,
                                        orientation='vertical')
        # label_cm = 'punch ratio'
        # cb1.set_label(label=label_cm,weight='bold')
        cb1.ax.tick_params(labelsize=8)
        self.canvas.draw()
