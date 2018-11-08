# -*- coding: utf-8 -*-

from __future__ import division
from math import sqrt
from PySide2.QtCore import *
from PySide2.QtGui import *
# from PyQt5.QtXml import *
import re

NAME, AREA, ASX, ASY, IX, IY, ZX, ZY, \
Sx, Sy, RX, RY, BF, TF, D, TW, XM, YM, V2, V3, SLENDER = range(21)

LH, TH, LV, TV, LW, _TW, DIST, ISTBPLATE, ISLRPLATE, ISWEBPLATE, USEAS, DUCTILITY, ISDOUBLE, \
ISSOUBLE, SECTIONSIZE, SECTIONTYPE, CONVERT_TYPE = range(17)

#ipesProp = Ipe.createStandardIpes()
#unpsProp = Unp.createStandardUnps()
#sectionProperties = {'IPE': ipesProp, 'UNP': unpsProp}

MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1


class Section(object):
    sectionType = {'IPE': 'STEEL_I_SECTION',
                   'UNP': 'STEEL_I_SECTION',
                   'CPE': 'STEEL_I_SECTION'}

    def __init__(self, cc=0, composite=None, useAs='B', ductility='M',
                TBPlate=None, LRPlate=None, webPlate=None, slender=None, isDouble=False,
                isSouble=False, convert_type='slender', **kwargs):
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

        if convert_type == 'shear':
            self.bf_equivalentI, self.tf_equivalentI, self.d_equivalentI, self.tw_equivalentI = \
            self.equivalent_section_to_I_with_shear_correction()

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
               '\t<J>0</J>\n'
               '  </{}>'
              ).format(secType, self.name, self.name, self.d_equivalentI, self.bf_equivalentI, self.tf_equivalentI,
                                       self.tw_equivalentI, self.area, self.ASy, self.ASx, self.Ix, self.Iy,
                                       self.Sx, self.Sx, self.Sy, self.Sy, self.Rx,
                                       self.Ry, self.Zx, self.Zy, secType)
        return s

    @staticmethod
    def exportXml(fname, sections):
        #error = None
        #fh = None
        #try:
        fh = open(fname, 'w')
        #if not fh.open(QIODevice.WriteOnly):
            #raise IOError, unicode(fh.errorString())
        #stream.setCodec(CODEC)
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n'
        '<PROPERTY_FILE xmlns="http://www.csiberkeley.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.csiberkeley.com CSIExtendedSectionPropertyFile.xsd">\n'
        '   <EbrahimRaeyat_Presents>\n'
        '      <Comment_on_CopyRight> This database is provided by: EbrahimRaeyat, (2017); http://www.ebrahimraeyat.blog.ir </Comment_on_CopyRight>\n'
        '   </EbrahimRaeyat_Presents>\n'
        '  <CONTROL>\n'
        '      <FILE_ID>CSI Frame Properties</FILE_ID>\n'
        '      <VERSION>1</VERSION>\n'
        '      <LENGTH_UNITS>mm</LENGTH_UNITS>\n'
        '      <FORCE_UNITS>kgf</FORCE_UNITS>\n'
        '  </CONTROL>\n\n')
        for section in sections:
            fh.write(section.__str__())
        fh.write('\n</PROPERTY_FILE>')
        return True, "Exported section properties to "    # "%s" % (QFileInfo(fname).fileName())


    @staticmethod
    def export_to_autocad(fname, sections):
        fh = open(fname, 'w')
        #if not fh.open(QIODevice.WriteOnly):
            #raise IOError, unicode(fh.errorString())
        #stream = QTextStream(fh)
        for section in sections:
            try:
                fh.write(section.autocadScrText)
            except AttributeError:
                pass
        return True, "Exported section properties to %s" % (QFileInfo(fname).fileName())

    def equivalentSectionI(self):

        if not self.composite:
            return self.bf, self.tf, self.d, self.tw

        if self.isSouble:
            return 3 * self.bf, 3 * self.tf, self.d, self.tw

        slenderParameters = {'notPlate': {'B': {'M': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                        'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                        'H': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('2*0.55*tf/.6', ''), 'D': 'd',
                        'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}},
                                    'C': {'M': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                                    'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                                    'H': {'BF': '2*bf', 'tfCriteria': 'True', 'TF': ('BF*tf/bf', ''), 'D': 'd',
                                    'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}}},
                        'TBPlate': {'B': {'M': {'BF': 'c+2*xm', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                        'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                        'H': {'BF': 'c+2*xm', 'tfCriteria': 't1<(.6*B1*tf)/(0.55*bf)',
                            'TF': ('(0.55*BF*t1)/(.60*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                            'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}},
                        'C': {'M': {'BF': 'c+2*xm', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                        'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')},
                            'H': {'BF': 'c+2*xm', 'tfCriteria': 't1<(B1*tf)/(bf)',
                                'TF': ('(BF*t1)/(B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                                'twCriteria': 'True', 'TW': ('(D-2*TF)/(d-2*(tf+r))*tw', '')}}},
                        'LRPlate': {'B': {'M': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                        'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')},
                        'H': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(.6*B1*tf)/(0.55*bf)',
                        'TF': ('(0.55*BF*t1)/(.60*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}},
                        'C': {'M': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                        'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')},
                        'H': {'BF': 'c+2*xm+2*t2', 'tfCriteria': 't1<(B1*tf)/(bf)',
                        'TF': ('(BF*t1)/(B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2*(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}}}}

        composite = str(self.composite)
        useAs = str(self.useAs)
        ductility = str(self.ductility)
        xm = self.baseSection.xm
        bf = self.baseSection.bf
        tf = self.baseSection.tf
        d = self.baseSection.d
        tw = self.baseSection.tw
        r = self.baseSection.r1
        if self.cc:
            c = self.cc
        else:
            c = 0
        try:
            B1 = self.TBPlate.bf
            t1 = self.TBPlate.tf
        except:
            pass

        try:
            B2 = self.LRPlate.tf
            t2 = self.LRPlate.bf
        except:
            pass

        try:
            B2 = self.webPlate.tf
            t2 = self.webPlate.bf
        except:
            pass

        parameters = slenderParameters[composite][useAs][ductility]
        #BF = eval(parameters['BF'])
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

        #if self.baseSection.type == 'UNP':
            #TF = .5 * TF

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

        #self.equalSlendersParamsEtabs()

        return V2, V3


        if self.isEquivalenIpeSlender():
            self.slender = u'لاغر'
        else:
            self.slender = u'غیرلاغر'



#def equalSlendersParams(BF, TF, D, TW):
    #'''Return BF, TF, D, TW for equivalent I section to
    #correct calculation of AS2 and AS3 that etabs calculate
    #automatically and change user input for this parameters.'''
    #ASx = self.ASx
    #ASy = self.ASy

    #FS = BF / (2 * TF)
    #TF = sqrt((.6 * ASx) / FS)
    #BF = FS * TF
    #WS = (D - 2 * TF) / TW
    #delta = TF ** 2 + 4 * (ASy * WS)
    #D = (3 * TF + sqrt(delta)) / 2
    #TW = (D - 2 * TF) / WS

    #return BF, TF, D, TW

    #def equalSlendersParamsEtabs(self):
        #'''Return BF, TF, D, TW for equivalent I section to
        #correct calculation of AS2 and AS3 that etabs calculate
        #automatically and change user input for this parameters.
        #FS = flange slender
        #WS = web slender'''

        #FS = self.bf / (2 * self.tf)
        #WS = (self.d - 2 * self.tf) / self.tw
        #TF = sqrt((.25 * self.ASx) / FS)
        #BF = 2 * FS * TF
        #D = TF + sqrt(TF ** 2 + WS * self.ASy)
        #TW = (D - 2 * TF) / WS

        #self.bf = BF
        #self.tf = TF
        #self.d = D
        #self.tw = TW

    def isEquivalenIpeSlender(self):
        '''This function gives a equivalent ipe section and
            check it's slender'''

        slenderParameters = {'flang':{'B': {'O': 0.76, 'M': 0.76, 'H': 0.60}, 'C': {'O': 1.28, 'M': 0.76, 'H': 0.60}},
                             'web': {'B': {'O':3.76, 'M': 3.76, 'H': 2.45}, 'C': {'O': 1.49, 'M': 1.12, 'H': 0.77}}}

        E = 2e6
        Fy = 2400
        w = sqrt(E / Fy)
        useAs = str(self.useAs)
        ductility = str(self.ductility)
        FS = slenderParameters['flang'][useAs][ductility] * w
        WS = slenderParameters['web'][useAs][ductility] * w

        fs = self.bf_equivalentI / self.tf_equivalentI
        ws = (self.d_equivalentI - 2 * self.tf_equivalentI) / self.tw_equivalentI

        #print 'FS = {}, WS = {}\nfs = {}, ws = {}'.format(FS, WS, fs, ws)

        if fs > FS or ws > WS:
            return  True
        else:
            return False


def DoubleSection(section, dist=0):

    '''dist = distance between two sections, 0 mean that there is no
    distance between sections'''
    _type = section.type
    dist *= 10
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
    if dist == 0:
        name = '2' + section.name
    else:
        name = '2' + section.name + 'c{:.0f}'.format(cc / 10)
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                         xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                         Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1, isDouble=True, cc=cc,
                         useAs=useAs, ductility=ductility, baseSection=baseSection,
                         composite='notPlate', convert_type=convert_type)


def SoubleSection(section, dist=0):

    '''dist = distance between two sections, 0 mean that there is no
    distance between sections'''
    _type = section.type
    dist *= 10
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
    if dist == 0:
        name = '3' + section.name
    else:
        name = '3' + section.name + 'c{:.0f}'.format(cc / 10)
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                         xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                         Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1, isDouble=False, isSouble=True, cc=cc,
                         useAs=useAs, ductility=ductility, baseSection=baseSection,
                         composite='notPlate', convert_type=convert_type)

def AddPlateTB(section, plate):
    '''add plate to Top and Botton of section, center of palate in x direction
       is equal to center of section.
       bf times to 2 beacuse section equal to I_STEEL_SECTION and b/t in I
       section equal to bf/(2*tf)'''

    _type = section.type
    name = section.name + 'TB' + plate.name
    area = section.area + 2 * plate.area
    xmax = section.xmax
    #xmax = max(section.xmax, plate.xmax)
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
    baseSection = section.baseSection
    bf = baseSection.bf
    tf = baseSection.tf
    d = baseSection.d
    tw = baseSection.tw
    r1 = baseSection.r1
    useAs = baseSection.useAs
    ductility = baseSection.ductility
    convert_type = section.convert_type
    cc = section.cc
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
        xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy, Zx=Zx, Zy=Zy, bf=bf, tf=tf,
        d=d, tw=tw, r1=r1, isDouble=isDouble, isSouble=isSouble, baseSection=baseSection, cc=cc,
        useAs=useAs, TBPlate=plate, ductility=ductility, composite='TBPlate', convert_type=convert_type)


def AddPlateLR(section, plate):

    _type = section.type
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
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
        xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy, Zx=Zx, Zy=Zy, bf=bf, tf=tf,
        d=d, tw=tw, r1=r1, isDouble=isDouble, isSouble=isSouble, baseSection=baseSection, cc=cc,
        useAs=useAs, TBPlate=TBPlate, LRPlate=plate,
        ductility=ductility, composite='LRPlate', convert_type=convert_type)


def AddPlateWeb(section, plate):

    _type = section.type
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
    return Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
        xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy, Zx=Zx, Zy=Zy, bf=bf, tf=tf,
        d=d, tw=tw, r1=r1, isDouble=isDouble, isSouble=isSouble, baseSection=baseSection, cc=cc,
        useAs=useAs, TBPlate=TBPlate, LRPlate=LRPlate, webPlate=plate,
        ductility=ductility, composite='LRPlate', convert_type=convert_type)

#class AddPlateTBThick(AddPlateTB):

    #def __init__(self, section, thick):
        #plateWidth = section.xmax - 40
        #plate = Plate(plateWidth, thick)
        #super(AddPlateTBThick, self).__init__(section, plate)


class Ipe(Section):

    def __init__(self, name, area, bf, d, Ix, Iy, Zx, Zy, tf, tw, r1):
        xm = bf / 2
        ym = d / 2
        xmax = bf
        ymax = d
        ASy = (d - tf) * tw
        ASx = 5 / 3 * bf * tf
        super(Ipe, self).__init__(_type='IPE', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1)

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
                                  Zx=pg.Zx, Zy=pg.Zy, bf=bf, tf=tf, d=d, tw=tw, r1=0)



class Unp(Section):

    def __init__(self, name, area, bf, d, xm, Ix, Iy, Zx, Zy, tf, tw):
        r1 = tf
        ym = d / 2
        xmax = bf
        ymax = d
        ASy = (d - tf) * tw
        ASx = 5 / 3 * bf * tf

        super(Unp, self).__init__(_type='UNP', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1)

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

class Cpe(Section):

    def __init__(self, name, area, bf, d, Ix, Iy, Zx, Zy, tf, tw, r1):
        xm = bf / 2
        ym = d / 2
        xmax = bf
        ymax = d
        ASy = (d / 1.5 - tf) * tw
        ASx = 5 / 3 * bf * tf
        super(Cpe, self).__init__(_type='CPE', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=d, tw=tw, r1=r1)

    @staticmethod
    def createStandardCpes():
        CPE14 = Cpe("CPE14", 1640, 73, 210, 12700000, 449000, 121000, 19200, 6.9, 4.7, 7)
        CPE16 = Cpe("CPE16", 2010, 82, 240, 20300000, 683000, 169000, 26100, 7.4, 5.0, 9)
        CPE18 = Cpe("CPE18", 2390, 91, 270, 30700000, 1010000, 228000, 34600, 8.0, 5.3, 9)
        CPE20 = Cpe("CPE20", 2850, 100, 300, 45400000, 1420000, 302000, 44600, 8.5, 5.6, 12)
        CPE22 = Cpe("CPE22", 3340, 110, 330, 64600000, 2050000, 392000, 58100, 9.2, 5.9, 12)
        CPE24 = Cpe("CPE24", 3910, 120, 360, 90700000, 2840000, 504000, 73900, 9.8, 6.2, 15)
        CPE27 = Cpe("CPE27", 4590, 135, 405, 134700000, 4200000, 665000, 96900, 10.2, 6.6, 15)
        CPE30 = Cpe("CPE30", 5380, 150, 450, 194100000, 6040000, 863000, 125000, 10.7, 7.1, 15)
        CPE = {14: CPE14, 16: CPE16, 18: CPE18, 20: CPE20, 22: CPE22, 24: CPE24, 27: CPE27, 30: CPE30}
        return CPE

    #def double(self, dist=0):
        #return DoubleSection(self, dist)

    #def addPlateTB(self, plate):
        #return AddPlateTB(self, plate)


class Plate(Section):

    def __init__(self, xmax, ymax):
        name = 'PL%sX%s' % (xmax, ymax)
        area = xmax * ymax
        xm = xmax / 2
        ym = ymax / 2
        ASy = 0
        ASx = area
        Ix = xmax * ymax ** 3 / 12
        Iy = ymax * xmax ** 3 / 12
        Zx = xmax * ymax ** 2 / 4
        Zy = ymax * xmax ** 2 / 4
        bf = xmax
        tf = ymax
        self.cc = 0
        super(Plate, self).__init__(_type='PLATE', name=name, area=area, xm=xm, ym=ym,
            xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
            Zx=Zx, Zy=Zy, bf=bf, tf=tf, d=0, tw=0, r1=0)


def createSection(sectionProp):
    ipesProp = Ipe.createStandardIpes()
    unpsProp = Unp.createStandardUnps()
    cpesProp = Cpe.createStandardCpes()
    sectionProperties = {'IPE': ipesProp, 'UNP': unpsProp, 'CPE': cpesProp}
    sectionType = sectionProp[SECTIONTYPE]
    sectionSize = sectionProp[SECTIONSIZE]
    section = sectionProperties[sectionType][sectionSize]
    #convert_type = sectionProp[CONVERT_TYPE]
    section.convert_type = sectionProp[CONVERT_TYPE]
    useAs = sectionProp[USEAS]
    ductility = sectionProp[DUCTILITY]
    section.useAs = useAs
    section.ductility = ductility
    dist = sectionProp[DIST]
    isDouble = sectionProp[ISDOUBLE]
    isSouble = sectionProp[ISSOUBLE]
    isTBPlate = sectionProp[ISTBPLATE]
    isLRPlate = sectionProp[ISLRPLATE]
    isWebPlate = sectionProp[ISWEBPLATE]
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
    if isSouble or isDouble or isTBPlate or isLRPlate or isWebPlate:
        #section.equivalentSectionI()
        section.name = '{}{}{}'.format(section.name, useAs, ductility)

    return section


class SectionTableModel(QAbstractTableModel):

    def __init__(self, filename=''):
        super(SectionTableModel, self).__init__()
        self.filename = filename
        self.dirty = False
        self.sections = []
        self.names = set()

    def sortByName(self):
        self.sections = sorted(self.sections)
        self.reset()

    def sortByArea(self):
        def compare(a, b):
            if a.area > b.area:
                return 1
            else:
                return -1
        self.sections = sorted(self.sections, compare)
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
        baseSection = section.baseSection
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
            #elif column == SLENDER:
                #return '{0:.1f}'.format(section.slender))
            elif column == V2:
                return '{0:.1f}'.format(section.V2)
            elif column == V3:
                return '{0:.1f}'.format(section.V3)
            elif column == XM:
                return '{0:.1f}'.format(section.xm / 10.)
            elif column == YM:
                return '{0:.1f}'.format(section.ym / 10.)

        elif role == Qt.TextAlignmentRole:
            return int(Qt.AlignCenter | Qt.AlignVCenter)
        elif role == Qt.BackgroundColorRole:
            if column == SLENDER:
                if section.slender == u'لاغر':
                    return QColor(250, 40, 0)
                else:
                    return QColor(100, 250, 0)
            elif '14' in baseSection.name:
                return QColor(150, 200, 150)
            elif '16' in baseSection.name:
                return QColor(150, 200, 250)
            elif '18' in baseSection.name:
                return QColor(250, 200, 250)
            elif '20' in baseSection.name:
                return QColor(250, 250, 130)
            elif '22' in baseSection.name:
                return QColor(10, 250, 250)
            elif '24' in baseSection.name:
                return QColor(210, 230, 230)
            elif '27' in baseSection.name:
                return QColor(110, 230, 230)
            elif '30' in baseSection.name:
                return QColor(210, 130, 230)
            else:
                return QColor(150, 150, 250)
        #elif role == Qt.TextColorRole:
            #if column == SLENDER:
                #return Qt.red)

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
            elif section == SLENDER:
                return "Slender"
            elif section == V2:
                return "V2 coef."
            elif section == V3:
                return "V3 coef."
            elif section == XM:
                return "xm (cm)"
            elif section == YM:
                return "ym (cm)"

        return int(section + 1)

    def rowCount(self, index=QModelIndex()):
        return len(self.sections)

    def columnCount(self, index=QModelIndex()):
        return 21

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.sections):
            section = self.sections[index.row()]
            column = index.column()
            if column == NAME:
                section.name = value
            try:
                value = float(value)
                if  value > 0:
                    if column == AREA:
                        section.area = value
                    elif column == ASX:
                        section.ASx = value
                    elif column == ASY:
                        section.ASy = value
                    elif column == IX:
                        section.Ix = value
                    elif column == IY:
                        section.Iy = value
                    elif column == ZX:
                        section.Zx = value
                    elif column == ZY:
                        section.Zy = value
                    elif column == BF:
                        section.bf_equivalentI = value
                    elif column == TF:
                        section.tf_equivalentI = value
                    elif column == D:
                        section.d_equivalentI = value
                    elif column == TW:
                        section.tw_equivalentI = value
                    elif column == XM:
                        section.xm = value
                    elif column == YM:
                        section.ym = value

                    section.Rx = sqrt(section.Ix / section.area)
                    section.Ry = sqrt(section.Iy / section.area)
                    section.Sx = section.Ix / section.ym
                    section.Sy = section.Iy / section.xm
            except ValueError:
                pass

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

    def load(self):
        exception = None
        fh = None
        try:
            #if self.filename.isEmpty():
                #raise IOError, "no filename specified for loading"
            fh = QFile(self.filename)
            #if not fh.open(QIODevice.ReadOnly):
                #raise IOError, unicode(fh.errorString())
            stream = QDataStream(fh)
            magic = stream.readInt32()
            #if magic != MAGIC_NUMBER:
                #raise IOError, "unrecognized file type"
            #fileVersion = stream.readInt16()
            #if fileVersion != FILE_VERSION:
                #raise IOError, "unrecognized file type version"
            self.sections = []
            while not stream.atEnd():
                sectionType = QString()
                useAs = QString()
                ductility = QString()
                stream >> sectionType >> useAs >> ductility
                sectionType = str(sectionType)
                useAs = str(useAs)
                ductility = str(ductility)
                isDouble = stream.readBool()
                isSouble = stream.readBool()
                isTBPlate = stream.readBool()
                lh = stream.readInt16()
                th = stream.readInt16()
                isLRPlate = stream.readBool()
                lv = stream.readInt16()
                tv = stream.readInt16()
                isWebPlate = stream.readBool()
                lw = stream.readInt16()
                tw = stream.readInt16()
                dist = stream.readInt16()
                sectionSize = stream.readInt16()

                section = createSection((lh, th, tv, lv, tw, lw, dist, isTBPlate, isLRPlate,
                    isWebPlate, useAs, ductility, isDouble, isSouble, sectionSize, sectionType))

                self.sections.append(section)
                #self.names.add(unicode(name))
                #self.types.add(unicode(_type))
            self.dirty = False
        #except IOError, err:
            #exception = err
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception

    def save(self):
        exception = None
        fh = None
        try:
            #if self.filename.isEmpty():
                #raise IOError, "no filename specified for saving"
            fh = QFile(self.filename)
            #if not fh.open(QIODevice.WriteOnly):
                #raise IOError, unicode(fh.errorString())
            stream = QDataStream(fh)
            stream.writeInt32(MAGIC_NUMBER)
            stream.writeInt16(FILE_VERSION)
            stream.setVersion(QDataStream.Qt_4_7)
            for section in self.sections:
                #print 'ym of {} = {}'.format(section.name, section.ym)
                stream << QString(section.type) << QString(section.useAs) << QString(section.ductility)
                stream.writeBool(section.isDouble)
                stream.writeBool(section.isSouble)

                if not section.TBPlate:
                    stream.writeBool(False)
                    stream.writeInt16(-1)
                    stream.writeInt16(-1)
                else:
                    stream.writeBool(True)
                    stream.writeInt16(section.TBPlate.bf)
                    stream.writeInt16(section.TBPlate.tf)

                if not section.LRPlate:
                    stream.writeBool(False)
                    stream.writeInt16(-1)
                    stream.writeInt16(-1)
                else:
                    stream.writeBool(True)
                    stream.writeInt16(section.LRPlate.bf)
                    stream.writeInt16(section.LRPlate.tf)

                if not section.webPlate:
                    stream.writeBool(False)
                    stream.writeInt16(-1)
                    stream.writeInt16(-1)
                else:
                    stream.writeBool(True)
                    stream.writeInt16(section.webPlate.bf)
                    stream.writeInt16(section.webPlate.tf)
                baseSection = section.baseSection

                dist = int((section.cc - 2 * (baseSection.bf - baseSection.xm)) / 10)
                stream.writeInt16(dist)
                sectionSize = int(re.sub("[^0-9]", "", str(baseSection.name)))
                stream.writeInt16(sectionSize)

            self.dirty = False
        #except IOError, err:
            #exception = err
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception

if __name__ == '__main__':
    model = SectionTableModel()
