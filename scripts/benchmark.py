#!/usr/bin/env python3
"""
Benchmark de Concurrencia para Servidores de Inferencia LLM
Compara comportamiento ante ráfagas concurrentes de peticiones.
"""

import asyncio
import time
import aiohttp
import statistics
import argparse

PROMPT = "Explica en tres párrafos técnicos qué es la memoria virtual y cómo se gestionan las páginas de memoria en el kernel de Linux."

async def send_request(session, url, model, headers, req_id):
    # Envia una peticion individual y mide su latencia
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    start_time = time.perf_counter()
    try:
        async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            data = await resp.json()
            latency = time.perf_counter() - start_time
            if resp.status == 200:
                tokens = data["usage"]["completion_tokens"]
                return {"id": req_id, "success": True, "latency": latency, "tokens": tokens}
            else:
                return {"id": req_id, "success": False, "latency": latency, "error": resp.status}
    except Exception as e:
        latency = time.perf_counter() - start_time
        return {"id": req_id, "success": False, "latency": latency, "error": str(e)}

async def run_benchmark(url, model, concurrency, auth_header):
    # Ejecuta peticiones concurrentes y calcula metricas
    headers = {"Content-Type": "application/json"}
    if auth_header:
        headers["Authorization"] = f"Bearer {auth_header}"

    print("\n=======================================================")
    print(f"Iniciando Benchmark: {concurrency} peticiones CONCURRENTES")
    print(f"Target: {url} | Modelo: {model}")
    print("=======================================================")

    async with aiohttp.ClientSession() as session:
        t0 = time.perf_counter()
        tasks = [send_request(session, url, model, headers, i) for i in range(concurrency)]
        results = await asyncio.gather(*tasks)
        total_wall_time = time.perf_counter() - t0

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    if successful:
        latencies = [r["latency"] for r in successful]
        total_tokens = sum(r["tokens"] for r in successful)
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        throughput_tokens_sec = total_tokens / total_wall_time

        print("\nRESULTADOS:")
        print(f" - Peticiones exitosas: {len(successful)}/{concurrency}")
        print(f" - Fallidas / Timeout:  {len(failed)}")
        print(f" - Tiempo total del test: {total_wall_time:.2f} s")
        print(f" - Throughput global:     {throughput_tokens_sec:.2f} tokens/segundo")
        print(f" - Latencia promedio:     {avg_latency:.2f} s")
        print(f" - Latencia P95:          {p95_latency:.2f} s")
    else:
        print(f"\nTodas las peticiones fallaron. Errores: {[r.get('error') for r in failed]}")

if __name__ == "__main__":
    # Parser de argumentos por linea de comandos
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:4000/v1/chat/completions", help="Endpoint OpenAI-compatible")
    parser.add_argument("--model", default="production-model", help="Nombre del modelo")
    parser.add_argument("--concurrency", type=int, default=20, help="Numero de peticiones concurrentes")
    parser.add_argument("--key", default="sk-production-admin-key", help="API Key si aplica")
    args = parser.parse_args()

    asyncio.run(run_benchmark(args.url, args.model, args.concurrency, args.key))
