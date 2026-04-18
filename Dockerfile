# Use Python 3.11 slim image for smaller size
FROM python:3.12-slim

# Install system dependencies for Chrome, browser automation, and git (needed for py2js)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    bash \
    xvfb \
    fluxbox \
    x11vnc \
    novnc \
    websockify \
    dbus-x11 \
    fonts-liberation \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency metadata first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies into .venv
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser \
    && mkdir -p /data/profiles /data/output /data/storage \
    && chmod +x /app/docker/entrypoint.sh \
    && chown -R mcpuser:mcpuser /app /data
USER mcpuser

# Expose MCP HTTP and noVNC ports
EXPOSE 8000
EXPOSE 6080
ENV PORT=8000
ENV DISPLAY=:99
ENV XVFB_WHD=1920x1080x24
ENV GHOST_ENABLE_NOVNC=true
ENV STEALTH_BROWSER_STORAGE_FILE=/data/storage/instances.json

# Health check for FastMCP HTTP server (uses PORT env var).
# FastMCP's /mcp route can return 400/406 to raw GET requests without a
# negotiated MCP session, so the container only verifies that the port accepts
# TCP connections.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, socket; s = socket.create_connection(('127.0.0.1', int(os.getenv('PORT', '8000'))), 5); s.close()" || exit 1

# Start the MCP server with HTTP transport (reads PORT env var automatically)
ENTRYPOINT ["bash", "docker/entrypoint.sh"]
CMD [".venv/bin/python", "src/server.py", "--transport", "http", "--host", "0.0.0.0"]
