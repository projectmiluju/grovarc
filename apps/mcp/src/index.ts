import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { tools } from "./tools.js";

const server = new McpServer({
  name: "grovarc",
  version: "0.1.0",
});

// 모든 tool 등록
for (const tool of tools) {
  server.tool(tool.name, tool.description, tool.inputSchema.shape, tool.handler);
}

// stdio transport로 실행 (Cursor / Claude Code / Codex CLI / Gemini CLI 공통)
const transport = new StdioServerTransport();
await server.connect(transport);
