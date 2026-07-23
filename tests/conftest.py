import os
import sys

# The repo root IS the cot_gateway package (it has __init__.py and uses
# relative imports), so tests import it by putting the repo's PARENT on
# sys.path — mirroring how `python -m cot_gateway.main` is run.
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)
