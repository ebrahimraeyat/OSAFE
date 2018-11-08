# -*- coding: utf-8 -*-
import ArchProfile
import Draft
import FreeCAD as App
import FreeCADGui as Gui
import sec

ipesProp = sec.Ipe.createStandardIpes()
unpsProp = sec.Unp.createStandardUnps()
cpesProp = sec.Cpe.createStandardCpes()
sectionProp = {'IPE': ipesProp, 'UNP': unpsProp, 'CPE': cpesProp}
base_section_type = {'IPE': 'H', 'UNP': 'U', 'CPE': 'H'}

LH, TH, LV, TV, LW, TW, DIST, ISTBPLATE, ISLRPLATE, ISWEBPLATE, USEAS, DUCTILITY, ISDOUBLE, \
ISSOUBLE, SECTIONSIZE, SECTIONTYPE, CONVERT_TYPE = range(17)

class PlotSectionAndEqSection(object):

    def __init__(self, section_prop, row=0):
        self.row = row
        self.section_prop = section_prop

    def plot(self):
        sectionType = self.section_prop[SECTIONTYPE]    # IPE
        sectionSize = self.section_prop[SECTIONSIZE]    # 22
        baseSection = sectionProp[sectionType][sectionSize] # IPE22 SECTION
        baseSectionType = base_section_type[sectionType]     # H, U
        bf = baseSection.bf_equivalentI
        d = baseSection.d_equivalentI
        tf = baseSection.tf_equivalentI
        tw = baseSection.tw_equivalentI
        if sectionType == 'UNP':
            bf, d, tf, tw = d, bf, tw, tf
        dist = self.section_prop[DIST] * 10
        doc = App.getDocument("current_section")
        group=doc.addObject("App::DocumentObjectGroup","Profiles_set")
        s1 = ArchProfile.makeProfile([0, sectionType, sectionType + '_000', baseSectionType ,bf, d, tw, tf])
        obj = doc.getObjectsByLabel(s1.Label)[0]
        doc.recompute()
        if sectionType == 'UNP':
            Draft.rotate(doc.UNP_000, 90)
        group.addObject(s1)
        deltax = baseSection.bf + dist
        if self.section_prop[ISSOUBLE]:
            Draft.move(obj, App.Vector(deltax, 0, 0))
            s2 = ArchProfile.makeProfile([0, sectionType, sectionType + '_000', baseSectionType ,bf, d, tw, tf])
            s3 = Draft.rotate(obj, 180, center=App.Vector(0, 0, 0), copy=True)
            group.addObjects([s2, s3])

        if self.section_prop[ISDOUBLE]:
            Draft.move(obj, App.Vector(deltax / 2, 0, 0))
            s2 = Draft.rotate(obj, 180, center=App.Vector(0, 0, 0), copy=True)
            group.addObject(s2)

        if self.section_prop[ISTBPLATE]:
            y = obj.Shape.OuterWire.BoundBox.YMax + self.section_prop[TH] / 2
            p3 = App.Vector(0, y, 0)
            width = self.section_prop[LH]
            height = self.section_prop[TH]
            plt = ArchProfile.makeProfile([0, 'PlateT', 'PlateT' + '_000', 'R' , width, height])
            Draft.move(doc.PlateT_000, p3)
            plb = Draft.rotate(doc.PlateT_000, 180, center=App.Vector(0, 0, 0), copy=True)
            group.addObjects([plt, plb])

        if self.section_prop[ISLRPLATE]:
            width = self.section_prop[LV]
            height = self.section_prop[TV]
            x = obj.Shape.OuterWire.BoundBox.XMax + height / 2
            p5 = App.Vector(x, 0, 0)
            plr = ArchProfile.makeProfile([0, 'PlateR', 'PlateR' + '_000', 'R' , height, width])
            Draft.move(doc.PlateR_000, p5)
            pll = Draft.rotate(doc.PlateR_000, 180, center=App.Vector(0, 0, 0), copy=True)
            group.addObjects([plr, pll])

        if self.section_prop[ISWEBPLATE]:
            width = self.section_prop[LW]
            height = self.section_prop[TW]
            x = obj.Shape.BoundBox.Center.x + (obj.WebThickness.Value + height) / 2
            p6 = App.Vector(x, 0, 0)
            plwr = ArchProfile.makeProfile([0, 'PlateWR', 'PlateWR' + '_000', 'R' , height, width])
            Draft.move(doc.PlateWR_000, p6)
            plwl = Draft.rotate(doc.PlateWR_000, 180, center=App.Vector(0, 0, 0), copy=True)
            group.addObjects([plwr, plwl])
            
        doc.recompute()


    # def textItem(self, win, html, pos=None, anchor=(0, 0), isFill=True, isRotate=False):
    #     if isFill:
    #         text = pg.TextItem(html=html, anchor=anchor, border='k', fill=(0, 0, 255, 100))
    #     else:
    #         text = pg.TextItem(html=html, anchor=anchor)
    #     if isRotate:
    #         text.setRotation(90)
    #     win.addItem(text)
    #     if pos:
    #         text.setPos(pos.x, pos.y)
    #         pos = Point(pos.x, pos.y + anchor[1] * 20)
    #         self.add_text_to_script_file(html, pos, isRotate)
    #     else:
    #         text.setPos(0, 0)
