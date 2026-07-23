"""The affiliation policy is a rules-of-engagement decision: below the
confidence floor the gateway must refuse to assert friend/hostile. These
tests make that refusal explicit and enforced."""
from cot_gateway import config
from cot_gateway.affiliation import affiliation_for, cot_type_for


def test_confident_detections_map_by_class():
    assert affiliation_for("drone", 0.95) == "h"
    assert affiliation_for("friendly_vehicle", 0.95) == "f"
    assert affiliation_for("person", 0.95) == "u"


def test_low_confidence_degrades_to_unknown():
    # Even a class mapped hostile must NOT render hostile below the floor.
    below = config.CONFIDENCE_FLOOR - 0.01
    assert affiliation_for("drone", below) == "u"
    assert affiliation_for("friendly_vehicle", below) == "u"


def test_unknown_class_defaults_to_unknown():
    assert affiliation_for("garbage_truck", 0.99) == "u"


def test_cot_type_is_well_formed():
    assert cot_type_for("drone", 0.95) == "a-h-G"
    assert cot_type_for("drone", 0.10) == "a-u-G"
