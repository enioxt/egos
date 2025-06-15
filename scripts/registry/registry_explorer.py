#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Tool Registry Explorer

This script provides a user-friendly interface to explore and visualize the contents
of the EGOS tool registry. It can display tools by category, filter by tags,
and generate summary reports.

Part of the EGOS Tool Registry and Integration System.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

@references:
- C:\EGOS\WORK_2025_05_22_tool_registry_system_plan.md (Tool Registry System Plan)
- C:\EGOS\config\tool_registry.json (Tool Registry)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import datetime

class RegistryExplorer:
    """
    Explorer for the EGOS tool registry. Provides methods to browse,
    filter, and summarize the registry contents.
    """
    
    def __init__(self, registry_path: Path):
        """Initialize the explorer with the registry path"""
        self.registry_path = registry_path
        self.registry = self._load_registry()
        
    def _load_registry(self) -> Dict[str, Any]:
        """Load the tool registry from the file system"""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load tool registry: {e}")
            return {"tools": []}
    
    def list_tools(self, category: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tools, optionally filtered by category or tag"""
        tools = self.registry.get("tools", [])
        
        if category:
            tools = [t for t in tools if t.get("category") == category]
            
        if tag:
            tools = [t for t in tools if tag in t.get("tags", [])]
            
        return tools
    
    def get_categories(self) -> List[str]:
        """Get all unique categories in the registry"""
        categories = set()
        for tool in self.registry.get("tools", []):
            if "category" in tool:
                categories.add(tool["category"])
        return sorted(list(categories))
    
    def get_tags(self) -> List[str]:
        """Get all unique tags used in the registry"""
        tags = set()
        for tool in self.registry.get("tools", []):
            for tag in tool.get("tags", []):
                tags.add(tag)
        return sorted(list(tags))
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific tool by its ID"""
        for tool in self.registry.get("tools", []):
            if tool.get("id") == tool_id:
                return tool
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate a summary of the registry contents"""
        tools = self.registry.get("tools", [])
        categories = self.get_categories()
        tags = self.get_tags()
        
        # Count tools by category
        category_counts = {}
        for category in categories:
            category_counts[category] = len([t for t in tools if t.get("category") == category])
        
        # Count tools by status
        status_counts = {}
        for tool in tools:
            status = tool.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Find most recent updates
        sorted_tools = sorted(
            tools, 
            key=lambda t: t.get("last_updated", "1970-01-01"),
            reverse=True
        )
        recent_updates = [
            {"id": t["id"], "name": t["name"], "last_updated": t.get("last_updated")}
            for t in sorted_tools[:5]
        ]
        
        return {
            "total_tools": len(tools),
            "categories": {
                "count": len(categories),
                "distribution": category_counts
            },
            "statuses": status_counts,
            "tags": {
                "count": len(tags),
                "list": tags
            },
            "recent_updates": recent_updates,
            "registry_last_updated": self.registry.get("last_updated", "unknown")
        }
    
    def print_tool_details(self, tool: Dict[str, Any]) -> None:
        """Print detailed information about a tool"""
        print(f"\n=== {tool.get('name')} ===")
        print(f"ID: {tool.get('id')}")
        print(f"Path: {tool.get('path')}")
        print(f"Category: {tool.get('category')}")
        print(f"Status: {tool.get('status')}")
        print("\nDescription:")
        print(f"  {tool.get('description')}")
        print("\nUsage:")
        print(f"  {tool.get('usage')}")
        
        if "tags" in tool and tool["tags"]:
            print("\nTags:")
            print(f"  {', '.join(tool['tags'])}")
        
        if "dependencies" in tool and tool["dependencies"]:
            print("\nDependencies:")
            for dep in tool["dependencies"]:
                print(f"  - {dep}")
        
        if "website_integration" in tool:
            wi = tool["website_integration"]
            print("\nWebsite Integration:")
            if "page" in wi:
                print(f"  Page: {wi['page']}")
            if "category" in wi:
                print(f"  Category: {wi['category']}")
            if "priority" in wi:
                print(f"  Priority: {wi['priority']}")
        
        if "examples" in tool and tool["examples"]:
            print("\nExamples:")
            for i, example in enumerate(tool["examples"], 1):
                print(f"  {i}. {example.get('description', 'Example')}")
                print(f"     Command: {example.get('command', '')}")
        
        print("\nMetadata:")
        print(f"  Created: {tool.get('created', 'unknown')}")
        print(f"  Last Updated: {tool.get('last_updated', 'unknown')}")
        print(f"  Maintainer: {tool.get('maintainer', 'unknown')}")
    
    def print_summary(self) -> None:
        """Print a summary of the registry contents"""
        summary = self.get_summary()
        
        print("\n=== EGOS Tool Registry Summary ===\n")
        print(f"Total Tools: {summary['total_tools']}")
        print(f"Registry Last Updated: {summary['registry_last_updated']}")
        
        print("\nCategories:")
        for category, count in summary['categories']['distribution'].items():
            print(f"  {category}: {count} tools")
        
        print("\nStatus Distribution:")
        for status, count in summary['statuses'].items():
            print(f"  {status}: {count} tools")
        
        print("\nRecently Updated Tools:")
        for tool in summary['recent_updates']:
            print(f"  {tool['name']} (updated: {tool['last_updated']})")
        
        print("\nTop Tags:")
        for tag in summary['tags']['list'][:10]:  # Show top 10 tags
            print(f"  {tag}")
    
    def print_tools_table(self, tools: List[Dict[str, Any]]) -> None:
        """Print a tabular list of tools"""
        if not tools:
            print("\nNo tools found matching the criteria.")
            return
        
        # Determine column widths
        id_width = max(len("ID"), max(len(t.get("id", "")) for t in tools))
        name_width = max(len("Name"), max(len(t.get("name", "")) for t in tools))
        category_width = max(len("Category"), max(len(t.get("category", "")) for t in tools))
        status_width = max(len("Status"), max(len(t.get("status", "")) for t in tools))
        
        # Print header
        print(f"\n{'ID':<{id_width}} | {'Name':<{name_width}} | {'Category':<{category_width}} | {'Status':<{status_width}}")
        print(f"{'-' * id_width}-+-{'-' * name_width}-+-{'-' * category_width}-+-{'-' * status_width}")
        
        # Print tools
        for tool in tools:
            print(f"{tool.get('id', ''):<{id_width}} | {tool.get('name', ''):<{name_width}} | {tool.get('category', ''):<{category_width}} | {tool.get('status', ''):<{status_width}}")

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="EGOS Tool Registry Explorer - Browse and visualize the tool registry"
    )
    
    parser.add_argument("--registry", type=str, default="config/tool_registry.json",
                      help="Path to the tool registry JSON file")
    parser.add_argument("--list", action="store_true",
                      help="List all tools")
    parser.add_argument("--category", type=str,
                      help="Filter tools by category")
    parser.add_argument("--tag", type=str,
                      help="Filter tools by tag")
    parser.add_argument("--tool", type=str,
                      help="Show details for a specific tool ID")
    parser.add_argument("--summary", action="store_true",
                      help="Show a summary of the registry contents")
    parser.add_argument("--categories", action="store_true",
                      help="List all categories")
    parser.add_argument("--tags", action="store_true",
                      help="List all tags")
    
    args = parser.parse_args()
    
    try:
        registry_path = Path(os.getcwd()) / args.registry
        explorer = RegistryExplorer(registry_path)
        
        if args.tool:
            tool = explorer.get_tool_by_id(args.tool)
            if tool:
                explorer.print_tool_details(tool)
            else:
                print(f"Tool with ID '{args.tool}' not found.")
                
        elif args.list or args.category or args.tag:
            tools = explorer.list_tools(args.category, args.tag)
            explorer.print_tools_table(tools)
            
        elif args.categories:
            categories = explorer.get_categories()
            print("\nAvailable Categories:")
            for category in categories:
                print(f"  {category}")
                
        elif args.tags:
            tags = explorer.get_tags()
            print("\nAvailable Tags:")
            for tag in tags:
                print(f"  {tag}")
                
        elif args.summary or not any([args.list, args.category, args.tag, args.tool, args.categories, args.tags]):
            # Show summary by default if no other option specified
            explorer.print_summary()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    main()