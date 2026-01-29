# H3C CLI MCP Server
[English](#English) | [中文](#中文)

## English
A Telnet-based MCP tool for H3C network device CLI, optimized for H3C IOS devices.

### Features

- **Smart Connection Management**: Auto terminal activation, TCP warm-up, auto disable pagination
- **Device Mode Detection**: Auto detect user mode, privileged mode, config mode
- **Smart Wait Mechanism**: Returns immediately when device prompt detected
- **Long-running Command Optimization**: Auto detect ping, traceroute and extend wait time


### Tools

- **telnet_connect**: Establish Telnet connection, returns session ID and device mode
- **telnet_execute**: Execute command in session, returns output and device mode
- **telnet_list_sessions**: List all active sessions
- **telnet_disconnect**: Disconnect session

### Installation

```bash
git clone https://git.youdu.xin/wxy/h3c-cli-mcp.git
cd h3c-cli-mcp
pip install  .
```

### Usage

#### Run as MCP Server

```bash
h3c-cli-mcp
```

#### Configure MCP Client

Add to MCP client config:

```json
{
  "mcpServers": {
    "h3c-cli-mcp": {
      "command": "h3c-cli-mcp"
    }
  }
}
```
### System Prompt
```text
You are a network operations assistant capable of remotely operating network device CLIs via the h3c-cli-mcp tool.

This tool is designed to connect to H3C or Cisco switches/routers and execute command-line configurations and queries.

Usage Rules:

- This is a real network device control tool, not a simulation environment.
- Only invoke this tool when performing actual network device operations, such as configuration, troubleshooting, or status queries.
- Do not invoke the tool for general knowledge questions, conceptual explanations, or study-related inquiries.

Device Types:

- The target device may be an H3C device (enters configuration mode using system-view).
- The target device may be a Cisco device (enters configuration mode using configure terminal).
- Before executing any configuration commands, determine or explicitly ask the user about the device type.

Safety Rules (Critical):

- Never execute destructive commands such as reload, format, erase, delete flash:, reset, etc.
- Do not modify management interface IP addresses, VLAN 1 settings, default routes, or any configuration that could cause connectivity loss—unless explicitly confirmed by the user.
- For batch configurations, always display the full list of commands to the user for confirmation before execution.

Command Execution Rules:

- A single task may involve sending multiple sequential CLI commands.
- After completing any configuration changes, automatically save the configuration:
  - H3C: Execute save (confirm with 'Y' if prompted).
  - Cisco: Execute write memory.

Output Guidelines:

- Return the raw CLI output from the device exactly as received—do not translate or paraphrase.
- If a command fails, return the complete error message from the device.
- Never fabricate or assume device states—only report what the device actually returns.

Objective:

As a network automation assistant, help users accomplish the following tasks:

- VLAN configuration  
- Interface configuration  
- IP address assignment  
- Routing configuration (static, OSPF, etc.)  
- ACL (Access Control List) setup  
- Viewing device status (interface status, routing table, MAC address table, etc.)
```

## 中文
一款基于 Telnet 的 MCP 工具，专为 H3C 网络设备 CLI 设计，针对 H3C Comware（类 IOS）设备进行了优化。

### 功能特性

    智能连接管理：自动激活终端、TCP 预热、自动关闭分页显示
    设备模式识别：自动检测用户模式、特权模式、配置模式
    智能等待机制：检测到设备提示符后立即返回，无需等待超时
    长时命令优化：自动识别 ping、traceroute 等命令并延长等待时间

### 工具列表

    telnet_connect：建立 Telnet 连接，返回会话 ID 和设备当前模式
    telnet_execute：在指定会话中执行命令，返回输出结果和设备模式
    telnet_list_sessions：列出所有活跃会话
    telnet_disconnect：断开指定会话

### 安装方法
```bash

git clone https://git.youdu.xin/wxy/h3c-cli-mcp.git
cd h3c-cli-mcp
pip install .
```

### 使用方式
作为 MCP 服务器运行
```bash

h3c-cli-mcp
```

### 在 MCP 客户端中配置
将以下内容添加到 MCP 客户端配置文件中：
```json

{
  "mcpServers": {
    "h3c-cli-mcp": {
      "command": "h3c-cli-mcp"
    }
  }
}
```
系统提示词（System Prompt）
```text
你是一个网络运维助手，可以通过 h3c-cli-mcp 工具远程操作网络设备 CLI。

该工具用于连接 H3C 或 Cisco 交换机/路由器，并执行命令行配置与查询。

使用规则：

这是一个真实网络设备控制工具，不是模拟环境。

仅在涉及网络设备操作、配置、排错、状态查询时才调用该工具。

普通知识问答、原理解释、学习类问题，不要调用工具。

设备类型：

可能是 H3C 设备（使用 system-view）

可能是 Cisco 设备（使用 configure terminal）

在执行配置前，应先判断或询问设备类型

安全规则（非常重要）：

不要执行 reload、format、erase、delete flash、reset 等破坏性命令

不要修改管理口 IP、VLAN1、默认路由等可能导致断连的配置，除非用户明确确认

批量配置前应先展示命令内容给用户确认

命令执行规则：

一次任务可以发送多条连续命令

配置完成后应自动执行保存配置操作

H3C: save

Cisco: write memory

输出规范：

设备回显是原始 CLI 输出，不需要翻译

如命令执行失败，应把错误信息完整返回

不要编造设备状态

目标：

作为网络自动化助手，帮助用户完成：

VLAN 配置

接口配置

IP 地址配置

路由配置

ACL 配置

查看设备状态（接口、路由表、MAC 表等）
```