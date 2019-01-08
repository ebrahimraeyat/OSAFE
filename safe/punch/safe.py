from collections import namedtuple
import pandas as pd
import numpy as np


class Safe:
	__bool = {'Yes': True, 'No': False}

	def __init__(self, filename):
		self.filename = filename
		self.excel = None
		self.access = None
		self.read_file()
		self.read_sheets_informations()
		self.load_combinations = self.read_load_combinations()
		self.points_loads = self.read_point_loads()
		self.points_loads_combinations = self.apply_loads_combinations_to_points(
            	self.load_combinations, self.points_loads)

	def __str__(self):
		s = ''
		if not self.version:
			return s
		s += f"{self.program_name} ver '{self.version}'\n"
		s += f'Code : {self.concrete_code}\n'
		s += f"No. of Columns = {len(self.points_loads['Point'].unique())}\n"
		s += f"No. of Load Combinations = {len(self.load_combinations['Combo'].unique())}"
		return s

	def read_file(self):
		if self.filename.endswith((".xls", ".xlsx")):
			self.excel = pd.read_excel(self.filename, sheetname=None, skiprows=[0,2])
		elif self.filename.endswith((".mdb", ".accdb")):
			#TODO
			pass

	def read_sheets_informations(self):
		self.program_control()
		self.solid_slabs = self.solid_slabs()
		self.slab_prop_assignment = self.slab_prop_assignment()
		self.obj_geom_points = self.obj_geom_points()
		all_areas = self.obj_geom_all_areas()
		self.obj_geom_areas = all_areas[0]
		self.obj_geom_stiff = all_areas[1]
		self.point_loads = self.point_loads()
		self.concrete_mat = self.concrete_mat()

	def program_control(self):
		if self.excel is not None:
			program_control = self.excel["Program Control"]
		elif self.access:
			# TODO
			pass

		self.program_name = program_control["ProgramName"][0]
		self.version = program_control["Version"][0]
		UNITS = namedtuple("UNITS", 'force length temp')
		curr_units = program_control["CurrUnits"][0].split(",")
		self.curr_units = UNITS._make(curr_units)
		self.concrete_code = program_control["ConcCode"][0]

	def obj_geom_points(self):
		obj_geom_points = self.excel['Obj Geom - Point Coordinates']
		POINTS = namedtuple("POINTS", 'x y z special')
		point_props = {}
		for _, row in obj_geom_points.iterrows():
			_id = row['Point']
			x = row['GlobalX']
			y = row['GlobalY']
			z = row['GlobalZ']
			special = self.__bool[row['SpecialPt']]
			curr_points = (x, y, z, special)
			point_props[_id] = POINTS._make(curr_points)
		return point_props

	def obj_geom_all_areas(self):
		stiff = []
		for key, value in self.solid_slabs.items():
			if value.type == 'Stiff':
				stiff.append(key)
		# find stiff areas according to stiff assignment names
		stiff_areas = []
		for key, value in self.slab_prop_assignment.items():
			if value in stiff:
				stiff_areas.append(key)

		obj_geom_areas = self.excel['Obj Geom - Areas 01 - General']
		areas_prop = {}
		stiff_prop = {}
		all_areas = []
		for _, row in obj_geom_areas.iterrows():
			_id = row['Area']
			if not _id in all_areas:
				all_areas.append(_id)
				points = []
			for i in range(4):
				point = row['Point' + str(i+1)]
				try:
					point = int(point)
				except:
					continue
				points.append(point)
			if _id in stiff_areas:
				stiff_prop[_id] = points
			else:
				areas_prop[_id] = points
		return areas_prop, stiff_prop

	def point_loads(self):
		point_loads_sheet = self.excel["Load Assignments - Point Loads"]
		POINTLOADS = namedtuple("POINTLOADS", 'fx fy fz mx my mz')
		point_ids = point_loads_sheet['Point'].unique()
		point_loads = {_id: {'xdim': 0, 'ydim': 0, 'loads': {}} for _id in point_ids}
		load_pats = point_loads_sheet['LoadPat'].unique()
		for _, row in point_loads_sheet.iterrows():
			_id = row['Point']
			load_pat = row['LoadPat']
			fx = row['Fx']
			fy = row['Fy']
			fz = row['Fgrav']
			mx = row['Mx']
			my = row['My']
			mz = row['Mz']
			curr_loads = (fx, fy, fz, mx, my, mz)
			xdim = row['XDim']
			ydim = row['YDim']
			point_loads[_id]['loads'][load_pat] = POINTLOADS._make(curr_loads)
			point_loads[_id]['xdim'] = xdim
			point_loads[_id]['ydim'] = ydim
		return point_loads

	def solid_slabs(self):
		solid_slabs_sheet = self.excel['Slab Prop 02 - Solid Slabs']
		SOLIDSLABS = namedtuple("SOLIDSLABS", 'type matProp thickness')
		solid_slabs = {}
		for _, row in solid_slabs_sheet.iterrows():
			name = row['Slab']
			_type = row['Type']
			matProp = row['MatProp']
			thickness = row['Thickness']
			solid_slabs[name] = SOLIDSLABS._make((_type, matProp, thickness))
		return solid_slabs

	def slab_prop_assignment(self):
		slab_prop_assignment_sheet = self.excel['Slab Property Assignments']
		slab_prop_assignment = {}
		for _, row in slab_prop_assignment_sheet.iterrows():
			slab_prop_assignment[row['Area']] = row['SlabProp']
		return slab_prop_assignment

	def get_thickness(self, areas):
		areas_thickness = {}
		for key, area in areas.items():
			slab_prop_assign = self.slab_prop_assignment[key]
			try:
				slab_prop = self.solid_slabs[slab_prop_assign]
				thickness = slab_prop.thickness
			except: thickness = 5001
			areas_thickness[key] = thickness
		d_list = list(areas_thickness.values())
		d_list = [d for d in d_list if d < 5000]
		self.max_thickness = max(d_list)
		return areas_thickness

	def concrete_mat(self):
		concrete_mat_sheet = self.excel['Material Prop 03 - Concrete']
		concrete_mat = {}
		for _, row in concrete_mat_sheet.iterrows():
			concrete_mat[row['Material']] = row['Fc']
		return concrete_mat

	def grid_lines(self):
		grid_lines_sheet = self.excel['Grid Lines']
		grid_lines = {'x': {}, 'y': {}}
		for _, row in grid_lines_sheet.iterrows():
			_dir = row['AxisDir'].lower()
			_id = row['GridID']
			ordinate = row['Ordinate']
			grid_lines[_dir][_id] = ordinate
		return grid_lines

	def read_load_combinations(self):
		df = self.excel['Load Combinations']
		combos_sr = df[df['DSStrength'] == 'Yes']['Combo']
		combos_df = df[df['Combo'].isin(combos_sr)]
		return combos_df[['Combo','Load','SF']]

	def read_point_loads(self):
		df = self.excel['Load Assignments - Point Loads']
		df['LoadPat'] = df['LoadPat'].str.rstrip('_ABOVE')
		return df[['Point', 'LoadPat', 'Fgrav', 'Mx', 'My']]

	def apply_loads_combinations_to_points(self, combos_df, point_load_df):
		points = point_load_df['Point'].unique()
		combos_sr = combos_df['Combo'].unique()
		points_combos_loads = pd.DataFrame(columns=['Point', 'Combo', 'Fgrav', 'Mx', 'My'])
		index = 0
		for p in points:
		    point = (point_load_df[point_load_df['Point'] == p][['LoadPat','Fgrav', 'Mx', 'My']]
		             .set_index('LoadPat')
		            )
		    for combo in combos_sr:
		        udcon = (combos_df[combos_df['Combo'] == combo]
		                 .set_index('Load')
		                )
		        load = list(point.mul(udcon['SF'], axis=0).sum())
		        points_combos_loads.loc[index] = [p, combo] + load
		        index += 1
		return points_combos_loads

if __name__ == '__main__':
	safe = Safe("sattari_safe.xlsx")
	safe.program_control()




