FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install project dependencies when a requirements file is present.
COPY . .
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi \
    && pip install streamlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"

# Prefer common Streamlit entrypoint names; otherwise use the first Python
# file found near the project root. Set APP_FILE at runtime to override.
CMD ["sh", "-c", "APP=\"${APP_FILE:-}\"; if [ -z \"$APP\" ]; then for f in app.py streamlit_app.py main.py Home.py; do if [ -f \"$f\" ]; then APP=\"$f\"; break; fi; done; fi; if [ -z \"$APP\" ]; then APP=$(find . -maxdepth 2 -type f -name '*.py' ! -path './.venv/*' ! -path './venv/*' | sort | head -n 1); fi; if [ -z \"$APP\" ]; then echo 'ERROR: No Streamlit entrypoint found. Set APP_FILE to the correct Python file.'; exit 1; fi; exec streamlit run \"$APP\" --server.port=\"${PORT:-8501}\" --server.address=0.0.0.0"]
