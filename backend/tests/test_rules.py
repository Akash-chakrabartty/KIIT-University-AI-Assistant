import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reasoning.rules import calculate_sgpa, check_eligibility


def test_calculate_sgpa_basic():
    courses = [{"credits": 4, "grade_points": 8}, {"credits": 3, "grade_points": 7}]
    # (4*8 + 3*7) / 7 = (32+21)/7 = 7.571...
    assert calculate_sgpa(courses) == 7.57


def test_calculate_sgpa_empty():
    assert calculate_sgpa([]) is None


def test_calculate_sgpa_zero_credits():
    assert calculate_sgpa([{"credits": 0, "grade_points": 8}]) is None


def test_check_eligibility_pass():
    rule = {"min_cgpa": 6.0, "max_backlogs": 2}
    assert check_eligibility(cgpa=6.5, backlogs=1, rule=rule) is True


def test_check_eligibility_fail_cgpa():
    rule = {"min_cgpa": 6.0, "max_backlogs": 2}
    assert check_eligibility(cgpa=5.9, backlogs=0, rule=rule) is False


def test_check_eligibility_fail_backlogs():
    rule = {"min_cgpa": 6.0, "max_backlogs": 2}
    assert check_eligibility(cgpa=8.0, backlogs=3, rule=rule) is False


def test_check_eligibility_boundary():
    rule = {"min_cgpa": 6.0, "max_backlogs": 2}
    assert check_eligibility(cgpa=6.0, backlogs=2, rule=rule) is True
