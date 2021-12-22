# -*- coding: utf-8 -*-

from __future__ import division
import os
import sys
from math import sqrt
import copy
import uuid

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QItemDelegate, QTextEdit, QLineEdit, QDoubleSpinBox, QMessageBox
abs_path = os.path.dirname(__file__)
sys.path.insert(0, abs_path)
import pandas as pd
import numpy as np

from slender_params import slenderParameters
from sectionproperties.pre.sections import ISection, PfcSection, RectangularSection, MergedSection
from sectionproperties.analysis.cross_section import CrossSection
from sectionproperties.analysis import solver

column_count = 18
NAME, AREA, ASX, ASY, IX, IY, ZX, ZY, \
    Sx, Sy, RX, RY, CW, J, BF, TF, D, TW = range(column_count)

LH, TH, LV, TV, LW, _TW, DIST, ISTBPLATE, ISLRPLATE, ISWEBPLATE, USEAS, DUCTILITY, ISDOUBLE, \
    ISSOUBLE, SECTIONSIZE, SECTIONTYPE, CONVERT_TYPE, ISCC = range(18)

MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1


class Section(object):
    sectionType = {'IPE': 'STEEL_I_SECTION',
                   'UNP': 'STEEL_I_SECTION',
                   'CPE': 'STEEL_I_SECTION',
                   'BOX': 'STEEL_I_SECTION',
                   'UPA': 'STEEL_I_SECTION',
                   }

    def __init__(self, cc=0, composite=None, useAs='B', ductility='M',
                 TBPlate=None, LRPlate=None, webPlate=None, slender=None, isDouble=False,
                 isSouble=False, convert_type='Compaction', geometry_list=[],
                 is_closed=False, **kwargs):
        self.type = kwargs['_type']
        self.name = kwargs['name']
        self.area = kwargs['area']
        self.xm = kwargs['xm']
        self.ym = kwargs['ym']
        self.xmax = kwargs['xmax']
        self.ymax = kwargs['ymax']
        self.ASy = kwargs['ASy']
        self.ASx = kwargs['ASx']
        self.Ix = kwargs['Ix']
        self.Iy = kwargs['Iy']
        self.Zx = kwargs['Zx']
        self.Zy = kwargs['Zy']
        self.bf = kwargs['bf']
        self.tf = kwargs['tf']
        self.d = kwargs['d']
        self.tw = kwargs['tw']
        self.r1 = kwargs['r1']
        self.cw = kwargs['cw']
        self.J = kwargs['J']
        self.cc = cc
        self.composite = composite
        self.useAs = useAs
        self.ductility = ductility
        self.convert_type = convert_type
        self.TBPlate = TBPlate
        self.LRPlate = LRPlate
        self.webPlate = webPlate
        self.slender = slender
        self.isDouble = isDouble
        self.isSouble = isSouble
        self.geometry_list = geometry_list
        self.is_closed = is_closed
        self.calculateSectionProp()
        try:
            self.baseSection = kwargs['baseSection']
        except:
            self.baseSection = self
        try:
            self.bf_equivalentI, self.tf_equivalentI, self.d_equivalentI, self.tw_equivalentI = \
                self.equivalentSectionI()
        except AttributeError:
            self.bf_equivalentI, self.tf_equivalentI, self.d_equivalentI, self.tw_equivalentI = \
                self.bf, self.tf, self.d, self.tw

        self.V2, self.V3 = self.shear_coefftiont()

        if convert_type == 'Shear':
            self.bf_equivalentI, self.tf_equivalentI, self.d_equivalentI, self.tw_equivalentI = \
                self.equivalent_section_to_I_with_shear_correction()
        self.components = []
        self.conversions = {}
        self.uid = str(uuid.uuid4().int)

    def equivalent_section_to_I_with_shear_correction(self):
        BF = self.xmax
        D = self.ymax
        tw = self.ASy / D
        tf = self.ASx / (2 * BF)
        return BF, tf, D, tw

    def calculateSectionProp(self):
        self.Sx = self.Ix / self.ym
        self.Sy = self.Iy / (self.xmax - self.xm)
        self.Rx = sqrt(self.Ix / self.area)
        self.Ry = sqrt(self.Iy / self.area)

    

    def j_func(self):
        self.solve_warping()
        self.warping_section.calculate_warping_properties()
        self.J = self.warping_section.get_j()

    def create_warping_section(self):
        geometry = MergedSection(self.geometry_list)
        geometry.clean_geometry(verbose=True)
        n = len(self.geometry_list)
        mesh = geometry.create_mesh(mesh_sizes=n * [50])
        self.warping_section = CrossSection(geometry, mesh)

    def solve_warping(self):
        if not hasattr(self, 'warping_section'):
            self.create_warping_section()
        self.warping_section.calculate_geometric_properties()

    @staticmethod
    def exportXml(fname, sections):
        fh = open(fname, 'w')
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n'
                 '<PROPERTY_FILE xmlns="http://www.csiberkeley.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.csiberkeley.com CSIExtendedSectionPropertyFile.xsd">\n'
                 '   <EbrahimRaeyat_Presents>\n'
                 '      <Comment_on_CopyRight> This database is provided by: EbrahimRaeyat, (2021); http://www.ebrahimraeyat.blog.ir </Comment_on_CopyRight>\n'
                 '   </EbrahimRaeyat_Presents>\n'
                 '  <CONTROL>\n'
                 '      <FILE_ID>CSI Frame Properties</FILE_ID>\n'
                 '      <VERSION>1</VERSION>\n'
                 '      <LENGTH_UNITS>mm</LENGTH_UNITS>\n'
                 '      <FORCE_UNITS>kgf</FORCE_UNITS>\n'
                 '  </CONTROL>\n\n')
        for section in sections:
            fh.write(section.xml)
        fh.write('\n</PROPERTY_FILE>')
        return True, "Exported section properties to "    # "%s" % (QFileInfo(fname).fileName())

    @staticmethod
    def export_to_autocad(fname, sections):
        fh = open(fname, 'w')
        for section in sections:
            try:
                fh.write(section.autocadScrText)
            except AttributeError:
                pass
        return True, "Exported section properties to %s" % (QFileInfo(fname).fileName())

    @staticmethod
    def export_to_xlsm(fname, sections):
        import os
        IPES = pd.DataFrame(columns=['TYPE', 'EDI_LABEL', 'LABEL', 'T_F', 'A', 'D', 'BF', 'TW',
                                     'TF', 'KDES', 'KDET', 'IX', 'ZX', 'SX', 'RX', 'ASX', 'IY', 'ZY', 'SY',
                                     'RY', 'ASY', 'J', 'CW'], index=range(len(sections) + 1))

        fname_pro = fname.with_suffix('.pro')
        IPES['TYPE'][:] = 'W'
        IPES['TYPE'][0] = str(fname_pro)
        IPES['EDI_LABEL'][0] = len(sections)
        for row, section in enumerate(sections, start=1):
            IPES['EDI_LABEL'][row] = IPES['LABEL'][row] = section.name
            IPES['T_F'][row] = ''
            IPES['A'][row] = section.area
            IPES['D'][row] = section.d_equivalentI
            IPES['BF'][row] = section.bf_equivalentI
            IPES['TW'][row] = section.tw_equivalentI
            IPES['TF'][row] = section.tf_equivalentI
            IPES['KDES'][row] = ''
            IPES['KDET'][row] = ''
            IPES['IX'][row] = section.Ix
            IPES['ZX'][row] = section.Zx
            IPES['SX'][row] = section.Sx
            IPES['RX'][row] = section.Rx
            IPES['ASX'][row] = section.ASx
            IPES['IY'][row] = section.Iy
            IPES['ZY'][row] = section.Zy
            IPES['SY'][row] = section.Sy
            IPES['RY'][row] = section.Ry
            IPES['ASY'][row] = section.ASy
            IPES['J'][row] = section.J
            IPES['CW'][row] = section.cw

        from openpyxl import load_workbook

        original_xlsm = os.path.join(abs_path, "data", "Proper.xlsm")
        book = load_workbook(original_xlsm, keep_vba=True)
        writer = pd.ExcelWriter(fname, engine='openpyxl')
        writer.book = book
        IPES.to_excel(writer, sheet_name='I-Wide Flange Data', index=False)
        writer.save()
        writer.close()

    def equivalentSectionI(self, useAs=None, ductility=None):

        if self.baseSection.type in ('UNP', 'UPA'):
            bf = self.baseSection.bf * 2
        else:
            bf = self.baseSection.bf
        if not self.composite:
            return bf, self.tf, self.d, self.tw

        if self.isSouble:
            return 3 * self.bf, 3 * self.tf, self.d, self.tw

        if self.type == 'BOX':
            if not (bool(self.TBPlate) and bool(self.LRPlate)):
                raise AttributeError('You must have for side plate!')
            return self.TBPlate.bf, self.TBPlate.tf, \
                (self.LRPlate.tf + 2 * self.TBPlate.tf), 2 * self.LRPlate.bf

        composite = str(self.composite)
        if not useAs:
            useAs = str(self.useAs)
        if not ductility:
            ductility = str(self.ductility)
        xm = self.baseSection.xm

        tf = self.baseSection.tf
        d = self.baseSection.d
        tw = self.baseSection.tw
        r = self.baseSection.r1
        if self.cc:
            c = self.cc
        else:
            c = 0
        if bool(self.TBPlate):
            B1 = self.TBPlate.bf
            if B1 > self.xmax:
                B1 = self.xmax
            t1 = self.TBPlate.tf

        lr_plate_ratio = None
        if bool(self.LRPlate):
            B2 = self.baseSection.d
            t2 = self.LRPlate.bf
            lr_plate_ratio = B2 / t2

        if bool(self.webPlate):
            if lr_plate_ratio:
                if self.webPlate.tf / self.webPlate.bf > lr_plate_ratio:
                    B2 = self.webPlate.tf
                    t2 = self.webPlate.bf
            else:
                B2 = self.webPlate.tf
                t2 = self.webPlate.bf

        parameters = slenderParameters[composite][useAs][ductility]
        # BF = eval(parameters['BF'])
        BF = self.xmax
        tfCriteria = eval(parameters['tfCriteria'])
        if tfCriteria:
            TF = eval(parameters['TF'][0])
        else:
            TF = eval(parameters['TF'][1])
        D = eval(parameters['D'])
        twCriteria = eval(parameters['twCriteria'])
        if twCriteria:
            TW = eval(parameters['TW'][0])
        else:
            TW = eval(parameters['TW'][1])

        # if self.baseSection.type == 'UNP':
            # TF = .5 * TF

        return BF, TF, D, TW

    def shear_coefftiont(self):
        if self.baseSection != self:
            ASyEtabs = self.d_equivalentI * self.tw_equivalentI
            ASxEtabs = 2 * self.bf_equivalentI * self.tf_equivalentI
            V2 = self.ASy / ASyEtabs
            V3 = self.ASx / ASxEtabs
        else:
            V2 = 1
            V3 = 1

        # self.equalSlendersParamsEtabs()

        return V2, V3

        if self.isEquivalenIpeSlender():
            self.slender = u'لاغر'
        else:
            self.slender = u'غیرلاغر'


