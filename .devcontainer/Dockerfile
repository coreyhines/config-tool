# Use Fedora base image
FROM registry.fedoraproject.org/fedora:39 as final

# Install system packages and cleanup in one layer
RUN dnf update -y && dnf install -y \
    python3.12 \
    python3.12-pip \
    sudo-rs \
    vim-minimal \
    git \
    zip \
    cloc \
    bind-utils \
    zsh \
    less \
    iputils \
    curl \
    powerline-fonts \
    fontconfig \
    rust \
    cargo \
    openssh-clients \
    procps-ng \
    tar \
    gzip \
    bash-completion \
    && dnf clean all \
    && ln -sf /usr/bin/python3.12 /usr/bin/python \
    && ln -sf /usr/bin/pip3.12 /usr/bin/pip

ARG USER
ARG UID
ARG GID

ENV USERNAME=$USER \
    USER_UID=$UID \
    USER_GID=$GID \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/$USER/.local/bin:$PATH" \
    SHELL=/bin/zsh \
    CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH="/usr/local/cargo/bin:$PATH" \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

# Create the user and setup sudo-rs
RUN mkdir -p /etc/sudoers-rs.d && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers-rs.d/$USERNAME \
    && chmod 0440 /etc/sudoers-rs.d/$USERNAME

# Setup SSH directory with proper permissions
RUN mkdir -p /home/$USERNAME/.ssh \
    && chown -R $USERNAME:$USER_GID /home/$USERNAME/.ssh \
    && chmod 700 /home/$USERNAME/.ssh

# Copy dotfiles
COPY --chown=$USERNAME:dialout .zshrc /home/$USERNAME/

# Install Python packages
RUN python3.12 -m pip install --no-cache-dir \
    black==24.2.0 \
    ruff==0.3.4 \
    pytest==8.0.2 \
    pytest-cov==4.1.0 \
    pre-commit==3.6.2

USER $USERNAME
WORKDIR /home/$USERNAME

# Set up ZSH with Oh My Zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

WORKDIR /workspace
