# cot_gateway as a container: point it at a TAK server with COT_URL.
#
#   docker build -t cot-gateway .
#   docker run --rm -e COT_URL=tcp://takserver:8087 cot-gateway
#
# All tuning (STALE_SECONDS, CONFIDENCE_FLOOR, FAKE_*) is env-overridable,
# so the same image runs a demo feed or a real detector integration.
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pytak

# The repo root is the package; give it its package name inside the image so
# `python -m cot_gateway.main` resolves the relative imports.
COPY __init__.py affiliation.py config.py cot.py fakegen.py main.py \
     selfcheck.py worker.py /app/cot_gateway/

# Default: plaintext CoT to a FreeTAKServer on the docker network.
ENV COT_URL=tcp://127.0.0.1:8087

CMD ["python", "-m", "cot_gateway.main"]
