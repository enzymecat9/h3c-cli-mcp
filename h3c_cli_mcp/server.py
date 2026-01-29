"""
Multi-Vendor Telnet MCP Server
Supports Cisco IOS & H3C Comware devices
"""

import asyncio
import uuid
import re
import json
from datetime import datetime
from dataclasses import dataclass, field

import telnetlib3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Multi-Vendor CLI MCP Server")

# =========================================================
# 🔍 提示符识别（核心：厂商判断 + 模式识别）
# =========================================================

def detect_vendor_and_mode(output: str) -> tuple[str, str]:
    if not output:
        return "unknown", "unknown"

    clean = output.replace('\x08', '').replace(' \b', '')

    # H3C
    h3c_match = re.search(r'[\r\n](\[[^\]]+\]|<[^>]+>)\s*$', clean)
    if h3c_match:
        return "h3c", h3c_match.group(1)

    # Cisco
    cisco_match = re.search(
        r'[\r\n]([A-Za-z0-9._-]+(\([a-z0-9-]+\))?[#>])\s*$',
        clean
    )
    if cisco_match:
        return "cisco", cisco_match.group(1)

    return "unknown", "unknown"

# =========================================================
# 🧩 会话模型
# =========================================================

@dataclass
class TelnetSession:
    session_id: str
    host: str
    port: int
    reader: telnetlib3.TelnetReader
    writer: telnetlib3.TelnetWriter
    vendor: str = "unknown"
    connected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "sessionId": self.session_id,
            "host": self.host,
            "port": self.port,
            "vendor": self.vendor,
            "connectedAt": self.connected_at.isoformat(),
        }

# =========================================================
# 🧠 会话管理器（多厂商核心）
# =========================================================

class TelnetSessionManager:

    def __init__(self):
        self.sessions: dict[str, TelnetSession] = {}

    async def connect(self, host: str, port: int, timeout: int = 5000) -> str:
        reader, writer = await asyncio.wait_for(
            telnetlib3.open_connection(host, port),
            timeout=timeout / 1000.0
        )

        session_id = str(uuid.uuid4())
        session = TelnetSession(session_id, host, port, reader, writer)
        self.sessions[session_id] = session

        # 激活终端
        for _ in range(3):
            writer.write("\r\n")
            await writer.drain()
            await asyncio.sleep(0.2)

        await self._drain(reader)

        # 识别厂商
        writer.write("\r\n")
        await writer.drain()
        await asyncio.sleep(0.3)
        output = await self._read_quick(reader)
        vendor, _ = detect_vendor_and_mode(output)
        session.vendor = vendor

        # 厂商初始化
        if vendor == "cisco":
            writer.write("terminal length 0\r\n")
        elif vendor == "h3c":
            writer.write("screen-length 0 temporary\r\n")

        await writer.drain()
        await asyncio.sleep(0.3)
        await self._drain(reader)

        return session_id

    async def execute(self, session_id: str, command: str, wait_ms: int = 3000) -> str:
        session = self.sessions[session_id]
        session.writer.write(command + "\r\n")
        await session.writer.drain()

        output = ""
        start = asyncio.get_event_loop().time()

        if session.vendor == "h3c":
            prompt_pattern = re.compile(r'[\r\n](\[[^\]]+\]|<[^>]+>)\s*$')
        else:
            prompt_pattern = re.compile(r'[\r\n]([A-Za-z0-9._-]+(\([a-z0-9-]+\))?[#>])\s*$')

        while True:
            if asyncio.get_event_loop().time() - start > wait_ms / 1000:
                break
            try:
                data = await asyncio.wait_for(session.reader.read(4096), timeout=0.2)
                if data:
                    output += data
                    clean = output.replace('\x08', '').replace(' \b', '')
                    if prompt_pattern.search(clean):
                        await asyncio.sleep(0.2)
                        break
            except asyncio.TimeoutError:
                pass

        return output

    async def disconnect(self, session_id: str):
        session = self.sessions.pop(session_id)
        session.writer.close()

    def list_sessions(self):
        return [s.to_dict() for s in self.sessions.values()]

    async def _drain(self, reader):
        try:
            while True:
                await asyncio.wait_for(reader.read(4096), timeout=0.1)
        except asyncio.TimeoutError:
            pass

    async def _read_quick(self, reader):
        out = ""
        try:
            while True:
                out += await asyncio.wait_for(reader.read(4096), timeout=0.2)
        except asyncio.TimeoutError:
            pass
        return out


session_manager = TelnetSessionManager()

# =========================================================
# 🛠 MCP 工具
# =========================================================

@mcp.tool()
async def telnet_connect(host: str, port: int) -> str:
    session_id = await session_manager.connect(host, port)
    output = await session_manager.execute(session_id, "", 1000)
    vendor, mode = detect_vendor_and_mode(output)

    return json.dumps({
        "success": True,
        "sessionId": session_id,
        "vendor": vendor,
        "deviceMode": mode
    }, ensure_ascii=False)


@mcp.tool()
async def telnet_execute(session_id: str, command: str) -> str:
    output = await session_manager.execute(session_id, command)
    vendor, mode = detect_vendor_and_mode(output)

    return json.dumps({
        "success": True,
        "output": output,
        "vendor": vendor,
        "deviceMode": mode
    }, ensure_ascii=False)


@mcp.tool()
def telnet_list_sessions() -> str:
    return json.dumps(session_manager.list_sessions(), ensure_ascii=False)


@mcp.tool()
async def telnet_disconnect(session_id: str) -> str:
    await session_manager.disconnect(session_id)
    return f"Session {session_id} disconnected"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