# def equalSlendersParams(BF, TF, D, TW):
    #'''Return BF, TF, D, TW for equivalent I section to
    # correct calculation of AS2 and AS3 that etabs calculate
    # automatically and change user input for this parameters.'''
    # ASx = self.ASx
    # ASy = self.ASy

    # FS = BF / (2 * TF)
    # TF = sqrt((.6 * ASx) / FS)
    # BF = FS * TF
    # WS = (D - 2 * TF) / TW
    # delta = TF ** 2 + 4 * (ASy * WS)
    # D = (3 * TF + sqrt(delta)) / 2
    # TW = (D - 2 * TF) / WS

    # return BF, TF, D, TW

    # def equalSlendersParamsEtabs(self):
        #'''Return BF, TF, D, TW for equivalent I section to
        # correct calculation of AS2 and AS3 that etabs calculate
        # automatically and change user input for this parameters.
        # FS = flange slender
        # WS = web slender'''

        # FS = self.bf / (2 * self.tf)
        # WS = (self.d - 2 * self.tf) / self.tw
        # TF = sqrt((.25 * self.ASx) / FS)
        # BF = 2 * FS * TF
        # D = TF + sqrt(TF ** 2 + WS * self.ASy)
        # TW = (D - 2 * TF) / WS

        # self.bf = BF
        # self.tf = TF
        # self.d = D
        # self.tw = TW

    def isEquivalenIpeSlender(self):
        '''This function gives a equivalent ipe section and
            check it's slender'''

        slenderParameters = {'flang': {'B': {'O': 0.76, 'M': 0.76, 'H': 0.60}, 'C': {'O': 1.28, 'M': 0.76, 'H': 0.60}},
                             'web': {'B': {'O': 3.76, 'M': 3.76, 'H': 2.45}, 'C': {'O': 1.49, 'M': 1.12, 'H': 0.77}}}

        E = 2e6
        Fy = 2400
        w = sqrt(E / Fy)
        useAs = str(self.useAs)
        ductility = str(self.ductility)
        FS = slenderParameters['flang'][useAs][ductility] * w
        WS = slenderParameters['web'][useAs][ductility] * w

        fs = self.bf_equivalentI / self.tf_equivalentI
        ws = (self.d_equivalentI - 2 * self.tf_equivalentI) / self.tw_equivalentI

        # print 'FS = {}, WS = {}\nfs = {}, ws = {}'.format(FS, WS, fs, ws)

        if fs > FS or ws > WS:
            return True
        else:
            return False


