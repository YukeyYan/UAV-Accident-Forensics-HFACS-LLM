# UAV Accident Forensics System Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for advanced visualizations)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Node.js dependencies (if web_components exists)
RUN if [ -d "web_components" ]; then \
        cd web_components && \
        npm install && \
        cd ..; \
    fi

# Create necessary directories
RUN mkdir -p data logs reports

# Expose ports
EXPOSE 8501 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start Node.js service in background if available\n\
if [ -d "web_components" ]; then\n\
    echo "Starting Node.js visualization service..."\n\
    cd web_components\n\
    npm start &\n\
    cd ..\n\
fi\n\
\n\
# Start Streamlit\n\
echo "Starting Streamlit application..."\n\
streamlit run streamlit_app.py \\\n\
    --server.port $STREAMLIT_SERVER_PORT \\\n\
    --server.address $STREAMLIT_SERVER_ADDRESS \\\n\
    --server.headless true \\\n\
    --browser.gatherUsageStats false\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
