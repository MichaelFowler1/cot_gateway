"""Map a detection's class_name + confidence to a CoT affiliation/type.

CoT 'type' encodes affiliation as the second atom: a-f-* friendly,
a-h-* hostile, a-u-* unknown. We keep this in one place so the policy is
easy to audit and tune.
"""

from . import config

# class_name -> affiliation atom ("f" friendly, "h" hostile, "u" unknown).
# These seeds are ILLUSTRATIVE — tune them to your detector's label set and
# your ROE. Anything not listed defaults to unknown.
CLASS_AFFILIATION = {
    "friendly_vehicle": "f",
    "soldier_friendly": "f",
    "person": "u",
    "civilian": "u",
    "vehicle": "u",
    "drone": "h",
    "technical": "h",
    "soldier_hostile": "h",
}

DEFAULT_AFFILIATION = "u"


def affiliation_for(class_name: str, confidence: float) -> str:
    """Return the affiliation atom for a detection.

    Below CONFIDENCE_FLOOR we don't trust the label enough to assert
    friend/hostile, so we degrade to unknown.
    """
    if confidence < config.CONFIDENCE_FLOOR:
        return "u"
    return CLASS_AFFILIATION.get(class_name, DEFAULT_AFFILIATION)


def cot_type_for(class_name: str, confidence: float) -> str:
    """Return a full CoT type string, e.g. 'a-h-G'.

    '-G' is the generic ground battle-dimension — a sane v1 default. Richer
    MIL-STD-2525 typing (air/sea, specific functions) is a later concern.
    """
    return f"a-{affiliation_for(class_name, confidence)}-G"
