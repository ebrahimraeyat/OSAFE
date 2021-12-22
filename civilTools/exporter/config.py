import json

def save(widget, json_file):
	d = {}
	d['ostan'] = widget.ostanBox.currentText()
	d['shahr'] = widget.shahrBox.currentText()
	d['soil_type'] = widget.soilType.currentText()
	d['importance_factor'] = widget.IBox.currentText()
	d['height'] = widget.HSpinBox.value()
	d['no_of_story'] = widget.storySpinBox.value()
	d['t_an_x'] = widget.xTAnalaticalSpinBox.value()
	d['t_an_y'] = widget.yTAnalaticalSpinBox.value()
	d['infill'] = widget.infillCheckBox.isChecked()
	d['x_system'] = find_selected_item_in_treewidget(widget.x_treeWidget)
	d['y_system'] = find_selected_item_in_treewidget(widget.y_treeWidget)
	with open(json_file, 'w') as f:
		json.dump(d, f)

def load(widget, json_file):
	with open(json_file, 'r') as f:
		d = json.load(f)

	index = widget.ostanBox.findText(d['ostan'])
	widget.ostanBox.setCurrentIndex(index)
	index = widget.shahrBox.findText(d['shahr'])
	widget.shahrBox.setCurrentIndex(index)
	index = widget.soilType.findText(d['soil_type'])
	widget.soilType.setCurrentIndex(index)
	index = widget.IBox.findText(d['importance_factor'])
	widget.IBox.setCurrentIndex(index)
	widget.HSpinBox.setValue(d['height'])
	widget.storySpinBox.setValue(d['no_of_story'])
	widget.xTAnalaticalSpinBox.setValue(d['t_an_x'])
	widget.yTAnalaticalSpinBox.setValue(d['t_an_y'])
	widget.infillCheckBox.setChecked(d['infill'])
	x_item = d.get('x_system', None)
	y_item = d.get('y_system', None)
	if x_item and y_item:
		select_treewidget_item(widget.x_treeWidget, *x_item)
		select_treewidget_item(widget.y_treeWidget, *y_item)

def find_selected_item_in_treewidget(treewidget):
	root_item = treewidget.invisibleRootItem()
	top_level_count = root_item.childCount()

	for i in range(top_level_count):
		top_level_item = root_item.child(i)
		child_num = top_level_item.childCount()
		for n in range(child_num):
			child_item = top_level_item.child(n)
			if child_item.isSelected():
				return i, n

def select_treewidget_item(treewidget, i, n):
	if i is None:
		return
	cur_i, cur_n = find_selected_item_in_treewidget(treewidget)
	root_item = treewidget.invisibleRootItem()
	if cur_i == i and cur_n == n:
		return
	else:
		root_item.child(cur_i).child(cur_n).setSelected(False)
		root_item.child(cur_i).setExpanded(False)
		root_item.child(i).child(n).setSelected(True)
		root_item.child(i).setExpanded(True)