def DoubleSection(section, dist=0):
    '''dist = distance between two sections, 0 mean that there is no
    distance between sections'''
    _type = section.type
    # dist *= 10
    area = 2 * section.area
    xm = section.xmax + dist / 2
    ym = section.ym
    xmax = 2 * section.xmax + dist
    ymax = section.ymax
    ASy = 2 * section.ASy
    ASx = 2 * section.ASx
    Ix = 2 * section.Ix
    Iy = 2 * (section.Iy + section.area * (section.xmax - section.xm + dist / 2) ** 2)
    Zx = 2 * section.Zx
    Zy = section.area * (2 * (section.bf - section.xm) + dist)
    baseSection = section.baseSection
    bf = baseSection.bf
    tf = baseSection.tf
    d = baseSection.d
    tw = baseSection.tw
    r1 = baseSection.r1
    useAs = baseSection.useAs
    ductility = baseSection.ductility
    convert_type = section.convert_type
    cc = dist + 2 * (baseSection.bf - baseSection.xm)
    dw = cc
    hw = d - 2 * tf
    if _type in ('UNP', 'UPA'):
        dw = dist + 2 * bf - tw
    cw = 2 * baseSection.cw + (tw * hw ** 3 / 12) * dw ** 2 / 2
    J = 0
    if dist == 0:
        name = '2' + section.name
        is_closed = True
    else:
        name = '2' + section.name + 'c{:.0f}'.format(cc)
        J = 2 * baseSection.J
        is_closed = False
    new_geometry = copy.deepcopy(baseSection.geometry_list[0])
    # if _type in ("UNP", "UPA"):
    new_geometry.rotate_section(180, rot_point=[bf, d / 2])
    new_geometry.shift = [dist, 0]
    new_geometry.shift_section()
    new_geometry.holes.append([bf + dist / 2, d / 2])
    geometry_list = [baseSection.geometry_list[0], new_geometry]
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                   xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                   Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1, cw=cw, J=J, isDouble=True, cc=cc,
                   useAs=useAs, ductility=ductility, baseSection=baseSection,
                   composite='notPlate', convert_type=convert_type, geometry_list=geometry_list,
                   is_closed=is_closed)


def SoubleSection(section, dist=0):
    '''dist = distance between two sections, 0 mean that there is no
    distance between sections'''
    _type = section.type
    # dist *= 10
    area = 3 * section.area
    xm = (section.xmax * 3 + 2 * dist) / 2
    ym = section.ym
    xmax = 3 * section.xmax + 2 * dist
    ymax = section.ymax
    ASy = 3 * section.ASy
    ASx = 3 * section.ASx
    Ix = 3 * section.Ix
    Iy = 3 * section.Iy + 2 * section.area * (xm - section.xm) ** 2
    Zx = 3 * section.Zx
    Zy = section.Zy + 2 * section.area * (xm - section.xm)
    baseSection = section.baseSection
    bf = baseSection.bf
    tf = baseSection.tf
    d = baseSection.d
    tw = baseSection.tw
    r1 = baseSection.r1
    useAs = baseSection.useAs
    ductility = baseSection.ductility
    convert_type = section.convert_type
    cc = dist + 2 * (baseSection.bf - baseSection.xm)
    J = 0
    if dist == 0:
        name = '3' + section.name
        is_closed = True
    else:
        name = '3' + section.name + 'c{:.0f}'.format(cc)
        J = 3 * baseSection.J
        is_closed = False

    x_shift = bf + dist
    geometry2 = copy.deepcopy(baseSection.geometry_list[0])
    geometry2.shift = [x_shift, 0]
    geometry2.shift_section()
    geometry2.holes.append([bf + dist / 2, d / 2])
    x_shift = 2 * (bf + dist)
    geometry3 = copy.deepcopy(baseSection.geometry_list[0])
    geometry3.shift = [x_shift, 0]
    geometry3.shift_section()
    geometry3.holes.append([2 * bf + dist, d / 2])
    geometry_list = [baseSection.geometry_list[0], geometry2, geometry3]
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                   xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                   Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1, cw=0, J=0, isDouble=False, isSouble=True, cc=cc,
                   useAs=useAs, ductility=ductility, baseSection=baseSection,
                   composite='notPlate', convert_type=convert_type, geometry_list=geometry_list, is_closed=is_closed)


def AddPlateTB(section, plate):
    '''add plate to Top and Bottom of section, center of palate in x direction
       is equal to center of section.
       bf times to 2 because section equal to I_STEEL_SECTION and b/t in I
       section equal to bf/(2*tf)'''

    _type = section.type
    baseSection = section.baseSection
    name = section.name + 'F' + plate.name
    area = section.area + 2 * plate.area
    xmax = section.xmax
    # if not baseSection.type in ('UNP, UPA'):
    #     xmax = max(xmax, plate.bf)
    # xmax = max(section.xmax, plate.xmax)
    ymax = section.ymax + 2 * plate.ymax
    xm = xmax / 2
    ym = ymax / 2
    ASy = section.ASy
    ASx = section.ASx + 2 * plate.area
    Ix = section.Ix + 2 * (plate.Ix + plate.area * (section.ym + plate.ym) ** 2)
    Iy = section.Iy + 2 * plate.Iy
    Zx = section.Zx + 2 * (plate.area * (section.ym + plate.ym))
    Zy = section.Zy + 2 * plate.Zy
    isDouble = section.isDouble
    isSouble = section.isSouble
    bf = baseSection.bf
    tf = baseSection.tf
    d = baseSection.d
    tw = baseSection.tw
    r1 = baseSection.r1
    useAs = baseSection.useAs
    ductility = baseSection.ductility
    convert_type = section.convert_type
    cc = section.cc
    dp = d + plate.ymax
    cw = section.cw + plate.Iy * (dp ** 2 / 2)
    if _type == 'BOX':
        cw = 0
    # if palate.bf > self.cc - bf:
    is_closed = True
    x = xm - plate.bf / 2
    p3 = (x, section.ymax)
    p4 = (x, -plate.tf)
    geometry1 = RectangularSection(d=plate.tf, b=plate.bf, shift=p3)
    geometry2 = RectangularSection(d=plate.tf, b=plate.bf, shift=p4)
    geometry_list = section.geometry_list + [geometry1, geometry2]
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                   xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy, Zx=Zx, Zy=Zy, bf=bf, tf=tf,
                   d=d, tw=tw, r1=r1, cw=cw, J=0, isDouble=isDouble, isSouble=isSouble, baseSection=baseSection, cc=cc,
                   useAs=useAs, TBPlate=plate, ductility=ductility, composite='TBPlate', convert_type=convert_type, geometry_list=geometry_list, is_closed=is_closed)


