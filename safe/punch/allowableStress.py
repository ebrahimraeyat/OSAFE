import math

pi = math.pi
alpha_ss = {'interier':40, 'edge':30, 'corner':20}


def allowable_stress(bx, by, location, fc, b0d=None,b0=None, d=None, phi_c=.75):
	beta = bx / by
	if beta < 1:
		beta = by / bx
	alpha_s = alpha_ss[location]
	one_way_shear_capacity = math.sqrt(fc) * b0d / 6  * phi_c
	Vc1 = one_way_shear_capacity * 2
	Vc2 = one_way_shear_capacity * (1 + 2 / beta)
	# Vc3 = one_way_shear_capacity * (2 + alpha_s * d / b0) / 2
	Vc = min(Vc1, Vc2)
	vc = Vc / (b0d)
	return vc


