#!/usr/bin/env python3
"""Reverse proxy for 讯飞 Coding Plan → New API compatibility.

Maps:
  /v1/*        → 讯飞 OpenAI protocol /v2/*
  /anthropic/* → 讯飞 Anthropic protocol /anthropic/*
Also maps model names: glm-5.1 → astron-code-latest
"""
import asyncio
import aiohttp
from aiohttp import web
import json

UPSTREAM_OPENAI = "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
UPSTREAM_ANTHROPIC = "https://maas-coding-api.cn-huabei-1.xf-yun.com/anthropic"
PORT = 3001

# Model name mapping
MODEL_MAP = {
    "glm-5.1": "astron-code-latest",
}

def map_model_in_body(body: bytes) -> bytes:
    """Replace model names in request body."""
    if not body:
        return body
    try:
        data = json.loads(body)
        if "model" in data and data["model"] in MODEL_MAP:
            data["model"] = MODEL_MAP[data["model"]]
            return json.dumps(data).encode()
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return body

# Reverse model map for response body
REVERSE_MODEL_MAP = {v: k for k, v in MODEL_MAP.items()}

def unmap_model_in_response(body: bytes) -> bytes:
    """Replace upstream model names back to user-facing names in response body."""
    if not body:
        return body
    try:
        data = json.loads(body)
        if "model" in data and data["model"] in REVERSE_MODEL_MAP:
            data["model"] = REVERSE_MODEL_MAP[data["model"]]
            return json.dumps(data).encode()
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return body

def unmap_model_in_stream(chunk: bytes) -> bytes:
    """Replace model names in SSE stream chunks."""
    if not chunk:
        return chunk
    try:
        text = chunk.decode('utf-8', errors='replace')
        for upstream, facing in REVERSE_MODEL_MAP.items():
            text = text.replace(f'"model":"{upstream}"', f'"model":"{facing}"')
            text = text.replace(f'"model": "{upstream}"', f'"model": "{facing}"')
        return text.encode('utf-8')
    except Exception:
        return chunk

async def proxy_handler(request: web.Request):
    path = request.path
    
    if path.startswith("/v1/"):
        upstream_path = path.replace("/v1/", "/", 1)
        upstream_url = UPSTREAM_OPENAI + upstream_path
    elif path.startswith("/anthropic/"):
        upstream_path = path.replace("/anthropic/", "/", 1)
        upstream_url = UPSTREAM_ANTHROPIC + upstream_path
    elif path == "/v1":
        upstream_url = UPSTREAM_OPENAI + "/"
    elif path == "/anthropic":
        upstream_url = UPSTREAM_ANTHROPIC + "/"
    else:
        return web.Response(status=404, text="Not found")
    
    # Forward headers
    headers = {}
    for key in ['Authorization', 'x-api-key', 'Content-Type', 'Accept',
                'anthropic-version', 'anthropic-beta', 'anthropic-dangerous-direct-browser-access']:
        val = request.headers.get(key)
        if val:
            headers[key] = val
    
    # Read and map body
    body = await request.read()
    body = map_model_in_body(body)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                request.method,
                upstream_url,
                headers=headers,
                data=body,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                resp_headers = {}
                for key, val in resp.headers.items():
                    if key.lower() not in ('transfer-encoding', 'connection', 'content-encoding', 'content-length'):
                        resp_headers[key] = val
                
                if resp.content_type == 'text/event-stream':
                    # Streaming response - process each chunk
                    response = web.StreamResponse(
                        status=resp.status,
                        headers=resp_headers,
                    )
                    await response.prepare(request)
                    async for chunk in resp.content.iter_any():
                        chunk = unmap_model_in_stream(chunk)
                        await response.write(chunk)
                    await response.write_eof()
                    return response
                else:
                    # Non-streaming response
                    resp_body = await resp.read()
                    resp_body = unmap_model_in_response(resp_body)
                    
                    return web.Response(
                        status=resp.status,
                        headers=resp_headers,
                        body=resp_body
                    )
    except Exception as e:
        return web.Response(
            status=502,
            content_type='application/json',
            text=json.dumps({"error": {"message": f"proxy error: {e}"}})
        )

async def main():
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', proxy_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"Xfyun reverse proxy on 0.0.0.0:{PORT}")
    print(f"  /v1/*        → {UPSTREAM_OPENAI}/*")
    print(f"  /anthropic/* → {UPSTREAM_ANTHROPIC}/*")
    print(f"  Model map: {MODEL_MAP}")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
