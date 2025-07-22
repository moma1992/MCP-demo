"""Test cases for calculator MCP server using FastMCP library"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from custom_mcp.custom_mcp import add, server


class TestCalculatorMCPServer:
    """Test suite for calculator MCP server functionality"""

    def test_add_two_positive_numbers(self) -> None:
        """Test adding two positive numbers"""
        result = add(2, 3)
        assert result == 5

    def test_add_negative_numbers(self) -> None:
        """Test adding negative numbers"""
        result = add(-2, -3)
        assert result == -5

    def test_add_zero(self) -> None:
        """Test adding with zero"""
        result = add(0, 5)
        assert result == 5

    def test_add_float_numbers(self) -> None:
        """Test adding float numbers"""
        result = add(2.5, 3.7)
        assert result == 6.2

    def test_add_large_numbers(self) -> None:
        """Test adding large numbers"""
        result = add(1000000, 2000000)
        assert result == 3000000

    def test_server_instance(self) -> None:
        """Test that server instance is created"""
        assert server.name == "Custom MCP"

    def test_add_function_exists(self) -> None:
        """Test that add function is properly defined"""
        assert callable(add)
        assert add.__doc__ == "Add two numbers together"
