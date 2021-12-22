import sympy
from sympy.solvers import solve
bf, tf, d, tw, BF, TF, D, TW, B1, t1, t2, w, Ca, r = sympy.symbols('bf tf d tw BF TF D TW B1 t1 t2 w Ca r')


def produce_conditions_from_slender_provision(conditions_left, conditions_right, slender_case='flang'):

    left_section_conditions = conditions_left[:-1]
    left_equal_section_condition = conditions_left[-1]
    right_section_conditions = conditions_right[:-1]
    right_equal_section_condition = conditions_right[-1]

    plate_thikness = t1
    equal_thikness = TF

    if slender_case == 'web':
        plate_thikness = t2
        equal_thikness = TW

    new_left_section_conditions = []
    # now we produce same right conditions to compare left side
    for i, condition in enumerate(left_section_conditions):
        new_condition = condition * float(right_equal_section_condition / right_section_conditions[i])
        new_left_section_conditions.append(new_condition)
    if_condition = solve(new_left_section_conditions[1] - new_left_section_conditions[0], plate_thikness)
    if_equal_thikness = solve(left_equal_section_condition - new_left_section_conditions[1], equal_thikness)
    else_equal_thikness = solve(left_equal_section_condition - new_left_section_conditions[0], equal_thikness)
    return if_condition[0], if_equal_thikness[0], else_equal_thikness[0]
