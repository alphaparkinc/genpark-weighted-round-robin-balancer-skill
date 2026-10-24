"""MCP Stdio Server for Weighted Round Robin Balancer.
100% Python Standard Library.
"""
import sys
import json
from client import WeightedRoundRobinBalancer

balancer = WeightedRoundRobinBalancer()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-weighted-round-robin-balancer-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "add_target",
                "description": "Register target server or model provider with static weighting",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "balancer_id": {"type": "string"},
                        "target_name": {"type": "string"},
                        "weight": {"type": "integer", "default": 1}
                    },
                    "required": ["balancer_id", "target_name"]
                }
            },
            {
                "name": "select_next_target",
                "description": "Select next backend using smooth weighted round-robin algorithm",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "balancer_id": {"type": "string"}
                    },
                    "required": ["balancer_id"]
                }
            },
            {
                "name": "set_target_health",
                "description": "Update target health status to enable or bypass routing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "balancer_id": {"type": "string"},
                        "target_name": {"type": "string"},
                        "healthy": {"type": "boolean", "default": True}
                    },
                    "required": ["balancer_id", "target_name"]
                }
            },
            {
                "name": "get_balancer_state",
                "description": "Return target weights, current weights, and selection metrics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "balancer_id": {"type": "string"}
                    },
                    "required": ["balancer_id"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "add_target":
            out = balancer.add_target(args.get("balancer_id", ""), args.get("target_name", ""), int(args.get("weight", 1)))
        elif name == "select_next_target":
            out = balancer.select_next_target(args.get("balancer_id", ""))
        elif name == "set_target_health":
            out = balancer.set_target_health(args.get("balancer_id", ""), args.get("target_name", ""), args.get("healthy", True))
        elif name == "get_balancer_state":
            out = balancer.get_balancer_state(args.get("balancer_id", ""))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