def AddPlateLR(section, plate):

    _type = section.type
    baseSection = section.baseSection
    # plate_name = name = 'PL%sX%s' % (plate.ymax, plate.xmax)
    name = section.name + 'LR' + plate.name
    area = section.area + 2 * plate.area
    ymax = max(section.ymax, plate.ymax)
    xmax = section.xmax + 2 * plate.xmax
    xm = xmax / 2
    ym = section.ym
    ASx = section.ASx
    ASy = section.ASy + 2 * plate.area
    Iy = section.Iy + 2 * (plate.Iy + plate.area * (section.xmax / 2 + plate.xm) ** 2)
    Ix = section.Ix + 2 * plate.Ix
    Zy = section.Zy + 2 * (plate.area * (section.xmax / 2 + plate.xm))
    Zx = section.Zx + 2 * plate.Zx
    isDouble = section.isDouble
    isSouble = section.isSouble
    baseSection = section.baseSection
    bf = baseSection.bf
    tf = baseSection.tf
    d = baseSection.d
    tw = baseSection.tw
    r1 = baseSection.r1
    TBPlate = section.TBPlate
    useAs = baseSection.useAs
    ductility = baseSection.ductility
    convert_type = section.convert_type
    cc = section.cc
    dp = section.xmax + plate.xmax
    cw = section.cw + plate.Ix * (dp ** 2 / 2)
    J = 0
    is_closed = section.is_closed
    if not is_closed:
        J = section.J + 2 * plate.J
    if _type == 'BOX':
        cw = 0
        if bool(TBPlate):
            a = TBPlate.bf - plate.bf
            b = plate.tf + TBPlate.tf
            Am = a * b
            p = 2 * (a + b)
            t1 = TBPlate.tf
            t2 = plate.bf
            J = 4 * (Am ** 2) / (2 * a / t1 + 2 * b / t2)
            is_closed = True
    y = baseSection.ym - plate.tf / 2
    p5 = (-plate.bf, y)
    p6 = (section.xmax, y)
    geometry1 = RectangularSection(d=plate.tf, b=plate.bf, shift=p5)
    geometry1.holes.append([bf / 4, d / 2])
    geometry2 = RectangularSection(d=plate.tf, b=plate.bf, shift=p6)
    geometry2.holes.append([p6[0] - bf / 4, d / 2])
    geometry_list = section.geometry_list + [geometry1, geometry2]
    composite = 'TBLRPLATE'
    if not TBPlate:
        composite = 'LRPLATE'
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                   xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy, Zx=Zx, Zy=Zy, bf=bf, tf=tf,
                   d=d, tw=tw, r1=r1, cw=cw, J=J, isDouble=isDouble, isSouble=isSouble, baseSection=baseSection, cc=cc,
                   useAs=useAs, TBPlate=TBPlate, LRPlate=plate,
                   ductility=ductility, composite=composite, convert_type=convert_type,
                   geometry_list=geometry_list, is_closed=is_closed)


def AddPlateWeb(section, plate):

    _type = section.type
    # plate_name = name = 'PL%sX%s' % (plate.ymax, plate.xmax)
    name = section.name + 'W' + plate.name
    area = section.area + 2 * plate.area
    ymax = section.ymax
    xmax = section.xmax
    xm = xmax / 2
    ym = section.ym
    ASx = section.ASx
    ASy = section.ASy + 2 * plate.area
    Iy = section.Iy + 2 * (plate.Iy + plate.area * ((section.cc + section.tw) / 2 + plate.xm) ** 2)
    Ix = section.Ix + 2 * plate.Ix
    Zy = section.Zy + 2 * (plate.area * ((section.cc + section.tw) / 2 + plate.xm))
    Zx = section.Zx + 2 * plate.Zx
    isDouble = section.isDouble
    isSouble = section.isSouble
    baseSection = section.baseSection
    bf = baseSection.bf
    tf = baseSection.tf
    d = baseSection.d
    tw = baseSection.tw
    r1 = baseSection.r1
    TBPlate = section.TBPlate
    LRPlate = section.LRPlate
    useAs = baseSection.useAs
    ductility = baseSection.ductility
    convert_type = section.convert_type
    cc = section.cc
    dp = section.cc + section.tw + plate.xmax
    cw = section.cw + plate.Ix * (dp ** 2 / 2)
    composite = 'TBLRPLATE'
    if not TBPlate:
        composite = 'LRPLATE'
    J = 0
    is_closed = section.is_closed
    if not is_closed:
        J = section.J + 2 * plate.J
    y = baseSection.ym - plate.tf / 2
    p8 = ((bf - tw) / 2 - plate.bf, y)
    multiplier = 0
    if isDouble:
        multiplier = 1
    elif isSouble:
        multiplier = 2
    p9 = (multiplier * section.cc + (bf + tw) / 2, y)
    geometry1 = RectangularSection(d=plate.tf, b=plate.bf, shift=p8)
    geometry2 = RectangularSection(d=plate.tf, b=plate.bf, shift=p9)
    geometry_list = section.geometry_list + [geometry1, geometry2]
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                   xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy, Zx=Zx, Zy=Zy, bf=bf, tf=tf,
                   d=d, tw=tw, r1=r1, cw=cw, J=J, isDouble=isDouble, isSouble=isSouble, baseSection=baseSection, cc=cc,
                   useAs=useAs, TBPlate=TBPlate, LRPlate=LRPlate, webPlate=plate,
                   ductility=ductility, composite=composite, convert_type=convert_type,
                   geometry_list=geometry_list, is_closed=is_closed)


class Ipe(Section):

    def __init__(self, name, area, bf, d, Ix, Iy, Zx, Zy, tf, tw, r1):
        xm = bf / 2
        ym = d / 2
        xmax = bf
        ymax = d
        ASy = (d - tf) * tw
        ASx = 5 / 3 * bf * tf
        df = d - tf
        cw = (tf * bf ** 3 / 12) * (df ** 2 / 2)
        J = (2 * bf * tf ** 3 + (d - 2 * tf) * tw ** 3) / 3
        geometry = ISection(d=d, b=bf, t_f=tf, t_w=tw, r=r1, n_r=4)
        super(Ipe, self).__init__(_type='IPE', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1, cw=cw, J=J,
                                  geometry_list=[geometry])

    @staticmethod
    def createStandardIpes():
        IPE14 = Ipe("IPE14", 1640, 73, 140, 5410000, 449000, 88300, 19200, 6.9, 4.7, 7)
        IPE16 = Ipe("IPE16", 2010, 82, 160, 8690000, 683000, 124000, 26100, 7.4, 5.0, 9)
        IPE18 = Ipe("IPE18", 2390, 91, 180, 13170000, 1010000, 166000, 34600, 8.0, 5.3, 9)
        IPE20 = Ipe("IPE20", 2850, 100, 200, 19400000, 1420000, 221000, 44600, 8.5, 5.6, 12)
        IPE22 = Ipe("IPE22", 3340, 110, 220, 27770000, 2050000, 285000, 58100, 9.2, 5.9, 12)
        IPE24 = Ipe("IPE24", 3910, 120, 240, 38900000, 2840000, 367000, 73900, 9.8, 6.2, 15)
        IPE27 = Ipe("IPE27", 4590, 135, 270, 57900000, 4200000, 484000, 96900, 10.2, 6.6, 15)
        IPE30 = Ipe("IPE30", 5380, 150, 300, 83600000, 6040000, 628000, 125000, 10.7, 7.1, 15)
        IPE = {14: IPE14, 16: IPE16, 18: IPE18, 20: IPE20, 22: IPE22, 24: IPE24, 27: IPE27, 30: IPE30}
        return IPE


