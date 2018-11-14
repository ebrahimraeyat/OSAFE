#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_civiltools
----------------------------------

Tests for `civiltools` module.
"""
#import sys
import unittest
from sec import *


class TestIpeSections(unittest.TestCase):

    def setUp(self):

        IPE = Ipe.createStandardIpes()
        self.__ductility = 'M'
        self.__useAs = 'C'
        self.IPE22 = IPE[22]
        self.IPE22.ductility = self.__ductility
        self.IPE22.useAs = self.__useAs
        self.IPE22_double = DoubleSection(self.IPE22, 8)

        plate1 = Plate(250, 12)
        self.IPE22_double_TBPlate = AddPlateTB(self.IPE22_double, plate1)

        plate2 = Plate(12, 250)
        self.IPE22_double_4sidePlate = AddPlateLR(self.IPE22_double_TBPlate, plate2)

        plate3 = Plate(10, 150)
        self.IPE22_double_TBPlate_webPlate = AddPlateWeb(self.IPE22_double_TBPlate, plate3)

    def test_IPE22_double(self):
        self.assertFalse(self.IPE22.isDouble)
        self.assertTrue(self.IPE22_double.isDouble)
        self.assertTrue(self.IPE22_double_TBPlate.isDouble)
        self.assertTrue(self.IPE22_double_4sidePlate.isDouble)
        self.assertTrue(self.IPE22_double_TBPlate_webPlate.isDouble)

    def test_IPE22_useAs(self):
        self.assertEqual(self.IPE22.useAs, self.__useAs)
        self.assertEqual(self.IPE22_double.useAs, self.__useAs)
        self.assertEqual(self.IPE22_double_TBPlate.useAs, self.__useAs)
        self.assertEqual(self.IPE22_double_4sidePlate.useAs, self.__useAs)
        self.assertEqual(self.IPE22_double_TBPlate_webPlate.useAs, self.__useAs)

    def test_IPE22_ductility(self):
        self.assertEqual(self.IPE22.ductility, self.__ductility)
        self.assertEqual(self.IPE22_double.ductility, self.__ductility)
        self.assertEqual(self.IPE22_double_TBPlate.ductility, self.__ductility)
        self.assertEqual(self.IPE22_double_4sidePlate.ductility, self.__ductility)
        self.assertEqual(self.IPE22_double_TBPlate_webPlate.ductility, self.__ductility)

    def test_IPE22_composite(self):
        self.assertFalse(self.IPE22.composite)
        self.assertEqual(self.IPE22_double.composite, 'notPlate')
        self.assertEqual(self.IPE22_double_TBPlate.composite, 'TBPlate')
        self.assertEqual(self.IPE22_double_4sidePlate.composite, 'LRPlate')
        self.assertEqual(self.IPE22_double_TBPlate_webPlate.composite, 'LRPlate')

    def test_IPE22_baseSection(self):
        self.assertEqual(self.IPE22.baseSection, self.IPE22)
        self.assertEqual(self.IPE22_double.baseSection, self.IPE22)
        self.assertEqual(self.IPE22_double_TBPlate.baseSection, self.IPE22)
        self.assertEqual(self.IPE22_double_4sidePlate.baseSection, self.IPE22)
        self.assertEqual(self.IPE22_double_TBPlate_webPlate.baseSection, self.IPE22)

    def test_IPE22_area(self):
        self.assertAlmostEqual(self.IPE22.area, 3340, places=1)
        self.assertAlmostEqual(self.IPE22_double.area, 6680, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.area, 12680, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.area, 18680, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate_webPlate.area, 15680, places=1)

    def test_IPE22_ASx(self):
        self.assertAlmostEqual(self.IPE22.ASx, 1686.67, places=1)
        self.assertAlmostEqual(self.IPE22_double.ASx, 3373.33, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.ASx, 9373.33, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.ASx, 9373.33, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate_webPlate.ASx, 9373.33, places=1)

    def test_IPE22_ASy(self):
        self.assertAlmostEqual(self.IPE22.ASy, 1243.72, places=1)
        self.assertAlmostEqual(self.IPE22_double.ASy, 2487.44, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.ASy, 2487.44, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.ASy, 8487.44, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate_webPlate.ASy, 5487.44, places=1)

    def test_IPE22_Ix(self):
        self.assertEqual(self.IPE22.Ix, 27770000)
        self.assertEqual(self.IPE22_double.Ix, 55540000)
        self.assertEqual(self.IPE22_double_TBPlate.Ix, 1.36348e8)
        self.assertEqual(self.IPE22_double_4sidePlate.Ix, 1.67598e8)
        self.assertEqual(self.IPE22_double_TBPlate_webPlate.Ix, 141973000)

    def test_IPE22_Iy(self):
        self.assertEqual(self.IPE22.Iy, 2050000)
        self.assertEqual(self.IPE22_double.Iy, 6.4387e7)
        self.assertEqual(self.IPE22_double_TBPlate.Iy, 9.5637e7)
        self.assertEqual(self.IPE22_double_4sidePlate.Iy, 2.41725e8)
        self.assertAlmostEqual(self.IPE22_double_TBPlate_webPlate.Iy, 127458107.5, places=1)

    def test_IPE22_Zx(self):
        self.assertEqual(self.IPE22.Zx, 285000)
        self.assertEqual(self.IPE22_double.Zx, 570000)
        self.assertEqual(self.IPE22_double_TBPlate.Zx, 1.266e6)
        self.assertEqual(self.IPE22_double_4sidePlate.Zx, 1.641e6)
        self.assertEqual(self.IPE22_double_TBPlate_webPlate.Zx, 1378500)

    def test_IPE22_Zy(self):
        self.assertEqual(self.IPE22.Zy, 58100)
        self.assertEqual(self.IPE22_double.Zy, 634600)
        self.assertEqual(self.IPE22_double_TBPlate.Zy, 1.0096e6)
        self.assertEqual(self.IPE22_double_4sidePlate.Zy, 1.9456e6)
        self.assertEqual(self.IPE22_double_TBPlate_webPlate.Zy, 1318450)

    def test_IPE22_Sx(self):
        self.assertAlmostEqual(self.IPE22.Sx, 252454.5454, places=1)
        self.assertAlmostEqual(self.IPE22_double.Sx, 504909.090, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.Sx, 1117606.557, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.Sx, 1373754.0983, places=1)

    def test_IPE22_Sy(self):
        self.assertAlmostEqual(self.IPE22.Sy, 37272.7, places=1)
        self.assertAlmostEqual(self.IPE22_double.Sy, 429246.6666, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.Sy, 637580.0, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.Sy, 1492129.629, places=1)

    def test_IPE22_Rx(self):
        self.assertAlmostEqual(self.IPE22.Rx, 91.1832, places=3)
        self.assertAlmostEqual(self.IPE22_double.Rx, 91.1832, places=3)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.Rx, 103.697, places=3)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.Rx, 94.7209, places=3)

    def test_IPE22_Ry(self):
        self.assertAlmostEqual(self.IPE22.Ry, 24.7744, places=3)
        self.assertAlmostEqual(self.IPE22_double.Ry, 98.1773, places=3)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.Ry, 86.8467, places=3)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.Ry, 113.7554, places=3)

    def test_IPE22_Xmax(self):
        self.assertAlmostEqual(self.IPE22.xmax, 110, places=1)
        self.assertAlmostEqual(self.IPE22_double.xmax, 300, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.xmax, 300, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.xmax, 324, places=1)

    def test_IPE22_center_to_center(self):
        self.assertEqual(self.IPE22.cc, 0)
        self.assertAlmostEqual(self.IPE22_double.cc, 190, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.cc, 190, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.cc, 190, places=1)

    def test_IPE22_bf(self):
        self.assertAlmostEqual(self.IPE22.bf, 110, places=1)
        self.assertAlmostEqual(self.IPE22_double.bf, 110, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.bf, 110, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.bf, 110, places=1)

    def test_IPE22_bf_equivalent(self):
        self.assertAlmostEqual(self.IPE22.bf_equivalentI, 110, places=1)
        self.assertAlmostEqual(self.IPE22_double.bf_equivalentI, 300, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.bf_equivalentI, 300, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.bf_equivalentI, 324, places=1)

    def test_IPE22_tf_equivalent(self):
        self.assertAlmostEqual(self.IPE22.tf_equivalentI, 9.2, places=1)
        self.assertAlmostEqual(self.IPE22_double.tf_equivalentI, 25.09, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.tf_equivalentI, 21.2211, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.tf_equivalentI, 22.9187, places=1)

    def test_IPE22_d_equivalent(self):
        self.assertAlmostEqual(self.IPE22.d_equivalentI, 220, places=1)
        self.assertAlmostEqual(self.IPE22_double.d_equivalentI, 220, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.d_equivalentI, 244, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.d_equivalentI, 244, places=1)

    def test_IPE22_tw_equivalent(self):
        self.assertAlmostEqual(self.IPE22.tw_equivalentI, 5.9, places=1)
        self.assertAlmostEqual(self.IPE22_double.tw_equivalentI, 5.6414, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.tw_equivalentI, 6.6959, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.tw_equivalentI, 6.5831, places=1)

    def test_IPE22_cw(self):
        self.assertAlmostEqual(self.IPE22.cw, 22672314338.666, places=1)
        self.assertAlmostEqual(self.IPE22_double.cw, 118058883054.29332, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate.cw, 538558883054.293, places=1)
        self.assertAlmostEqual(self.IPE22_double_4sidePlate.cw, 1299058883054.293, places=1)
        self.assertAlmostEqual(self.IPE22_double_TBPlate_webPlate.cw, 598176584616.7933, places=1)

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
