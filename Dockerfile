# ============================================================
# AI-Generated Dockerfile
# Language: python | Framework: flask
# Builder: python:3.11-slim → Runtime: python:3.11-slim
# ============================================================

FROM python:3.11-slim AS builder
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /usr/src/app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY --from=builder /install /usr/local
COPY . .
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:5000/health || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