class PG(Section):

    def __init__(self, d, tw, bf, tf):

        name = 'PG{}X{}-{}X{}'.format(d, tw, bf, tf)
        webPlate = Plate(tw, d - 2 * tf)
        flangePlate = Plate(bf, tf)
        pg = AddPlateTB(webPlate, flangePlate)
        ASy = (d - tf) * tw
        ASx = 5 / 3 * (bf * tf)

        super(PG, self).__init__(_type='IPE', name=name, area=pg.area, xm=pg.xm, ym=pg.ym,
                                 xmax=pg.xmax, ymax=pg.ymax, ASy=ASy, ASx=ASx, Ix=pg.Ix, Iy=pg.Iy,
                                 Zx=pg.Zx, Zy=pg.Zy, bf=bf, tf=tf, d=d, tw=tw, r1=0, cw=0, J=0)


class Unp(Section):

    def __init__(self, name, area, bf, d, xm, Ix, Iy, Zx, Zy, tf, tw):
        r1 = tf
        ym = d / 2
        xmax = bf
        ymax = d
        ASy = (d - tf) * tw
        ASx = 5 / 3 * bf * tf
        df = d - tf
        cw = (tf * bf ** 3 / 12) * (df ** 2 / 2)
        J = (2 * bf * tf ** 3 + (d - 2 * tf) * tw ** 3) / 3
        geometry = PfcSection(d=d, b=bf, t_f=tf, t_w=tw, r=r1, n_r=4)
        super(Unp, self).__init__(_type='UNP', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1,
                                  cw=cw, J=J, geometry_list=[geometry])

    @staticmethod
    def createStandardUnps():
                    # name, area, bf,   d,    xm,     Ix,      Iy,     Zx,   Zy, tf, tw
        UNP8 = Unp("UNP08", 1102, 45, 80, 14.44, 1058000, 194000, 32810, 13350, 8, 6)
        UNP10 = Unp("UNP10", 1346, 50, 100, 15.45, 2053000, 292900, 50330, 18000, 8.5, 6)
        UNP12 = Unp("UNP12", 1698, 55, 120, 15.98, 3641000, 431400, 74690, 23630, 9, 7)
        UNP14 = Unp("UNP14", 2036, 60, 140, 17.5, 6044000, 626000, 105400, 31430, 10, 7)
        UNP16 = Unp("UNP16", 2402, 65, 160, 18.32, 9246000, 853900, 141100, 39120, 10.5, 7.5)
        UNP18 = Unp("UNP18", 2796, 70, 180, 19.19, 1.353e7, 1137000, 183600, 48040, 11, 8)
        UNP20 = Unp("UNP20", 3219, 75, 200, 20.07, 1.911e7, 1483000, 233500, 58040, 11.5, 8.5)
        UNP22 = Unp("UNP22", 3744, 80, 220, 21.36, 2.691e7, 1966000, 298800, 71870, 12.5, 9)
        UNP24 = Unp("UNP24", 4229, 85, 240, 22.26, 3.597e7, 2479000, 366400, 84830, 13, 9.5)
        UNP26 = Unp("UNP26", 4827, 90, 260, 23.57, 4.821e7, 3178000, 453100, 102500, 14, 10)
        UNP28 = Unp("UNP28", 5340, 95, 280, 25.2, 6.272e7, 3989000, 544500, 122300, 15, 10)
        UNP30 = Unp("UNP30", 5874, 100, 300, 26.87, 8.022e7, 4940000, 646900, 144600, 16, 10)
        UNP = {8: UNP8, 10: UNP10, 12: UNP12, 14: UNP14, 16: UNP16, 18: UNP18,
               20: UNP20, 22: UNP22, 24: UNP24, 26: UNP26, 28: UNP28, 30: UNP30}
        return UNP


class Upa(Section):

    def __init__(self, name, area, bf, d, xm, Ix, Iy, Zx, Zy, tf, tw, r1, J):
        ym = d / 2
        xmax = bf
        ymax = d
        ASy = (d - tf) * tw
        ASx = 5 / 3 * bf * tf
        df = d - tf
        cw = (tf * bf ** 3 / 12) * (df ** 2 / 2)
        geometry = PfcSection(d=d, b=bf, t_f=tf, t_w=tw, r=r1, n_r=4)
        super(Upa, self).__init__(_type='UPA', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1,
                                  geometry_list=[geometry], cw=cw, J=J)

    @staticmethod
    def createStandardUpas():
                    # name, area, bf, d,  xm,     Ix,    Iy,    Zx,   Zy,  tf, tw, r1, J

        UPA8 = Upa("UPA08", 898.0, 40.0, 80.0, 13.1, 894000.0, 128000.0, 22400.0, 4750.0, 7.4, 4.5, 13.9, 13235.9)
        UPA10 = Upa("UPA10", 1090.0, 46.0, 100.0, 14.4, 1740000.0, 204000.0, 34800.0, 6460.0, 7.6, 4.5, 14.6, 16499.4)
        UPA12 = Upa("UPA12", 1330.0, 52.0, 120.0, 15.4, 3040000.0, 312000.0, 50600.0, 8520.0, 7.8, 4.8, 15.3, 20874.8)
        UPA14 = Upa("UPA14", 1560.0, 58.0, 140.0, 16.7, 4910000.0, 454000.0, 70200.0, 11000.0, 8.1, 4.9, 16.1, 26039)
        UPA16 = Upa("UPA16", 1810.0, 64.0, 160.0, 18.0, 7470000.0, 633000.0, 93400.0, 13800.0, 8.4, 5.0, 16.9, 31955.3)
        UPA18 = Upa("UPA18", 2070.0, 70.0, 180.0, 19.4, 10900000.0, 860000.0, 121000.0, 17000.0, 8.7, 5.1, 17.7, 38689.2)
        UPA20 = Upa("UPA20", 2340.0, 76.0, 200.0, 20.7, 15200000.0, 1130000.0, 152000.0, 20500.0, 9.0, 5.2, 18.5, 46309.8)
        UPA22 = Upa("UPA22", 2670.0, 82.0, 220.0, 22.10, 21100000.0, 1510000.0, 192000.0, 25100.0, 9.5, 5.4, 19.5, 58417.2)
        UPA24 = Upa("UPA24", 3060.0, 90.0, 240.0, 24.2, 29000000.0, 2080000.0, 242000.0, 31600.0, 10.0, 5.6, 20.5, 74049.2)
        UPA27 = Upa("UPA27", 3520.0, 95.0, 270.0, 24.7, 41600000.0, 2620000.0, 308000.0, 37300.0, 10.5, 6.0, 21.5, 92756.2)
        UPA30 = Upa("UPA30", 4050.0, 100.0, 300.0, 25.2, 58100000.0, 3270000.0, 387000.0, 43600.0, 11.0, 6.5, 23, 116195.8)

        UPA = {
            8: UPA8,
            10: UPA10,
            12: UPA12,
            14: UPA14,
            16: UPA16,
            18: UPA18,
            20: UPA20,
            22: UPA22,
            24: UPA24,
            27: UPA27,
            30: UPA30,
        }
        return UPA


