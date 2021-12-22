#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_civiltools
----------------------------------

Tests for `civiltools` module.
"""
#import sys
import unittest
from .sec import *


class TestIpeSoubleSections(unittest.TestCase):

    def setUp(self):

        IPE = Ipe.createStandardIpes()
        self.__ductility = 'M'
        self.__useAs = 'C'
        self.IPE22 = IPE[22]
        self.IPE22.ductility = self.__ductility
        self.IPE22.useAs = self.__useAs
        self.IPE22_souble = SoubleSection(self.IPE22, 0)

        plate1 = Plate(250, 12)
        self.IPE22_souble_TBPlate = AddPlateTB(self.IPE22_souble, plate1)

        plate2 = Plate(12, 250)
        self.IPE22_souble_4sidePlate = AddPlateLR(self.IPE22_souble_TBPlate, plate2)

    def test_IPE22_double(self):
        self.assertFalse(self.IPE22.isDouble)
        self.assertFalse(self.IPE22_souble.isDouble)
        self.assertFalse(self.IPE22_souble_TBPlate.isDouble)
        self.assertFalse(self.IPE22_souble_4sidePlate.isDouble)

    def test_IPE22_souble(self):
        self.assertFalse(self.IPE22.isSouble)
        self.assertTrue(self.IPE22_souble.isSouble)
        self.assertTrue(self.IPE22_souble_TBPlate.isSouble)
        self.assertTrue(self.IPE22_souble_4sidePlate.isSouble)

    def test_IPE22_useAs(self):
        self.assertEqual(self.IPE22.useAs, self.__useAs)
        self.assertEqual(self.IPE22_souble.useAs, self.__useAs)
        self.assertEqual(self.IPE22_souble_TBPlate.useAs, self.__useAs)
        self.assertEqual(self.IPE22_souble_4sidePlate.useAs, self.__useAs)

    def test_IPE22_ductility(self):
        self.assertEqual(self.IPE22.ductility, self.__ductility)
        self.assertEqual(self.IPE22_souble.ductility, self.__ductility)
        self.assertEqual(self.IPE22_souble_TBPlate.ductility, self.__ductility)
        self.assertEqual(self.IPE22_souble_4sidePlate.ductility, self.__ductility)

    def test_IPE22_composite(self):
        self.assertFalse(self.IPE22.composite)
        self.assertEqual(self.IPE22_souble.composite, 'notPlate')
        self.assertEqual(self.IPE22_souble_TBPlate.composite, 'TBPlate')
        self.assertEqual(self.IPE22_souble_4sidePlate.composite, 'TBLRPLATE')

    def test_IPE22_baseSection(self):
        self.assertEqual(self.IPE22.baseSection, self.IPE22)
        self.assertEqual(self.IPE22_souble.baseSection, self.IPE22)
        self.assertEqual(self.IPE22_souble_TBPlate.baseSection, self.IPE22)
        self.assertEqual(self.IPE22_souble_4sidePlate.baseSection, self.IPE22)

    def test_IPE22_area(self):
        self.assertAlmostEqual(self.IPE22.area, 3340, places=1)
        self.assertAlmostEqual(self.IPE22_souble.area, 10020, places=1)
        self.assertAlmostEqual(self.IPE22_souble_TBPlate.area, 16020, places=1)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.area, 22020, places=1)

    def test_IPE22_ASx(self):
        self.assertAlmostEqual(self.IPE22.ASx, 1686.67, places=1)
        self.assertAlmostEqual(self.IPE22_souble.ASx, 5060.01, places=1)
        self.assertAlmostEqual(self.IPE22_souble_TBPlate.ASx, 11060.01, places=1)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.ASx, 11060.01, places=1)

    def test_IPE22_ASy(self):
        self.assertAlmostEqual(self.IPE22.ASy, 1243.72, places=1)
        self.assertAlmostEqual(self.IPE22_souble.ASy, 3731.16, places=1)
        self.assertAlmostEqual(self.IPE22_souble_TBPlate.ASy, 3731.16, places=1)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.ASy, 9731.16, places=1)

    def test_IPE22_Ix(self):
        self.assertEqual(self.IPE22.Ix, 27770000)
        self.assertEqual(self.IPE22_souble.Ix, 83310000)
        self.assertEqual(self.IPE22_souble_TBPlate.Ix, 164118000)
        self.assertEqual(self.IPE22_souble_4sidePlate.Ix, 195368000)

    def test_IPE22_Iy(self):
        self.assertEqual(self.IPE22.Iy, 2050000)
        self.assertEqual(self.IPE22_souble.Iy, 86978000)
        self.assertEqual(self.IPE22_souble_TBPlate.Iy, 118228000)
        self.assertEqual(self.IPE22_souble_4sidePlate.Iy, 293746000)

    def test_IPE22_Zx(self):
        self.assertEqual(self.IPE22.Zx, 285000)
        self.assertEqual(self.IPE22_souble.Zx, 855000)
        self.assertEqual(self.IPE22_souble_TBPlate.Zx, 1551000)
        self.assertEqual(self.IPE22_souble_4sidePlate.Zx, 1926000)

    def test_IPE22_Zy(self):
        self.assertEqual(self.IPE22.Zy, 58100)
        self.assertEqual(self.IPE22_souble.Zy, 792900)
        self.assertEqual(self.IPE22_souble_TBPlate.Zy, 1167900)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.Zy, 2193900)

    #def test_IPE22_Sx(self):
        #self.assertAlmostEqual(self.IPE22.Sx, 252454.5454, places=1)
        #self.assertAlmostEqual(self.IPE22_double.Sx, 504909.090, places=1)
        #self.assertAlmostEqual(self.IPE22_double_TBPlate.Sx, 1117606.557, places=1)
        #self.assertAlmostEqual(self.IPE22_double_4sidePlate.Sx, 1373754.0983, places=1)

    #def test_IPE22_Sy(self):
        #self.assertAlmostEqual(self.IPE22.Sy, 37272.7, places=1)
        #self.assertAlmostEqual(self.IPE22_double.Sy, 429246.6666, places=1)
        #self.assertAlmostEqual(self.IPE22_double_TBPlate.Sy, 637580.0, places=1)
        #self.assertAlmostEqual(self.IPE22_double_4sidePlate.Sy, 1492129.629, places=1)

    #def test_IPE22_Rx(self):
        #self.assertAlmostEqual(self.IPE22.Rx, 91.1832, places=3)
        #self.assertAlmostEqual(self.IPE22_double.Rx, 91.1832, places=3)
        #self.assertAlmostEqual(self.IPE22_double_TBPlate.Rx, 103.697, places=3)
        #self.assertAlmostEqual(self.IPE22_double_4sidePlate.Rx, 94.7209, places=3)

    #def test_IPE22_Ry(self):
        #self.assertAlmostEqual(self.IPE22.Ry, 24.7744, places=3)
        #self.assertAlmostEqual(self.IPE22_double.Ry, 98.1773, places=3)
        #self.assertAlmostEqual(self.IPE22_double_TBPlate.Ry, 86.8467, places=3)
        #self.assertAlmostEqual(self.IPE22_double_4sidePlate.Ry, 113.7554, places=3)

    def test_IPE22_Xmax(self):
        self.assertAlmostEqual(self.IPE22.xmax, 110, places=1)
        self.assertAlmostEqual(self.IPE22_souble.xmax, 330, places=1)
        self.assertAlmostEqual(self.IPE22_souble_TBPlate.xmax, 330, places=1)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.xmax, 354, places=1)

    def test_IPE22_Xm(self):
        self.assertAlmostEqual(self.IPE22.xm, 55, places=1)
        self.assertAlmostEqual(self.IPE22_souble.xm, 165, places=1)
        self.assertAlmostEqual(self.IPE22_souble_TBPlate.xm, 165, places=1)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.xm, 177, places=1)

    def test_IPE22_center_to_center(self):
        self.assertEqual(self.IPE22.cc, 0)
        self.assertAlmostEqual(self.IPE22_souble.cc, 110, places=1)
        self.assertAlmostEqual(self.IPE22_souble_TBPlate.cc, 110, places=1)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.cc, 110, places=1)

    def test_IPE22_bf(self):
        self.assertAlmostEqual(self.IPE22.bf, 110, places=1)
        self.assertAlmostEqual(self.IPE22_souble.bf, 110, places=1)
        self.assertAlmostEqual(self.IPE22_souble_TBPlate.bf, 110, places=1)
        self.assertAlmostEqual(self.IPE22_souble_4sidePlate.bf, 110, places=1)

    #def test_IPE22_bf_equivalent(self):
        #self.assertAlmostEqual(self.IPE22.bf_equivalentI, 110, places=1)
        #self.assertAlmostEqual(self.IPE22_souble.bf_equivalentI, 330, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_TBPlate.bf_equivalentI, 330, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_4sidePlate.bf_equivalentI, 330, places=1)

    #def test_IPE22_tf_equivalent(self):
        #self.assertAlmostEqual(self.IPE22.tf_equivalentI, 9.2, places=1)
        #self.assertAlmostEqual(self.IPE22_souble.tf_equivalentI, 27.5999, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_TBPlate.tf_equivalentI, 27.5999, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_4sidePlate.tf_equivalentI, 27.5999, places=1)

    #def test_IPE22_d_equivalent(self):
        #self.assertAlmostEqual(self.IPE22.d_equivalentI, 220, places=1)
        #self.assertAlmostEqual(self.IPE22_souble.d_equivalentI, 220, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_TBPlate.d_equivalentI, 220, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_4sidePlate.d_equivalentI, 220, places=1)

    #def test_IPE22_tw_equivalent(self):
        #self.assertAlmostEqual(self.IPE22.tw_equivalentI, 5.9, places=1)
        #self.assertAlmostEqual(self.IPE22_souble.tw_equivalentI, 5.9, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_TBPlate.tw_equivalentI, 5.9, places=1)
        #self.assertAlmostEqual(self.IPE22_souble_4sidePlate.tw_equivalentI, 5.9, places=1)

    #def test_equivalent_IPE22_V2(self):
        #self.assertEqual(self.IPE22.V2, 1)
        #self.assertAlmostEqual(self.IPE22_double.V2, 1.85778, places=4)
        #self.assertAlmostEqual(self.IPE22_double_TBPlate.V2, 1.52249, places=4)
        #self.assertAlmostEqual(self.IPE22_double_4sidePlate.V2, 5.28392, places=4)

    #def test_equivalent_IPE22_V3(self):
        #self.assertEqual(self.IPE22.V3, 1)
        #self.assertAlmostEqual(self.IPE22_double.V3, 0.416667, places=4)
        #self.assertAlmostEqual(self.IPE22_double_TBPlate.V3, 0.736166, places=4)
        #self.assertAlmostEqual(self.IPE22_double_4sidePlate.V3, 0.63114, places=4)



    #IPE22.equivalentSectionI()

    #def tearDown(self):
        #pass

    #def test_000_something(self):
        #pass
if __name__ == '__main__':
    unittest.main()
