import base64
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import time

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = REPO_ROOT / "scripts" / "server.cjs"
TOKEN = "test-session-token"


def _available_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def companion_server(tmp_path):
    port = _available_port()
    env = os.environ.copy()
    env.update(
        {
            "BRAINSTORM_DIR": str(tmp_path),
            "BRAINSTORM_HOST": "127.0.0.1",
            "BRAINSTORM_PORT": str(port),
            "BRAINSTORM_TOKEN": TOKEN,
        }
    )
    process = subprocess.Popen(
        ["node", str(SERVER_PATH)],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            line = process.stdout.readline()
            if line:
                message = json.loads(line)
                if message.get("type") == "server-started":
                    yield port, tmp_path
                    return
            if process.poll() is not None:
                stderr = process.stderr.read()
                raise AssertionError(
                    f"companion server exited with {process.returncode}: {stderr}"
                )
        raise AssertionError("companion server did not start within 10 seconds")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _upgrade(port, *, token=None, origin=None):
    websocket_key = base64.b64encode(os.urandom(16)).decode("ascii")
    target = f"/?key={token}" if token is not None else "/"
    headers = [
        f"GET {target} HTTP/1.1",
        f"Host: 127.0.0.1:{port}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {websocket_key}",
        "Sec-WebSocket-Version: 13",
    ]
    if origin is not None:
        headers.append(f"Origin: {origin}")

    sock = socket.create_connection(("127.0.0.1", port), timeout=5)
    sock.sendall(("\r\n".join(headers) + "\r\n\r\n").encode("ascii"))
    response = b""
    try:
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    except ConnectionResetError:
        pass
    return sock, response


def _masked_text_frame(payload):
    data = payload.encode("utf-8")
    mask = os.urandom(4)
    if len(data) >= 126:
        raise ValueError("test payload is unexpectedly large")
    header = bytes([0x81, 0x80 | len(data)])
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
    return header + mask + masked


@pytest.mark.parametrize(
    ("token", "origin"),
    [
        (None, "http://127.0.0.1:{port}"),
        (TOKEN, "https://attacker.example"),
        (TOKEN, None),
    ],
)
def test_websocket_rejects_untrusted_handshakes(
    companion_server, token, origin
):
    port, session_dir = companion_server
    formatted_origin = origin.format(port=port) if origin else None

    sock, response = _upgrade(port, token=token, origin=formatted_origin)
    with sock:
        assert b"101 Switching Protocols" not in response
        try:
            sock.sendall(
                _masked_text_frame(
                    json.dumps({"type": "click", "choice": "forged"})
                )
            )
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    time.sleep(0.1)
    assert not (session_dir / "state" / "events").exists()


def test_authenticated_same_origin_websocket_persists_choice(companion_server):
    port, session_dir = companion_server
    origin = f"http://127.0.0.1:{port}"

    sock, response = _upgrade(port, token=TOKEN, origin=origin)
    with sock:
        assert response.startswith(b"HTTP/1.1 101 Switching Protocols\r\n")
        event = {"type": "click", "choice": "trusted"}
        sock.sendall(_masked_text_frame(json.dumps(event)))

    events_file = session_dir / "state" / "events"
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not events_file.exists():
        time.sleep(0.05)

    assert json.loads(events_file.read_text().strip()) == event
