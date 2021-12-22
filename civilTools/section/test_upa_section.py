import unittest

from .sec import *


class TestUpaSections(unittest.TestCase):

    def setUp(self):

        UPA = Upa.createStandardUpas()
        self.__ductility = "M"
        self.__useAs = "C"
        self.UPA08 = UPA[8]
        self.UPA08.ductility = self.__ductility
        self.UPA08.useAs = self.__useAs
        self.UPA08_double = DoubleSection(self.UPA08, 10)

    def test_UPA08_Iy(self):
        self.assertAlmostEqual(self.UPA08.Iy, 128000, places=1)
        self.assertAlmostEqual(self.UPA08_double.Iy, 2083627.559, places=1)
