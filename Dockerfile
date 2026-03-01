FROM python:3.12-slim

# Install system dependencies: git, curl, ca-certificates, gh CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] \
        https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Install uv (into /root/.local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Python tools
RUN pip install --no-cache-dir \
    aider-chat \
    aider-skills

# Copy and enable entrypoint script
COPY create-skill-entrypoint.sh /usr/local/bin/create-skill-entrypoint.sh
RUN chmod +x /usr/local/bin/create-skill-entrypoint.sh

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/create-skill-entrypoint.sh"]