class Cpe(Section):

    def __init__(self, name, area, bf, d, Ix, Iy, Zx, Zy, tf, tw, r1):
        xm = bf / 2
        ym = d / 2
        xmax = bf
        ymax = d
        ASy = (d / 1.5 - tf) * tw
        ASx = 5 / 3 * bf * tf
        df = d - tf
        cw = (tf * bf ** 3 / 12) * (df ** 2 / 2)
        geometry = ISection(d=d, b=bf, t_f=tf, t_w=tw, r=r1, n_r=4)
        super(Cpe, self).__init__(_type='CPE', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1,
                                  geometry_list=[geometry], cw=cw, J=0)

    @staticmethod
    def createStandardCpes():
        CPE14 = Cpe("CPE14", 1310, 73, 210, 12700000, 449000, 121000, 19200, 6.9, 4.7, 7)
        CPE16 = Cpe("CPE16", 1610, 82, 240, 20300000, 683000, 169000, 26100, 7.4, 5.0, 9)
        CPE18 = Cpe("CPE18", 1910, 91, 270, 30700000, 1010000, 228000, 34600, 8.0, 5.3, 9)
        CPE20 = Cpe("CPE20", 2290, 100, 300, 45400000, 1420000, 302000, 44600, 8.5, 5.6, 12)
        CPE22 = Cpe("CPE22", 2690, 110, 330, 64600000, 2050000, 392000, 58100, 9.2, 5.9, 12)
        CPE24 = Cpe("CPE24", 3170, 120, 360, 90700000, 2840000, 504000, 73900, 9.8, 6.2, 15)
        CPE27 = Cpe("CPE27", 3700, 135, 405, 134700000, 4200000, 665000, 96900, 10.2, 6.6, 15)
        CPE30 = Cpe("CPE30", 4320, 150, 450, 194100000, 6040000, 863000, 125000, 10.7, 7.1, 15)
        CPE = {14: CPE14, 16: CPE16, 18: CPE18, 20: CPE20, 22: CPE22, 24: CPE24, 27: CPE27, 30: CPE30}
        return CPE


class Plate(Section):

    def __init__(self, xmax, ymax):
        area = xmax * ymax
        if xmax > ymax:
            name = f'{xmax/10:.0f}X{ymax}'
            j = xmax * ymax ** 3 / 3
            ASy = 0
            ASx = area
        else:
            name = f'{ymax/10:.0f}X{xmax}'
            j = ymax * xmax ** 3 / 3
            ASy = area
            ASx = 0
        xm = xmax / 2
        ym = ymax / 2
        Ix = xmax * ymax ** 3 / 12
        Iy = ymax * xmax ** 3 / 12
        Zx = xmax * ymax ** 2 / 4
        Zy = ymax * xmax ** 2 / 4
        bf = xmax
        tf = ymax
        self.cc = 0
        super(Plate, self).__init__(_type='PLATE', name=name, area=area, xm=xm, ym=ym,
                                    xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                    Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=0, tw=0, r1=0, cw=0, J=j)


class Box(Section):

    def __init__(self, xmax, ymax, mode=1):
        name = "Box{}".format(mode)
        xm = xmax / 2
        ym = ymax / 2
        super(Box, self).__init__(_type='BOX', name=name, area=0.0001, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=0, ASx=0, Ix=0, Iy=0,
                                  Zx=0, Zy=0, bf=xmax, tf=1, d=ymax, tw=1, r1=0, cw=0, J=0)

    @staticmethod
    def createStandardBox():
        BOX1 = Box(400, 400, mode=1)
        BOX2 = Box(300, 300, mode=2)
        BOX = {1: BOX1, 2: BOX2}
        return BOX


def createSection(sectionProp):
    ipesProp = Ipe.createStandardIpes()
    unpsProp = Unp.createStandardUnps()
    upasProp = Upa.createStandardUpas()
    cpesProp = Cpe.createStandardCpes()
    boxProp = Box.createStandardBox()
    sectionProperties = {
        'IPE': ipesProp,
        'UNP': unpsProp,
        'CPE': cpesProp,
        'BOX': boxProp,
        'UPA': upasProp,
    }
    sectionType = sectionProp[SECTIONTYPE]
    sectionSize = sectionProp[SECTIONSIZE]
    section = sectionProperties[sectionType][sectionSize]
    isTBPlate = sectionProp[ISTBPLATE]
    isLRPlate = sectionProp[ISLRPLATE]
    isWebPlate = sectionProp[ISWEBPLATE]
    if sectionType == 'BOX':
        if (isTBPlate and isLRPlate):
            xmax, ymax = sectionProp[LH], sectionProp[LV]
            if sectionSize == 2:
                xmax = sectionProp[LH] - 2 * sectionProp[TV]
            section = Box(xmax, ymax, mode=sectionSize)

    section.convert_type = sectionProp[CONVERT_TYPE]
    useAs = sectionProp[USEAS]
    ductility = sectionProp[DUCTILITY]
    section.useAs = useAs
    section.ductility = ductility
    isDouble = sectionProp[ISDOUBLE]
    isSouble = sectionProp[ISSOUBLE]
    is_cc = sectionProp[ISCC]
    if not is_cc:
        dist = sectionProp[DIST]
    else:
        dist = sectionProp[DIST] - 2 * (section.bf - section.xm)
        if all([dist < 0, (isDouble or isSouble)]):
            print("distance between section is Negative!")
            return None

    if isDouble:
        section = DoubleSection(section, dist)
    if isSouble:
        section = SoubleSection(section, dist)
    if isTBPlate:
        p1 = Plate(sectionProp[LH], sectionProp[TH])
        section = AddPlateTB(section, p1)
    if isLRPlate:
        p2 = Plate(sectionProp[TV], sectionProp[LV])
        section = AddPlateLR(section, p2)
    if isWebPlate:
        p3 = Plate(sectionProp[_TW], sectionProp[LW])
        section = AddPlateWeb(section, p3)
    for use_as in ('B', 'C'):
        for ductil in ('M', 'H'):
            name = '{}{}{}'.format(section.name, use_as, ductil)
            section.conversions[name] = section.equivalentSectionI(
                useAs=use_as, ductility=ductil)
    # shear section
    name = f'{section.name}_S'
    section.conversions[name] = section.equivalent_section_to_I_with_shear_correction()
    section.shear_name = name

    # if use_as == useAs and ductil == ductility:

    if isSouble or isDouble or isTBPlate or isLRPlate or isWebPlate:
        # section.equivalentSectionI()
        section.name = '{}{}{}'.format(section.name, useAs, ductility)

    section.prop = sectionProp

    return section


