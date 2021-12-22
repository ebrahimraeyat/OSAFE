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


class TestCpeSections(unittest.TestCase):

    def setUp(self):

        CPE = Cpe.createStandardCpes()
        self.__ductility = 'M'
        self.__useAs = 'B'
        self.CPE22 = CPE[22]
        self.CPE22.ductility = self.__ductility
        self.CPE22.useAs = self.__useAs
        self.CPE22_double = DoubleSection(self.CPE22, 0)

        plate1 = Plate(250, 12)
        self.CPE22_TBPlate = AddPlateTB(self.CPE22, plate1)
        self.CPE22_double_TBPlate = AddPlateTB(self.CPE22_double, plate1)

        plate2 = Plate(12, 200)
        self.CPE22_double_4sidePlate = AddPlateLR(self.CPE22_double_TBPlate, plate2)

    def test_CPE22_double(self):
        self.assertFalse(self.CPE22.isDouble)
        self.assertTrue(self.CPE22_double.isDouble)
        self.assertTrue(self.CPE22_double_TBPlate.isDouble)
        self.assertTrue(self.CPE22_double_4sidePlate.isDouble)

    def test_CPE22_useAs(self):
        self.assertEqual(self.CPE22.useAs, self.__useAs)
        self.assertEqual(self.CPE22_double.useAs, self.__useAs)
        self.assertEqual(self.CPE22_double_TBPlate.useAs, self.__useAs)
        self.assertEqual(self.CPE22_double_4sidePlate.useAs, self.__useAs)

    def test_CPE22_ductility(self):
        self.assertEqual(self.CPE22.ductility, self.__ductility)
        self.assertEqual(self.CPE22_double.ductility, self.__ductility)
        self.assertEqual(self.CPE22_double_TBPlate.ductility, self.__ductility)
        self.assertEqual(self.CPE22_double_4sidePlate.ductility, self.__ductility)

    def test_CPE22_composite(self):
        self.assertFalse(self.CPE22.composite)
        self.assertEqual(self.CPE22_double.composite, 'notPlate')
        self.assertEqual(self.CPE22_double_TBPlate.composite, 'TBPlate')
        self.assertEqual(self.CPE22_double_4sidePlate.composite, 'TBLRPLATE')

    def test_CPE22_baseSection(self):
        self.assertEqual(self.CPE22.baseSection, self.CPE22)
        self.assertEqual(self.CPE22_double.baseSection, self.CPE22)
        self.assertEqual(self.CPE22_double_TBPlate.baseSection, self.CPE22)
        self.assertEqual(self.CPE22_double_4sidePlate.baseSection, self.CPE22)

    def test_CPE22_area(self):
        self.assertAlmostEqual(self.CPE22.area, 2690, places=1)
        self.assertAlmostEqual(self.CPE22_double.area, 5380, places=1)
        self.assertAlmostEqual(self.CPE22_double_TBPlate.area, 11380, places=1)
        self.assertAlmostEqual(self.CPE22_double_4sidePlate.area, 16180, places=1)

    def test_CPE22_ASx(self):
        self.assertAlmostEqual(self.CPE22.ASx, 1686.67, places=1)
        self.assertAlmostEqual(self.CPE22_double.ASx, 3373.33, places=1)
        self.assertAlmostEqual(self.CPE22_double_TBPlate.ASx, 9373.33, places=1)
        self.assertAlmostEqual(self.CPE22_double_4sidePlate.ASx, 9373.33, places=1)

    def test_CPE22_ASy(self):
        self.assertAlmostEqual(self.CPE22.ASy, 1243.72, places=1)
        self.assertAlmostEqual(self.CPE22_double.ASy, 2487.44, places=1)
        self.assertAlmostEqual(self.CPE22_double_TBPlate.ASy, 2487.44, places=1)
        self.assertAlmostEqual(self.CPE22_double_4sidePlate.ASy, 7287.44, places=1)

    def test_CPE22_Ix(self):
        self.assertEqual(self.CPE22.Ix, 64600000)
        self.assertEqual(self.CPE22_double.Ix, 129200000)
        # self.assertEqual(self.CPE22_double_TBPlate.Ix, 1.36348e8)
        # self.assertEqual(self.CPE22_double_4sidePlate.Ix, 1.67598e8)
        # self.assertEqual(self.CPE22_double_TBPlate_webPlate.Ix, 141973000)

    def test_CPE22_Iy(self):
        self.assertEqual(self.CPE22.Iy, 2050000)
        self.assertEqual(self.CPE22_double.Iy, 20374500)
        self.assertEqual(self.CPE22_double_TBPlate.Iy, 51624500)
        # self.assertEqual(self.CPE22_double_4sidePlate.Iy, 2.41725e8)
        # self.assertAlmostEqual(self.CPE22_double_TBPlate_webPlate.Iy, 127458107.5, places=1)

    # def test_CPE22_Sx(self):
    #     self.assertAlmostEqual(self.CPE22.Sx, 391515.151, places=1)
    #     self.assertAlmostEqual(self.CPE22_double.Sx, 504909.090, places=1)
    #     self.assertAlmostEqual(self.CPE22_double_TBPlate.Sx, 1117606.557, places=1)
    #     self.assertAlmostEqual(self.CPE22_double_4sidePlate.Sx, 1373754.0983, places=1)

    # def test_CPE22_Sy(self):
    #     self.assertAlmostEqual(self.CPE22.Sy, 37272.7, places=1)
    #     self.assertAlmostEqual(self.CPE22_double.Sy, 220972.7272, places=1)
    #     self.assertAlmostEqual(self.CPE22_double_TBPlate.Sy, 505063.63, places=1)
    #     self.assertAlmostEqual(self.CPE22_double_4sidePlate.Sy, 1492129.629, places=1)

    def test_CPE22_Rx(self):
        self.assertAlmostEqual(self.CPE22.Rx, 154.9673, places=3)
        self.assertAlmostEqual(self.CPE22_double.Rx, 154.9673, places=3)
        # self.assertAlmostEqual(self.CPE22_double_TBPlate.Rx, 103.697, places=3)
        # self.assertAlmostEqual(self.CPE22_double_4sidePlate.Rx, 94.7209, places=3)

    # def test_CPE22_Ry(self):
    #     self.assertAlmostEqual(self.CPE22.Ry, 24.7744, places=3)
    #     self.assertAlmostEqual(self.CPE22_double.Ry, 60.322, places=3)
    #     self.assertAlmostEqual(self.CPE22_double_TBPlate.Ry, 66.19264, places=3)
    #     self.assertAlmostEqual(self.CPE22_double_4sidePlate.Ry, 113.7554, places=3)

    def test_CPE22_Xmax(self):
        self.assertAlmostEqual(self.CPE22.xmax, 110, places=1)
        self.assertAlmostEqual(self.CPE22_double.xmax, 220, places=1)
        # self.assertAlmostEqual(self.CPE22_double_TBPlate.xmax, 300, places=1)
        # self.assertAlmostEqual(self.CPE22_double_4sidePlate.xmax, 324, places=1)

    def test_CPE22_center_to_center(self):
        self.assertEqual(self.CPE22.cc, 0)
        self.assertAlmostEqual(self.CPE22_double.cc, 110, places=1)
        self.assertAlmostEqual(self.CPE22_double_TBPlate.cc, 110, places=1)
        self.assertAlmostEqual(self.CPE22_double_4sidePlate.cc, 110, places=1)

    def test_CPE22_bf(self):
        self.assertAlmostEqual(self.CPE22.bf, 110, places=1)
        self.assertAlmostEqual(self.CPE22_double.bf, 110, places=1)
        self.assertAlmostEqual(self.CPE22_double_TBPlate.bf, 110, places=1)
        self.assertAlmostEqual(self.CPE22_double_4sidePlate.bf, 110, places=1)

    def test_CPE22_J(self):
        self.CPE22_TBPlate.j_func()
        assert self.CPE22_TBPlate.J == 200


    #CPE22.equivalentSectionI()

    #def tearDown(self):
        #pass

    #def test_000_something(self):
        #pass


if __name__ == '__main__':
    unittest.main()
