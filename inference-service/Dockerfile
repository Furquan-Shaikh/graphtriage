FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# Install CPU-only PyTorch FIRST, from PyTorch's own CPU wheel index.
# Without this, pip installs the default Linux wheel, which bundles ~2GB+
# of NVIDIA CUDA libraries we don't need (no GPU in this setup) - that
# caused a download timeout during `docker compose up --build`.
# Once this is installed, sentence-transformers/torch_geometric below will
# reuse this CPU build instead of pulling the CUDA one.
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Sentence-BERT model at build time, not on the first request -
# avoids a slow/timeout-prone download happening during a live API call.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
