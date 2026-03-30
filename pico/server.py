import asyncio
import json

from config import CORS_ALLOW_ORIGIN, HTTP_PORT

latest_usage = {
    "five_hour_utilization": 0,
    "seven_day_utilization": 0,
}


def _cors_headers():
    return (
        f"Access-Control-Allow-Origin: {CORS_ALLOW_ORIGIN}\r\n"
        "Access-Control-Allow-Methods: POST, OPTIONS, GET\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n"
        "Access-Control-Max-Age: 86400\r\n"
    )


def _response(status_line, body=b"", content_type="text/plain; charset=utf-8", extra_headers=""):
    headers = (
        f"{status_line}\r\n"
        "Connection: close\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"{extra_headers}"
        "\r\n"
    )
    return headers.encode("utf-8") + body


async def _read_body(reader, n):
    out = b""
    while len(out) < n:
        chunk = await reader.read(n - len(out))
        if not chunk:
            break
        out += chunk
    return out


async def _read_headers(reader):
    headers = {}
    while True:
        line = await reader.readline()
        if not line:
            break
        line = line.rstrip(b"\r\n")
        if not line:
            break
        if b":" in line:
            name, value = line.split(b":", 1)
            headers[name.decode("utf-8").lower().strip()] = value.decode("utf-8").strip()
    return headers


def _parse_request_line(line):
    parts = line.decode("utf-8").strip().split()
    if len(parts) < 2:
        return None, None
    method = parts[0].upper()
    path = parts[1]
    if "?" in path:
        path = path.split("?", 1)[0]
    return method, path


async def _handle_client(reader, writer):
    try:
        first = await reader.readline()
        if not first:
            return
        method, path = _parse_request_line(first)
        if method is None:
            writer.write(_response("HTTP/1.1 400 Bad Request", b"Bad request"))
            await writer.drain()
            return

        headers = await _read_headers(reader)
        body = b""

        if method == "POST":
            cl = headers.get("content-length")
            if cl is None:
                writer.write(
                    _response(
                        "HTTP/1.1 411 Length Required",
                        b"Content-Length required",
                        extra_headers=_cors_headers(),
                    )
                )
                await writer.drain()
                return
            try:
                n = int(cl)
            except ValueError:
                writer.write(_response("HTTP/1.1 400 Bad Request", b"Bad Content-Length"))
                await writer.drain()
                return
            if n > 8192:
                writer.write(_response("HTTP/1.1 413 Payload Too Large", b"Too large"))
                await writer.drain()
                return
            if n:
                body = await _read_body(reader, n)

        if method == "OPTIONS" and path == "/update":
            writer.write(
                _response("HTTP/1.1 204 No Content", b"", extra_headers=_cors_headers())
            )
            await writer.drain()
            return

        if method == "POST" and path == "/update":
            try:
                data = json.loads(body.decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("not an object")
                latest_usage.update(data)
                print("Updated usage:", latest_usage)
                writer.write(
                    _response(
                        "HTTP/1.1 200 OK",
                        b"OK",
                        extra_headers=_cors_headers(),
                    )
                )
            except (ValueError, TypeError) as e:
                print("POST /update JSON error:", e)
                writer.write(
                    _response(
                        "HTTP/1.1 400 Bad Request",
                        b"Invalid JSON",
                        extra_headers=_cors_headers(),
                    )
                )
            await writer.drain()
            return

        if method == "GET" and path in ("/", "/health"):
            msg = b"lightpuck ok\n"
            writer.write(_response("HTTP/1.1 200 OK", msg))
            await writer.drain()
            return

        writer.write(_response("HTTP/1.1 404 Not Found", b"Not found"))
        await writer.drain()
    except Exception as e:
        print("Client handler error:", e)
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def start_http_server():
    await asyncio.start_server(_handle_client, "0.0.0.0", HTTP_PORT)
    print("HTTP server listening on 0.0.0.0:%d" % HTTP_PORT)
