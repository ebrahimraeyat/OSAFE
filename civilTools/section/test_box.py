import unittest
from .sec import Box, Plate, AddPlateTB, AddPlateLR


class TestBox(unittest.TestCase):

    def setUp(self):
        box1_empty = Box(300, 300, mode=1)
        box2_empty = Box(260, 300, mode=2)
        box3_empty = Box(496, 410)
        TBPlate = Plate(300, 20)
        LRPlate = Plate(20, 300)
        TBPlate_J = Plate(600, 45)
        LRPlate_J = Plate(52, 410)
        box1_tb = AddPlateTB(box1_empty, TBPlate)
        box2_tb = AddPlateTB(box2_empty, TBPlate)
        box3_tb = AddPlateTB(box3_empty, TBPlate_J)
        self.box1 = AddPlateLR(box1_tb, LRPlate)
        self.box2 = AddPlateLR(box2_tb, LRPlate)
        self.box3 = AddPlateLR(box3_tb, LRPlate_J)

    def test_area(self):
        self.assertAlmostEqual(self.box1.area, 24000, places=0)
        self.assertAlmostEqual(self.box2.area, 24000, places=0)

    def test_Asx(self):
        self.assertEqual(self.box1.ASx, 120e2)
        self.assertEqual(self.box2.ASx, 120e2)

    def test_Asy(self):
        self.assertEqual(self.box1.ASy, 120e2)
        self.assertEqual(self.box2.ASy, 120e2)

    def test_Ix(self):
        self.assertEqual(self.box1.Ix, 39760e4)
        self.assertEqual(self.box2.Ix, 39760e4)

    def test_Iy(self):
        self.assertEqual(self.box1.Iy, 39760e4)
        self.assertEqual(self.box2.Iy, 32560e4)

    def test_zx(self):
        self.assertEqual(self.box1.Zx, 2820e3)
        self.assertEqual(self.box2.Zx, 2820e3)

    def test_zy(self):
        self.assertEqual(self.box1.Zy, 2820e3)
        self.assertEqual(self.box2.Zy, 2580e3)

    def test_sx(self):
        self.assertAlmostEqual(self.box1.Sx, 2338823.52, places=1)
        self.assertAlmostEqual(self.box2.Sx, 2338823.52, places=1)

    def test_sy(self):
        self.assertAlmostEqual(self.box1.Sy, 2338823.52, places=1)
        self.assertAlmostEqual(self.box2.Sy, 2170666.66, places=1)

    def test_rx(self):
        self.assertAlmostEqual(self.box1.Rx, 128.7, places=1)
        self.assertAlmostEqual(self.box2.Rx, 128.7, places=1)

    def test_ry(self):
        self.assertAlmostEqual(self.box1.Ry, 128.7, places=1)
        self.assertAlmostEqual(self.box2.Ry, 116.47, places=1)

    def test_bf_equivalent(self):
        self.assertEqual(self.box1.bf_equivalentI, 300)
        self.assertEqual(self.box2.bf_equivalentI, 300)

    def test_tf_equivalent(self):
        self.assertEqual(self.box1.tf_equivalentI, 20)
        self.assertEqual(self.box2.tf_equivalentI, 20)

    def test_d_equivalent(self):
        self.assertEqual(self.box1.d_equivalentI, 340)
        self.assertEqual(self.box2.d_equivalentI, 340)

    def test_bf_equivalent(self):
        self.assertEqual(self.box1.tw_equivalentI, 40)
        self.assertEqual(self.box2.tw_equivalentI, 40)

    def test_cw(self):
        self.assertEqual(self.box1.cw, 0)
        self.assertEqual(self.box2.cw, 0)

    def test_j(self):
        self.assertAlmostEqual(self.box2.J, 535210666.66, places=0)
        self.assertAlmostEqual(self.box3.J, 5941427347, places=0)
