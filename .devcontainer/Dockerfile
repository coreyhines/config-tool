# Use Fedora Python image as base
FROM registry.fedoraproject.org/python-3.12:latest as final

# Install system packages and cleanup in one layer
RUN dnf update -y && dnf install -y \
    sudo-rs \
    vim-minimal \
    git \
    zip \
    cloc \
    bind-utils \
    zsh \
    zsh-syntax-highlighting \
    less \
    liquidprompt \
    iputils \
    curl \
    powerline-fonts \
    fontconfig \
    && dnf clean all

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

# Create the user and setup sudo-rs
RUN useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers-rs.d/$USERNAME \
    && chmod 0440 /etc/sudoers-rs.d/$USERNAME

# Copy dotfiles
COPY --chown=$USERNAME:$USERNAME .zshrc /home/$USERNAME/

# Install Python packages
RUN python -m pip install --no-cache-dir \
    black==24.2.0 \
    ruff==0.3.4 \
    pytest==8.0.2 \
    pytest-cov==4.1.0 \
    pre-commit==3.6.2

USER $USERNAME
WORKDIR /home/$USERNAME

# Set up ZSH with Oh My Zsh and plugins
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
    && git clone --depth 1 https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions \
    && git clone --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

WORKDIR /workspace

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1
