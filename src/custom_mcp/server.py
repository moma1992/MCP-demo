#!/usr/bin/env python3
"""
MCP Server for Claude Desktop
Implements STDIO transport for Model Context Protocol
"""

import json
import sys
from typing import Dict, Any, List
from .custom_mcp import create_custom_mcp_server


class MCPServerSTDIO:
    """MCP Server with STDIO transport for Claude Desktop"""
    
    def __init__(self, server):
        self.server = server
        self.request_id = 0
    
    def send_response(self, request_id: int, result: Any = None, error: str = None):
        """Send JSON-RPC response via STDOUT"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if error:
            response["error"] = {"code": -1, "message": error}
        else:
            response["result"] = result
        
        print(json.dumps(response), flush=True)
    
    def send_notification(self, method: str, params: Dict[str, Any] = None):
        """Send JSON-RPC notification via STDOUT"""
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params:
            notification["params"] = params
        
        print(json.dumps(notification), flush=True)
    
    def handle_initialize(self, request_id: int, params: Dict[str, Any]):
        """Handle initialize request"""
        capabilities = {
            "tools": {
                "listChanged": True
            }
        }
        
        server_info = {
            "name": self.server.name,
            "version": "1.0.0"
        }
        
        result = {
            "capabilities": capabilities,
            "serverInfo": server_info
        }
        
        self.send_response(request_id, result)
        # Send initialized notification
        self.send_notification("initialized")
        sys.stderr.write("Initialize response sent, server ready\n")
        sys.stderr.flush()
    
    def handle_tools_list(self, request_id: int, params: Dict[str, Any]):
        """Handle tools/list request"""
        tools = []
        
        for tool in self.server.list_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            })
        
        self.send_response(request_id, {"tools": tools})
    
    def handle_tools_call(self, request_id: int, params: Dict[str, Any]):
        """Handle tools/call request"""
        try:
            name = params.get("name")
            args = params.get("arguments", {})
            
            result = self.server.call_tool(name, args)
            
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }
            
            self.send_response(request_id, response)
            
        except Exception as e:
            self.send_response(request_id, error=str(e))
    
    def handle_request(self, request: Dict[str, Any]):
        """Handle incoming JSON-RPC request"""
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})
        
        if method == "initialize":
            self.handle_initialize(request_id, params)
        elif method == "initialized":
            # Notification, no response needed
            sys.stderr.write("Received initialized notification\n")
            sys.stderr.flush()
        elif method == "tools/list":
            self.handle_tools_list(request_id, params)
        elif method == "tools/call":
            self.handle_tools_call(request_id, params)
        else:
            if request_id is not None:
                self.send_response(request_id, error=f"Unknown method: {method}")
            else:
                sys.stderr.write(f"Unknown notification: {method}\n")
                sys.stderr.flush()
    
    def run(self):
        """Run the MCP server with STDIO transport"""
        sys.stderr.write("MCP Custom Server starting...\n")
        sys.stderr.flush()
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                sys.stderr.write(f"Received request: {line}\n")
                sys.stderr.flush()
                
                try:
                    request = json.loads(line)
                    self.handle_request(request)
                except json.JSONDecodeError as e:
                    sys.stderr.write(f"JSON decode error: {e}\n")
                    # Send error response if we can extract an ID
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            sys.stderr.write("Server interrupted by user\n")
            sys.exit(0)
        except Exception as e:
            sys.stderr.write(f"Server error: {e}\n")
            sys.stderr.flush()
            sys.exit(1)
        
        sys.stderr.write("Server shutting down normally\n")
        sys.stderr.flush()


def main():
    """Main entry point for MCP server"""
    custom_mcp_server = create_custom_mcp_server()
    mcp_server = MCPServerSTDIO(custom_mcp_server)
    mcp_server.run()


if __name__ == "__main__":
    main()