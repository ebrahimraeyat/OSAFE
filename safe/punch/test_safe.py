from safe import Safe
import unittest


class TestSafe(unittest.TestCase):
	def setUp(self):
		self.safe = Safe("test_files/sattari_safe.xlsx")

	def test_program_control(self):
		self.assertEqual(self.safe.program_name, "SAFE 2016")
		self.assertEqual(self.safe.version, "16.0.1")
		self.assertEqual(self.safe.curr_units.force, "N")
		self.assertEqual(self.safe.curr_units.length, " mm")
		self.assertEqual(self.safe.curr_units.temp, " C")
		self.assertEqual(self.safe.concrete_code, "ACI 318-14")

	def test_obj_geom_points(self):
		points = self.safe.obj_geom_points
		no_of_points = len(list(points.keys()))
		coord = points[29]
		self.assertEqual(no_of_points, 84)
		self.assertEqual(coord.x, 0)
		self.assertEqual(coord.y, 5.1)
		self.assertEqual(coord.z, 0)
		self.assertEqual(coord.special, True)

		coord = points[72]
		self.assertAlmostEqual(coord.x, 4.46, places=2)
		self.assertAlmostEqual(coord.y, 11.034, places=3)
		self.assertEqual(coord.z, 0)
		self.assertEqual(coord.special, False)

	def test_obj_geom_areas(self):
		areas = self.safe.obj_geom_areas
		no_of_areas = len(list(areas.keys()))
		self.assertEqual(no_of_areas, 6)
		point_numbers = areas[11]
		self.assertEqual(point_numbers, [76, 75, 73, 72])

		stiff = self.safe.obj_geom_stiff
		point_numbers = stiff[20]
		self.assertEqual(point_numbers, [112, 113, 114, 115])

	def test_point_loads(self):
		point_loads = self.safe.point_loads
		self.assertEqual(len(point_loads), 10)
		no_of_loads = len(list(point_loads[29]['loads'].keys()))
		self.assertEqual(no_of_loads, 27)
		#  point 29
		load = point_loads[29]['loads']['Dead_ABOVE']
		self.assertAlmostEqual(load.fx, -6.667899, places=5)
		self.assertAlmostEqual(load.fy, -8.647991, places=5)
		self.assertAlmostEqual(load.fz, 284.2031, places=4)
		self.assertAlmostEqual(load.mx, 9.956049, places=5)
		self.assertAlmostEqual(load.my, -7.921433, places=5)
		self.assertAlmostEqual(load.mz, 0.004490824, places=9)
		self.assertEqual(point_loads[29]['xdim'], 400)
		self.assertEqual(point_loads[29]['ydim'], 400)
		#  point 49 EYALL-0.3EX(3/3)_ABOVE load
		load = point_loads[49]['loads']['EYALL-0.3EX(3/3)_ABOVE']
		self.assertAlmostEqual(load.fx, -9.586596, places=5)
		self.assertAlmostEqual(load.fy, 37.83184, places=5)
		self.assertAlmostEqual(load.fz, 62.41515, places=5)
		self.assertAlmostEqual(load.mx, -113.0372, places=4)
		self.assertAlmostEqual(load.my, -31.61491, places=5)
		self.assertAlmostEqual(load.mz, 0.3031819, places=7)
		self.assertEqual(point_loads[49]['xdim'], 400)
		self.assertEqual(point_loads[49]['ydim'], 400)

class TestSafe_safdari(unittest.TestCase):
	def setUp(self):
		self.safe = Safe("test_files/safdari.xlsx")

	def test_solid_slabs(self):
		solid_slabs = self.safe.solid_slabs
		slab_prop = solid_slabs['COL']
		self.assertEqual(slab_prop.type, 'Stiff')
		self.assertEqual(slab_prop.matProp, 'C35')
		self.assertEqual(slab_prop.thickness, 3000)

	def test_slab_prop_assignment(self):
		slab_prop_assignment = self.safe.slab_prop_assignment
		self.assertEqual(slab_prop_assignment[9], 'SLAB70')
		self.assertEqual(slab_prop_assignment[31], 'COL')
		self.assertEqual(slab_prop_assignment[56], 'SLAB55')

	def test_concrete_mat(self):
		concrete_mat = self.safe.concrete_mat
		self.assertAlmostEqual(concrete_mat['C35'], 3.56900667277847, places=10)

class TestSafe_safdari(unittest.TestCase):
	def setUp(self):
		self.safe = Safe("test_files/davoodabadi_dynamic.xlsx")

	def test_obj_geom_all_areas(self):
		areas = self.safe.obj_geom_areas
		no_of_areas = len(list(areas.keys()))
		self.assertEqual(no_of_areas, 8)
		point_numbers = areas[12]
		self.assertEqual(point_numbers, [257, 256, 255, 254, 253])

		point_numbers = areas[11]
		self.assertEqual(point_numbers, [252, 251, 250, 249])

		point_numbers = areas[106]
		self.assertEqual(point_numbers, [465, 4, 461, 25, 462, 463, 464, 427, 428])


	def test_grid_lines(self):
		pass
		# grid_lines = self.safe.grid_lines()
		# no_of_x_grid_line = len(grid_lines['x'])
		# no_of_y_grid_line = len(grid_lines['y'])
		# self.assertEqual(no_of_x_grid_line, 5)
		# self.assertEqual(no_of_y_grid_line, 4)

	def test_load_cases(self):
		pass

	def test_load_combinations(self):
		pass

	def test_punching_shear(self):
		pass

	def test_slab_prop(self):
		pass

	def soil_prop(self):
		pass

	