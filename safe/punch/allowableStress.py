import math

pi = math.pi
alpha_ss = {'interier': 40, 'edge': 30, 'corner': 20}


def allowable_stress(bx, by, location, fc, b0, d, ACI2019=False, phi_c=.75):
    b0d = b0 * d
    beta = bx / by
    if beta < 1:
        beta = by / bx
    if ACI2019:
        lambda_s = min(math.sqrt(2 / (1 + .004 * d)), 1)
    else:
        lambda_s = 1
    alpha_s = alpha_ss[location]
    one_way_shear_capacity = math.sqrt(fc) * b0d / 6 * phi_c * lambda_s
    Vc1 = one_way_shear_capacity * 2
    Vc2 = one_way_shear_capacity * (1 + 2 / beta)
    Vc3 = one_way_shear_capacity * (2 + alpha_s * d / b0) / 2
    Vc = min(Vc1, Vc2, Vc3)
    vc = Vc / (b0d)
    return vc
