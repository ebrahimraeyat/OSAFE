import sys
from pathlib import Path

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches

punch_path = Path(__file__).absolute().parent
sys.path.insert(0, punch_path)
import punch_funcs
import Part

try:
	import FreeCAD
except:
	# path to FreeCAD.so
	FREECADPATH = '/usr/lib/freecad-daily-python3/lib/'
	sys.path.append(FREECADPATH)
	import FreeCAD


def add_edges_to_ax(obj, ax, linewidth=.5):
	for e in obj.Edges:
		if not len(e.Vertexes) == 2:
			continue
		v1, v2 = e.Vertexes
		xy = [[v1.X, v1.Y], [v2.X, v2.Y]]
		p = patches.Polygon(xy, edgecolor='black', linewidth=linewidth, closed=False)
		ax.add_patch(p)


def add_key_plan_edges_to_ax(punch, ax):
	# column = punch_funcs.rectangle_face(punch.center_of_load, punch.bx, punch.by)
	comp = Part.makeCompound([
			punch.foundation_plane,
			punch.edges,
			# column,
		])
	add_edges_to_ax(comp, ax, linewidth=.1)
	# add_edges_to_ax(column, ax, linewidth=.5)
	add_column_to_ax(punch, ax)
	set_ax_boundbox(comp, ax)
	return comp

def add_column_to_ax(punch, ax):
	xmin = punch.center_of_load.x - punch.bx / 2
	ymin = punch.center_of_load.y - punch.by / 2
	if FreeCAD.GuiUp:
		color = punch.ViewObject.ShapeColor[:-1]
	else:
		color = (.5, 0.5, 0.5)
	p = patches.Rectangle((xmin, ymin), punch.bx, punch.by, facecolor=color, edgecolor='black', linewidth=.3)
	ax.add_patch(p)


def add_punch_edges_to_ax(punch, ax):
	edges = punch.edges
	add_edges_to_ax(edges, ax, linewidth=.4)
	add_column_to_ax(punch, ax)
	set_ax_boundbox(edges, ax)
	# return comp

def set_ax_boundbox(shape, ax, scale=1, bb_add=50):
	b = shape.BoundBox
	xmin, ymin, xmax, ymax = b.XMin, b.YMin, b.XMax, b.YMax
	ax.set_xlim((xmin - bb_add) * scale, (xmax + bb_add) * scale)
	ax.set_ylim((ymin - bb_add) * scale, (ymax + bb_add) * scale)


def get_punch_picture(
		punch,
		filename='',
		) -> Path:
	fig = plt.figure(constrained_layout=True)
	widths = [2, 2, 2]
	heights = [2, 2, 1]
	gs = fig.add_gridspec(ncols=3, nrows=3, width_ratios=widths,
                          height_ratios=heights, left=0.05, right=0.48, wspace=0)
	ax1 = fig.add_subplot(gs[:-1, :], aspect='equal')
	plt.axis('off')
	add_punch_edges_to_ax(punch, ax1)
	ax2 = fig.add_subplot(gs[-1, 1], aspect='equal')
	plt.axis('off')
	add_key_plan_edges_to_ax(punch, ax2)
	import tempfile
	default_tmp_dir = tempfile._get_default_tempdir()
	if not filename:
		filename = next(tempfile._get_candidate_names())
	filename_path = Path(default_tmp_dir) / f'{filename}.jpg'
	fig.savefig(str(filename_path), orientation='portrait',
		# papertype='a4',
		bbox_inches='tight', dpi=600)
	return filename_path

def move_xy(xy, direction, dist=200):
	if direction in ('BOT', 'LEFT'):
		dist = -dist
	if direction in  ('TOP', 'BOT'):
		return (xy[0], xy[1] + dist)
	elif direction in ('LEFT', 'RIGHT'):
		return (xy[0] + dist, xy[1])


def annotate_dim(ax,xyfrom,xyto, direction='TOP', offset=200, text=None):
	'''
	direction: dimension arrow offset. can be: 'TOP', 'BOT', 'LEFT', 'RIGHT'
	'''
	xyfrom = move_xy(xyfrom, direction, offset)
	xyto = move_xy(xyto, direction, offset)
	if text is None:
		dist = np.sqrt((xyfrom[0]-xyto[0])**2 + (xyfrom[1]-xyto[1])**2)
		text = f'{dist: .0f}'
	ax.annotate("",xyfrom,xyto,arrowprops=dict(arrowstyle='<->'))
	ax.annotate("",xyfrom,xyto,arrowprops=dict(arrowstyle='|-|'))
	bbox=dict(fc="white", ec="none")
	ax.text((xyto[0]+xyfrom[0])/2,(xyto[1]+xyfrom[1])/2,text,fontsize=16, ha="center", va="center", bbox=bbox)

def export_dataframe_to_docx(df, doc=None):
	if not doc:
		import docx
		filepath = punch_path / 'Resources' / 'templates' / 'default.docx'
		doc = docx.Document(str(filepath))

	# add a table to the end and create a reference variable
	# extra row is so we can add the header row
	t = doc.add_table(df.shape[0]+1, df.shape[1], style='DATAFRAME')
	from docx.enum.table import WD_TABLE_ALIGNMENT
	t.alignment = WD_TABLE_ALIGNMENT.CENTER

	# add the header rows.
	for j in range(df.shape[-1]):
		cell = t.cell(0, j)
		cell.text = df.columns[j]
		# run = cell.paragraphs[0].runs[0]
		# run.font.bold = True

	# add the rest of the data frame
	for i in range(df.shape[0]):
		for j in range(df.shape[-1]):
			t.cell(i+1,j).text = str(df.values[i,j])
	# doc.save(str(filepath))

	return doc

def add_punch_ratios_to_doc(punch, doc=None):
	import pandas as pd
	df = pd.DataFrame(list(punch.combos_ratio.items()), columns=['Combo', 'Ratio'])
	doc = export_dataframe_to_docx(df, doc)
	return doc

def create_report(
				punch,
				filename: str,
				):
	image_file_path = get_punch_picture(punch)
	import docx
	filepath = punch_path / 'Resources' / 'templates' / 'default.docx'
	doc = docx.Document(str(filepath))
	doc.add_picture(str(image_file_path))
	doc = add_punch_ratios_to_doc(punch, doc)
	doc.save(filename)
	return doc
