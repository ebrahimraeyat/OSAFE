# -*- coding: utf-8 -*-
# from PySide2.QtCo
from PySide2.QtCore import *
from PySide2.QtGui import *

X, Y = range(2)
CFACTOR, K, TAN, CDRIFT, KDRIFT, TEXP125, TEXP, SYSTEM, LATERAL, RU, HMAX, OMEGA0, CD = range(13)
MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1

QVariant = str


class StructureModel(QAbstractTableModel):

    def __init__(self, build):
        super(StructureModel, self).__init__()
        #self.filename = filename
        self.dirty = False
        self.build = build

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index) |
                Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        row = index.row()
        column = index.column()
        system = self.build.x_system
        Texp = self.build.exp_period_x
        Tan = self.build.x_period_an
        k = self.build.kx
        k_drift = self.build.kx_drift
        c = ''
        c_drift = ''
        if self.build.results[0]:
            c = self.build.results[1]
        if self.build.results_drift[0]:
            c_drift = self.build.results_drift[1]

        if column == Y:
            system = self.build.y_system
            Texp = self.build.exp_period_y
            Tan = self.build.y_period_an
            k = self.build.ky
            k_drift = self.build.ky_drift
            if self.build.results[0]:
                c = self.build.results[2]
            if self.build.results_drift[0]:
                c_drift = self.build.results_drift[2]
        if role == Qt.DisplayRole:
            if row == SYSTEM:
                return QVariant(system.systemType)
            if row == LATERAL:
                return QVariant(system.lateralType)
            if row == HMAX:
                return QVariant(system.maxHeight)
            if row == RU:
                return QVariant(system.Ru)
            if row == OMEGA0:
                return QVariant(system.phi0)
            if row == CD:
                return QVariant(system.cd)
            if row == TEXP:
                return '{0:.4f}'.format(Texp)
            if row == TEXP125:
                return '{0:.4f}'.format(Texp * 1.25)
            if row == TAN:
                return '{0:.4f}'.format(Tan)
            if row == K:
                return '{0:.4f}'.format(k)
            if row == CFACTOR:
                try:
                    return '{0:.4f}'.format(c)
                except:
                    pass
            if row == KDRIFT:
                return '{0:.4f}'.format(k_drift)
            if row == CDRIFT:
                try:
                    return '{0:.4f}'.format(c_drift)
                except:
                    pass
        if role == Qt.BackgroundColorRole:
            # if row == HMAX:
            #     return QVariant(QColor(255, 140, 140))
            if row in (K, CFACTOR):
                return QVariant(QColor(100, 255, 100))
            if row in (KDRIFT, CDRIFT):
                return QVariant(QColor(100, 100, 255))
            if row == TAN:
                return QVariant(QColor(255, 255, 20))
            else:
                return QVariant(QColor(230, 230, 250))
        if role == Qt.FontRole:
            if row in (K, CFACTOR, KDRIFT, CDRIFT):
                font = QFont()
                font.setBold(True)
                font.setItalic(True)
                font.setPointSize(12)
                return font
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        if role == Qt.BackgroundColorRole:
            if orientation == Qt.Vertical:
                # if section == HMAX:
                #     return QVariant(QColor(255, 80, 80))
                if section in (K, CFACTOR):
                    return QVariant(QColor(120, 255, 120))
                if section in (KDRIFT, CDRIFT):
                    return QVariant(QColor(120, 120, 255))
                if section == TAN:
                    return QVariant(QColor(250, 250, 100))
                else:
                    return QVariant(QColor(230, 230, 250))
        if role == Qt.ToolTipRole:
            if section == TEXP125:
                return QVariant(u'مقدار حداکثر زمان تناوب تحلیلی که در محاسبه نیروی زلزله میتوان استفاده کرد.')
            if section == HMAX:
                return QVariant(u'حداکثر ارتفاع مجاز سیستم مقاوم نیروی جانبی')
        if role == Qt.WhatsThisRole:
            if section == TEXP125:
                return QVariant(u'حداکثر زمان تناوبی که میتوان برای ')
        if role == Qt.FontRole:
            if orientation == Qt.Vertical:
                if section in (K, CFACTOR, KDRIFT, CDRIFT):
                    font = QFont()
                    font.setBold(True)
                    font.setPointSize(12)
                    return font
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Vertical:
            if section == SYSTEM:
                return QVariant(u"سیستم سازه")
            if section == LATERAL:
                return QVariant(u'سیستم جانبی')
            if section == HMAX:
                return QVariant('H_max')
            if section == RU:
                return QVariant('Ru')
            if section == CD:
                return QVariant('Cd')
            if section == TEXP:
                return QVariant(u'زمان تناوب تجربی')
            if section == TEXP125:
                return QVariant(u'۱.۲۵ * زمان تناوب تجربی')
            if section == TAN:
                return QVariant(u'زمان تناوب تحلیلی')
            if section == K:
                return QVariant(u'K')
            if section == CFACTOR:
                return QVariant(u'C')
            if section == OMEGA0:
                return QVariant(u'omega_0')
            if section == KDRIFT:
                return QVariant(u'K_drift')
            if section == CDRIFT:
                return QVariant(u'C_drift')
        elif orientation == Qt.Horizontal:
            if section == X:
                return QVariant(u'X راستای')
            if section == Y:
                return QVariant(u'Y راستای')

    def rowCount(self, index=QModelIndex()):
        return 13

    def columnCount(self, index=QModelIndex()):
        return 2

    