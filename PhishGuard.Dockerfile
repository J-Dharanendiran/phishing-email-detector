FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    API_BASE_URL=http://127.0.0.1:8000

WORKDIR /app

# Install all dependencies from the root requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY frontend/ ./frontend/

EXPOSE 8000 8501

# Start FastAPI and Streamlit
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & API_PID=$!; streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8501; STATUS=$?; kill $API_PID 2>/dev/null || true; exit $STATUS"]