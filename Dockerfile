# nano-mcp-termux Dockerfile
# Build command: docker build -t Lmeng486/nano-mcp-termux .
# Run command: docker run -i --rm Lmeng486/nano-mcp-termux

FROM python:3.12-alpine

WORKDIR /app

# Copy the single-file MCP server
COPY nano_mcp_termux.py .
RUN chmod +x nano_mcp_termux.py

# Keep container running by waiting for input
CMD ["python3", "nano_mcp_termux.py"]