class SectionProperties:
    sectionType = {'IPE': 'STEEL_I_SECTION',
                   'UNP': 'STEEL_I_SECTION',
                   'CPE': 'STEEL_I_SECTION',
                   'BOX': 'STEEL_I_SECTION',
                   'UPA': 'STEEL_I_SECTION',
                   }

    def __init__(self, section, name):
        self.type = section.type
        self.name = name
        self.area = section.area
        self.ASx = section.ASx
        self.ASy = section.ASy
        self.Ix = section.Ix
        self.Iy = section.Iy
        self.Zx = section.Zx
        self.Zy = section.Zy
        self.cw = section.cw
        self.J = section.J
        self.xm = section.xm
        self.ym = section.ym
        self.Rx = section.Rx
        self.Ry = section.Ry
        self.Sx = section.Sx
        self.Sy = section.Sy
        self.xmax = section.xmax
        self.ymax = section.ymax
        self.useAs = section.useAs
        self.ductility = section.ductility
        self.shear_name = section.shear_name
        self.baseSection_name = section.baseSection.name
        self.conversions = section.conversions
        self.equivalent_dims()
        self.autocadScrText = section.autocadScrText
        self.geometry_list = section.geometry_list
        self.uid = section.uid

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def equivalent_dims(self):
        self.bf_equivalentI, self.tf_equivalentI, self.d_equivalentI, self.tw_equivalentI = self.conversions[self.name]
        self.xml = self.__str__()

    def __str__(self):
        secType = self.sectionType[str(self.type)]
        s = ('\n\n  <{}>\n'
             '\t<LABEL>{}</LABEL>\n'
             '\t<EDI_STD>{}</EDI_STD>\n'
             '\t<DESIGNATION>G</DESIGNATION>\n'
             '\t<D>{}</D>\n'
             '\t<BF>{}</BF>\n'
             '\t<TF>{}</TF>\n'
             '\t<TW>{}</TW>\n'
             '\t<FRAD>0</FRAD>\n'
             '\t<A>{:.0f}</A>\n'
             '\t<AS2>{:.0f}</AS2>\n'
             '\t<AS3>{:.0f}</AS3>\n'
             '\t<I33>{:.0f}</I33>\n'
             '\t<I22>{:.0f}</I22>\n'
             '\t<S33POS>{:.0f}</S33POS>\n'
             '\t<S33NEG>{:.0f}</S33NEG>\n'
             '\t<S22POS>{:.0f}</S22POS>\n'
             '\t<S22NEG>{:.0f}</S22NEG>\n'
             '\t<R33>{:.1f}</R33>\n'
             '\t<R22>{:.1f}</R22>\n'
             '\t<Z33>{:.0f}</Z33>\n'
             '\t<Z22>{:.0f}</Z22>\n'
             '\t<J>{:.0f}</J>\n'
             '\t<CW>{:.0f}</CW>\n'
             '  </{}>'
             ).format(secType, self.name, self.name, self.d_equivalentI, self.bf_equivalentI, self.tf_equivalentI,
                      self.tw_equivalentI, self.area, self.ASy, self.ASx, self.Ix, self.Iy,
                      self.Sx, self.Sx, self.Sy, self.Sy, self.Rx,
                      self.Ry, self.Zx, self.Zy, self.J, self.cw, secType)
        return s
    @staticmethod
    def exportXml(fname, sections):
        Section.exportXml(fname, sections)


