# vLLM Production Stack: Concurrency, Resilience & Telemetry

Production-grade LLM inference deployment featuring **vLLM** (PagedAttention & Continuous Batching), **LiteLLM Gateway** (circuit breakers & fallbacks), and full observability via **Prometheus** and **Grafana**.

Read the full technical breakdown on my blog: [De Ollama a Producción: Desplegando vLLM con PagedAttention y métricas en tiempo real](https://blog.jrodriiguezg.link)

---

## Architecture

- **Engine:** [vLLM](https://github.com/vllm-project/vllm) with AWQ quantization (`Qwen/Qwen2.5-3B-Instruct-AWQ`), PagedAttention, and Continuous Batching.
- **Gateway & Resilience:** [LiteLLM Proxy](https://github.com/BerriAI/litellm) providing OpenAI-compatible routing, timeouts, and silent failover.
- **Metrics Scraper:** [Prometheus](https://prometheus.io/) scraping the native `/metrics` endpoint every 2s.
- **Dashboards:** [Grafana](https://grafana.com/) for real-time visualization of TTFT, TPOT, and KV Cache utilization.

---

## Quick Start

### 1. Prerequisites
- Linux OS (Fedora / RHEL / Debian)
- NVIDIA GPU with proprietary drivers (`nvidia-smi`)
- Docker Engine & NVIDIA Container Toolkit (`nvidia-ctk`)

### 2. Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```

### 3. Launch the Stack
```bash
docker compose up -d
```

Check logs and health status:
```bash
docker compose logs -f vllm
curl http://localhost:8000/health
```

---

## Load & Concurrency Benchmark

Stress-test the deployment with the included asynchronous Python benchmark:

```bash
pip install -r scripts/requirements.txt

# Run 20 concurrent requests against vLLM
python3 scripts/benchmark.py --concurrency 20 --url http://localhost:4000/v1/chat/completions --model production-model
```

---

## Service Endpoints

| Service | Port | Description |
| :--- | :--- | :--- |
| **LiteLLM Gateway** | `http://localhost:4000` | OpenAI-compatible endpoint with circuit breaker |
| **vLLM Engine** | `http://localhost:8000` | Raw inference API & `/metrics` |
| **Prometheus** | `http://localhost:9090` | Telemetry scraper & PromQL console |
| **Grafana** | `http://localhost:3000` | Dashboards (`admin` / `admin`) |
