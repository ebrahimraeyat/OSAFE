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


class TestUnpSections(unittest.TestCase):

    def setUp(self):

        UNP = Unp.createStandardUnps()
        self.__ductility = 'M'
        self.__useAs = 'C'
        self.UNP22 = UNP[22]
        self.UNP22.ductility = self.__ductility
        self.UNP22.useAs = self.__useAs
        self.UNP22_double = DoubleSection(self.UNP22, 80)

        plate1 = Plate(250, 12)
        self.UNP22_double_TBPlate = AddPlateTB(self.UNP22_double, plate1)

        plate2 = Plate(12, 200)
        self.UNP22_double_4sidePlate = AddPlateLR(self.UNP22_double_TBPlate, plate2)

    def test_UNP22_double(self):
        self.assertFalse(self.UNP22.isDouble)
        self.assertTrue(self.UNP22_double.isDouble)
        self.assertTrue(self.UNP22_double_TBPlate.isDouble)
        self.assertTrue(self.UNP22_double_4sidePlate.isDouble)

    def test_UNP22_useAs(self):
        self.assertEqual(self.UNP22.useAs, self.__useAs)
        self.assertEqual(self.UNP22_double.useAs, self.__useAs)
        self.assertEqual(self.UNP22_double_TBPlate.useAs, self.__useAs)
        self.assertEqual(self.UNP22_double_4sidePlate.useAs, self.__useAs)

    def test_UNP22_ductility(self):
        self.assertEqual(self.UNP22.ductility, self.__ductility)
        self.assertEqual(self.UNP22_double.ductility, self.__ductility)
        self.assertEqual(self.UNP22_double_TBPlate.ductility, self.__ductility)
        self.assertEqual(self.UNP22_double_4sidePlate.ductility, self.__ductility)

    def test_UNP22_composite(self):
        self.assertFalse(self.UNP22.composite)
        self.assertEqual(self.UNP22_double.composite, 'notPlate')
        self.assertEqual(self.UNP22_double_TBPlate.composite, 'TBPlate')
        self.assertEqual(self.UNP22_double_4sidePlate.composite, 'TBLRPLATE')

    def test_UNP22_baseSection(self):
        self.assertEqual(self.UNP22.baseSection, self.UNP22)
        self.assertEqual(self.UNP22_double.baseSection, self.UNP22)
        self.assertEqual(self.UNP22_double_TBPlate.baseSection, self.UNP22)
        self.assertEqual(self.UNP22_double_4sidePlate.baseSection, self.UNP22)

    def test_UNP22_area(self):
        self.assertAlmostEqual(self.UNP22.area, 3744, places=1)
        self.assertAlmostEqual(self.UNP22_double.area, 7488, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.area, 13488, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.area, 18288, places=1)

    def test_UNP22_ASx(self):
        self.assertAlmostEqual(self.UNP22.ASx, 1666.6667, places=1)
        self.assertAlmostEqual(self.UNP22_double.ASx, 3333.3334, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.ASx, 9333.3334, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.ASx, 9333.3334, places=1)

    def test_UNP22_ASy(self):
        self.assertAlmostEqual(self.UNP22.ASy, 1867.5, places=1)
        self.assertAlmostEqual(self.UNP22_double.ASy, 3735.0, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.ASy, 3735.0, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.ASy, 8535.0, places=1)

    def test_UNP22_Ix(self):
        self.assertAlmostEqual(self.UNP22.Ix, 26910000.0, places=1)
        self.assertAlmostEqual(self.UNP22_double.Ix, 53820000, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.Ix, 134628000.0, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.Ix, 150628000.0, places=1)

    def test_UNP22_Iy(self):
        self.assertAlmostEqual(self.UNP22.Iy, 1966000, places=1)
        self.assertAlmostEqual(self.UNP22_double.Iy, 76789113.8048, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.Iy, 108039113.8048, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.Iy, 184301513.8048, places=1)

    def test_UNP22_Zx(self):
        self.assertEqual(self.UNP22.Zx, 298800)
        self.assertEqual(self.UNP22_double.Zx, 597600)
        self.assertEqual(self.UNP22_double_TBPlate.Zx, 1293600)
        self.assertEqual(self.UNP22_double_4sidePlate.Zx, 1533600)

    def test_UNP22_Zy(self):
        self.assertAlmostEqual(self.UNP22.Zy, 71870, places=1)
        self.assertAlmostEqual(self.UNP22_double.Zy, 738616.32, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.Zy, 1113616.31999, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.Zy, 1718416.31999, places=1)

    def test_UNP22_Sx(self):
        self.assertAlmostEqual(self.UNP22.Sx, 244636.3636, places=1)
        self.assertAlmostEqual(self.UNP22_double.Sx, 489272.7272, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.Sx, 1103508.1967, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.Sx, 1234655.7377, places=1)

    def test_UNP22_Sy(self):
        # self.assertAlmostEqual(self.UNP22.Sy, 37272.7, places=1)
        self.assertAlmostEqual(self.UNP22_double.Sy, 639909.2817, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.Sy, 900325.9483, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.Sy, 1396223.5894, places=1)

    # def test_UNP22_Rx(self):
        #self.assertAlmostEqual(self.UNP22.Rx, 91.1832, places=3)
        #self.assertAlmostEqual(self.UNP22_double.Rx, 91.1832, places=3)
        #self.assertAlmostEqual(self.UNP22_double_TBPlate.Rx, 103.697, places=3)
        #self.assertAlmostEqual(self.UNP22_double_4sidePlate.Rx, 94.7209, places=3)

    # def test_UNP22_Ry(self):
        #self.assertAlmostEqual(self.UNP22.Ry, 24.7744, places=3)
        #self.assertAlmostEqual(self.UNP22_double.Ry, 98.1773, places=3)
        #self.assertAlmostEqual(self.UNP22_double_TBPlate.Ry, 86.8467, places=3)
        #self.assertAlmostEqual(self.UNP22_double_4sidePlate.Ry, 113.7554, places=3)

    def test_UNP22_Xmax(self):
        self.assertAlmostEqual(self.UNP22.xmax, 80, places=1)
        self.assertAlmostEqual(self.UNP22_double.xmax, 240, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.xmax, 240, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.xmax, 264, places=1)

    def test_UNP22_center_to_center(self):
        self.assertEqual(self.UNP22.cc, 0)
        self.assertAlmostEqual(self.UNP22_double.cc, 197.28, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.cc, 197.28, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.cc, 197.28, places=1)

    def test_UNP22_bf(self):
        self.assertAlmostEqual(self.UNP22.bf, 80, places=1)
        self.assertAlmostEqual(self.UNP22_double.bf, 80, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.bf, 80, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.bf, 80, places=1)

    def test_UNP22_bf_equivalent(self):
        self.assertAlmostEqual(self.UNP22.bf_equivalentI, 160, places=1)
        self.assertAlmostEqual(self.UNP22_double.bf_equivalentI, 240, places=1)
        self.assertAlmostEqual(self.UNP22_double_TBPlate.bf_equivalentI, 240, places=1)
        self.assertAlmostEqual(self.UNP22_double_4sidePlate.bf_equivalentI, 264, places=1)

    # def test_UNP22_tf_equivalent(self):
        #self.assertAlmostEqual(self.UNP22.tf_equivalentI, 9.2, places=1)
        #self.assertAlmostEqual(self.UNP22_double.tf_equivalentI, 18.4, places=1)
        #self.assertAlmostEqual(self.UNP22_double_TBPlate.tf_equivalentI, 21.2211, places=1)
        #self.assertAlmostEqual(self.UNP22_double_4sidePlate.tf_equivalentI, 22.9187, places=1)

    # def test_UNP22_d_equivalent(self):
        #self.assertAlmostEqual(self.UNP22.d_equivalentI, 220, places=1)
        #self.assertAlmostEqual(self.UNP22_double.d_equivalentI, 220, places=1)
        #self.assertAlmostEqual(self.UNP22_double_TBPlate.d_equivalentI, 244, places=1)
        #self.assertAlmostEqual(self.UNP22_double_4sidePlate.d_equivalentI, 244, places=1)

    # def test_UNP22_tw_equivalent(self):
        #self.assertAlmostEqual(self.UNP22.tw_equivalentI, 5.9, places=1)
        #self.assertAlmostEqual(self.UNP22_double.tw_equivalentI, 6.08604, places=1)
        #self.assertAlmostEqual(self.UNP22_double_TBPlate.tw_equivalentI, 6.6959, places=1)
        #self.assertAlmostEqual(self.UNP22_double_4sidePlate.tw_equivalentI, 6.5831, places=1)

    # def test_equivalent_UNP22_V2(self):
        #self.assertEqual(self.UNP22.V2, 1)
        #self.assertAlmostEqual(self.UNP22_double.V2, 1.85778, places=4)
        #self.assertAlmostEqual(self.UNP22_double_TBPlate.V2, 1.52249, places=4)
        #self.assertAlmostEqual(self.UNP22_double_4sidePlate.V2, 5.28392, places=4)

    # def test_equivalent_UNP22_V3(self):
        #self.assertEqual(self.UNP22.V3, 1)
        #self.assertAlmostEqual(self.UNP22_double.V3, 0.416667, places=4)
        #self.assertAlmostEqual(self.UNP22_double_TBPlate.V3, 0.736166, places=4)
        #self.assertAlmostEqual(self.UNP22_double_4sidePlate.V3, 0.63114, places=4)

    # UNP22.equivalentSectionI()

    # def tearDown(self):
        # pass

    # def test_000_something(self):
        # pass


if __name__ == '__main__':
    unittest.main()
