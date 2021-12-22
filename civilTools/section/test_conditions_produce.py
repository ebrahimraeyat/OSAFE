import unittest
from resource.produce_conditions import *
import sympy
bf, tf, d, tw, BF, TF, D, TW, B1, t1, t2, w, Ca, r = sympy.symbols('bf tf d tw BF TF D TW B1 t1 t2 w Ca r')


class Test_conditions_produce(unittest.TestCase):

    def setUp(self):
        pass

    def test_2IPE_flang_plate_web_plate_beam_high_ductility_conditions_TF(self):

        if_condition, if_equal_TF, else_equal_TF = produce_conditions_from_slender_provision(
            [bf / (2 * tf), B1 / t1, BF / TF],
            [0.3 * w, 0.55 * w, 0.6 * w])
        self.assertAlmostEqual(if_condition * bf / (B1 * tf), 0.6 / 0.55, 6)
        self.assertEqual(else_equal_TF, BF * tf / bf)
        self.assertAlmostEqual(if_equal_TF * B1 / (BF * t1), 0.55 / 0.6, 6)

    def test_2IPE_flang_plate_web_plate_beam_high_ductility_conditions_TW(self):
        if_condition, if_equal_TW, else_equal_TW = produce_conditions_from_slender_provision(
            [(d - 2 * (tf + r)) / tw, d / t2, (D - 2 * TF) / TW],
            [2.45 * w * (1 - 0.93 * Ca), 2.45 * w * (1 - 0.93 * Ca), 2.45 * w * (1 - 0.93 * Ca)], 'web')
        self.assertEqual(if_condition, (-d * tw / -(d - 2.0 * (tf + r))))
        self.assertEqual(if_equal_TW, (D - 2 * TF) * t2 / d)
        self.assertEqual(else_equal_TW, (-D + 2.0 * TF) * tw / (-d + 2.0 * (tf + r)))

    def test_2IPE_flang_plate_web_plate_beam_medium_ductility_conditions_TW(self):
        if_condition, if_equal_TW, else_equal_TW = produce_conditions_from_slender_provision(
            [(d - 2 * (tf + r)) / tw, d / t2, (D - 2 * TF) / TW],
            [2.45 * w * (1 - 0.93 * Ca), 2.45 * w * (1 - 0.93 * Ca), 2.45 * w * (1 - 0.93 * Ca)], 'web')
        self.assertEqual(if_condition, (-d * tw / -(d - 2.0 * (tf + r))))
        self.assertEqual(if_equal_TW, (D - 2 * TF) * t2 / d)
        self.assertEqual(else_equal_TW, (-D + 2.0 * TF) * tw / (-d + 2.0 * (tf + r)))

    def test_2IPE_flang_plate_web_plate_beam_medium_ductility_conditions_TF(self):

        if_condition, if_equal_TF, else_equal_TF = produce_conditions_from_slender_provision(
            [bf / (2 * tf), B1 / t1, BF / TF],
            [0.38 * w, 1.12 * w, 0.76 * w])
        self.assertAlmostEqual(if_condition * bf / (B1 * tf), 0.76 / 1.12, 6)
        self.assertEqual(else_equal_TF, BF * tf / bf)
        self.assertAlmostEqual(if_equal_TF * B1 / (BF * t1), 1.12 / 0.76, 6)


if __name__ == '__main__':
    unittest.main()