class SectionTableModel(QAbstractTableModel):

    def __init__(self, filename=''):
        super(SectionTableModel, self).__init__()
        self.filename = filename
        self.dirty = False
        self.sections = []
        self.names = set()

    def sortByName(self):
        self.beginResetModel()
        self.sections = sorted(self.sections)
        self.endResetModel()

    def sortByArea(self):
        def compare(a, b):
            if a.area > b.area:
                return 1
            else:
                return -1
        self.sections = sorted(self.sections, key=compare)
        self.reset()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) |
            Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
                not (0 <= index.row() < len(self.sections))):
            return
        section = self.sections[index.row()]
        baseSection_name = section.baseSection_name
        column = index.column()
        if role == Qt.DisplayRole:
            if column == NAME:
                return section.name
            elif column == AREA:
                return '{0:.1f}'.format(section.area / 100.)
            elif column == ASY:
                return '{0:.1f}'.format(section.ASy / 100.)
            elif column == ASX:
                return '{0:.1f}'.format(section.ASx / 100.)
            elif column == IX:
                return '{0:.1f}'.format(section.Ix / 10000.)
            elif column == IY:
                return '{0:.1f}'.format(section.Iy / 10000.)
            elif column == ZX:
                return '{0:.1f}'.format(section.Zx / 1000.)
            elif column == ZY:
                return '{0:.1f}'.format(section.Zy / 1000.)
            elif column == BF:
                return '{0:.1f}'.format(section.bf_equivalentI / 10.)
            elif column == TF:
                return '{0:.1f}'.format(section.tf_equivalentI / 10.)
            elif column == D:
                return '{0:.1f}'.format(section.d_equivalentI / 10.)
            elif column == TW:
                return '{0:.1f}'.format(section.tw_equivalentI / 10.)
            elif column == Sx:
                return '{0:.1f}'.format(section.Sx / 1000.)
            elif column == Sy:
                return '{0:.1f}'.format(section.Sy / 1000.)
            elif column == RX:
                return '{0:.1f}'.format(section.Rx / 10.)
            elif column == RY:
                return '{0:.1f}'.format(section.Ry / 10.)
            elif column == CW:
                return '{0:.0f}'.format(section.cw / 1e6)
            elif column == J:
                return '{0:.0f}'.format(section.J / 10000)
            # elif column == SLENDER:
                # return '{0:.1f}'.format(section.slender))
            # elif column == V2:
            #     return '{0:.1f}'.format(section.V2)
            # elif column == V3:
            #     return '{0:.1f}'.format(section.V3)
            # elif column == XM:
            #     return '{0:.1f}'.format(section.xm / 10.)
            # elif column == YM:
            #     return '{0:.1f}'.format(section.ym / 10.)

        elif role == Qt.TextAlignmentRole:
            if column == NAME:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignCenter | Qt.AlignVCenter)
        elif role == Qt.BackgroundColorRole:
            # if column == SLENDER:
            #     if section.slender == u'لاغر':
            #         return QColor(250, 40, 0)
            #     else:
            #         return QColor(100, 250, 0)
            if '14' in baseSection_name:
                return QColor(150, 200, 150)
            elif '16' in baseSection_name:
                return QColor(150, 200, 250)
            elif '18' in baseSection_name:
                return QColor(250, 200, 250)
            elif '20' in baseSection_name:
                return QColor(250, 250, 130)
            elif '22' in baseSection_name:
                return QColor(10, 250, 250)
            elif '24' in baseSection_name:
                return QColor(210, 230, 230)
            elif '27' in baseSection_name:
                return QColor(110, 230, 230)
            elif '30' in baseSection_name:
                return QColor(210, 130, 230)
            else:
                return QColor(150, 150, 250)
        # elif role == Qt.TextColorRole:
            # if column == SLENDER:
            # return Qt.red)

        return

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            if section == NAME:
                return "Name"
            elif section == AREA:
                return "A (cm2)"
            elif section == ASY:
                return "ASy (cm2)"
            elif section == ASX:
                return "ASx (cm2)"
            elif section == IX:
                return "Ix (cm4)"
            elif section == IY:
                return "Iy (cm4)"
            elif section == ZX:
                return "Zx (cm3)"
            elif section == ZY:
                return "Zy (cm3)"
            elif section == BF:
                return "bf (cm)"
            elif section == TF:
                return "tf (cm)"
            elif section == D:
                return "d (cm)"
            elif section == TW:
                return "tw (cm)"
            elif section == Sx:
                return "Sx (cm3)"
            elif section == Sy:
                return "Sy (cm3)"
            elif section == RX:
                return "rx (cm)"
            elif section == RY:
                return "ry (cm)"
            elif section == CW:
                return "cw (cm6)"
            elif section == J:
                return "J (cm4)"
            # elif section == SLENDER:
            #     return "Slender"
            # elif section == V2:
            #     return "V2 coef."
            # elif section == V3:
            #     return "V3 coef."
            # elif section == XM:
            #     return "xm (cm)"
            # elif section == YM:
            #     return "ym (cm)"

        return int(section + 1)

    def rowCount(self, index=QModelIndex()):
        return len(self.sections)

    def columnCount(self, index=QModelIndex()):
        return column_count

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.sections):
            section = self.sections[index.row()]
            column = index.column()
            if column == NAME:
                if all([value != '', value not in self.names]):
                    section.name = value
                    self.names.add(value)
            try:
                value = float(value)
                if value > 0:
                    if column == AREA:
                        section.area = value * 100
                    elif column == ASX:
                        section.ASx = value * 100
                    elif column == ASY:
                        section.ASy = value * 100
                    elif column == IX:
                        section.Ix = value * 10000
                    elif column == IY:
                        section.Iy = value * 10000
                    elif column == ZX:
                        section.Zx = value * 1000
                    elif column == ZY:
                        section.Zy = value * 1000
                    elif column == BF:
                        section.bf_equivalentI = value * 10
                    elif column == TF:
                        section.tf_equivalentI = value * 10
                    elif column == D:
                        section.d_equivalentI = value * 10
                    elif column == TW:
                        section.tw_equivalentI = value * 10
                    elif column == CW:
                        section.cw = value * 1e6
                    elif column == J:
                        section.J = value * 10000
                    # elif column == XM:
                    #     section.xm = value
                    # elif column == YM:
                    #     section.ym = value

                    section.Rx = sqrt(section.Ix / section.area)
                    section.Ry = sqrt(section.Iy / section.area)
                    section.Sx = section.Ix / section.ym
                    section.Sy = section.Iy / (section.xmax - section.xm)
            except ValueError:
                pass
            section.xml = section.__str__()
            self.dirty = True
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.sections.insert(position + row,
                                 Ipe("IPE18", 2390, 91, 180, 13170000, 1010000, 166000, 34600, 8.0, 5.3, 9))
        self.endInsertRows()
        self.dirty = True
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.sections = (self.sections[:position] +
                         self.sections[position + rows:])
        self.endRemoveRows()
        self.dirty = True
        return True

    # def moveRows(self, parent, source_first, source_last, parent2, dest):
    #     self.beginMoveRows(parent, source_first, source_last, parent2, dest)

    #     sections = self.sections
    #     if source_first <= dest:
    #         new_order = sections[:source_first] + sections[source_last + 1:dest + 1] + sections[source_first:source_last + 1] + sections[dest + 1:]
    #     else:  # TODO what if source_first < dest < source_last
    #         new_order = sections[:dest] + sections[source_first:source_last + 1] + sections[dest:source_first] + sections[source_last + 1:]
    #     # self.alignment.set_sequences(new_order, notify=True)
    #     self.sections = new_order
    #     print("BEFORE endMoveRows in edit_sequence_list.Model, %s" % self)
    #     self.endMoveRows()


class SectionDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(SectionDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() == NAME:
            editor = QLineEdit(parent)
            editor.returnPressed.connect(self.commitAndCloseEditor)
            return editor
        else:
            # spinbox = QDoubleSpinBox(parent)
            # return spinbox
            return QItemDelegate.createEditor(self, parent, option,
                                              index)

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)
        if index.column() == NAME:
            editor.setText(text)

        else:
            # editor.setValue(float(text))
            QItemDelegate.setEditorData(self, editor, index)

    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, (QTextEdit, QLineEdit)):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)


if __name__ == '__main__':
    IPE = Ipe.createStandardIpes()
    __ductility = 'M'
    __useAs = 'C'
    IPE22 = IPE[22]
    IPE22.ductility = __ductility
    IPE22.useAs = __useAs
    IPE22_double = DoubleSection(IPE22, 0)
    geometry = MergedSection(IPE22_double.geometry_list)
    # geometry.plot_geometry()
    geometry.holes.append([110, 110])
    # # geometry.clean_geometry(verbose=True)
    n = len(IPE22_double.geometry_list)
    mesh = geometry.create_mesh(mesh_sizes=n * [2.5])
    # warping_section = CrossSection(geometry, mesh)
    # warping_section.plot_mesh()
