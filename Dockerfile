# Use Python slim image as base
FROM python:3.12-slim-bookworm as final

# Install system packages and cleanup in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    vim \
    git \
    zip \
    cloc \
    bind9-dnsutils \
    zsh \
    zsh-syntax-highlighting \
    less \
    liquidprompt \
    inetutils-ping \
    curl \
    fonts-powerline \
    fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG USER
ARG UID
ARG GID

ENV USERNAME=$USER \
    USER_UID=$UID \
    USER_GID=$GID \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/$USER/.local/bin:$PATH" \
    SHELL=/bin/zsh

# Create the user and setup sudo
RUN useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

# Install uv and Python packages
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && . ~/.bashrc \
    && export PATH="/home/$USERNAME/.local/bin:$PATH" \
    && /home/$USERNAME/.local/bin/uv venv \
    && . .venv/bin/activate \
    && /home/$USERNAME/.local/bin/uv pip install --upgrade pip \
    && /home/$USERNAME/.local/bin/uv pip install \
        black==24.1.1 \
        flake8==7.0.0 \
        pytest==8.0.0 \
        pytest-cov==4.1.0 \
        mypy==1.8.0 \
        pylint==3.0.3 \
        rope==1.12.0

# Set up ZSH with Oh My Zsh and plugins
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
    && git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions \
    && git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# Configure ZSH
COPY --chown=$USERNAME:$USERNAME .zshrc /home/$USERNAME/.zshrc

WORKDIR /workspace

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1 
