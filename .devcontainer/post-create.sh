#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Install Python dependencies with pip
echo "📦 Installing Python dependencies..."
python -m pip install -r requirements.txt

# Install additional development tools
echo "🛠 Installing development tools..."
python -m pip install ruff pytest pytest-cov pre-commit

# Setup pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
cat > .pre-commit-config.yaml <<EOL
repos:
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.4
    hooks:
    -   id: ruff
        args: [--fix]
    -   id: ruff-format
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
EOL

pre-commit install

# Setup Oh My Zsh with a modern theme and essential plugins
echo "🎨 Setting up Oh My Zsh..."
if [ -d "$HOME/.oh-my-zsh" ]; then
    rm -rf "$HOME/.oh-my-zsh"
fi

# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Install Powerlevel10k theme
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

# Install essential plugins
cd ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins
git clone --depth 1 https://github.com/zsh-users/zsh-autosuggestions
git clone --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting
git clone --depth 1 https://github.com/zdharma-continuum/fast-syntax-highlighting
git clone --depth 1 https://github.com/MichaelAquilina/zsh-you-should-use

# Setup dotfiles
echo "📂 Setting up dotfiles..."
if [ -d "$HOME/dotfiles" ]; then
    rm -rf "$HOME/dotfiles"
fi

# Clone and setup dotfiles
git clone --depth 1 git@github.com:coreyhines/dotfiles.git "$HOME/dotfiles"
if [ -f "$HOME/.zshrc" ]; then
    rm "$HOME/.zshrc"
fi
/usr/local/bin/dotbot -c "$HOME/dotfiles/install.conf.yaml"

# Create custom zsh configuration
echo "⚙️ Configuring Zsh..."
cat > "$HOME/.zshrc.local" <<EOL
# Enable Powerlevel10k instant prompt
if [[ -r "\${XDG_CACHE_HOME:-\$HOME/.cache}/p10k-instant-prompt-\${(%):-%n}.zsh" ]]; then
  source "\${XDG_CACHE_HOME:-\$HOME/.cache}/p10k-instant-prompt-\${(%):-%n}.zsh"
fi

# Set theme
ZSH_THEME="powerlevel10k/powerlevel10k"

# Enable plugins
plugins=(
    git
    docker
    python
    pip
    virtualenv
    history
    zsh-autosuggestions
    fast-syntax-highlighting
    zsh-you-should-use
)

# Source Oh My Zsh
source \$ZSH/oh-my-zsh.sh

# Aliases
alias ll='ls -la'
alias py='python3'
alias pipr='python -m pip install -r requirements.txt'

# Python development aliases
alias ruff='ruff check --fix .'
alias ruff-format='ruff format .'
alias pytest='python -m pytest'
EOL

echo "source \$HOME/.zshrc.local" >> "$HOME/.zshrc"

# Setup VS Code Python settings
echo "⚙️ Configuring VS Code Python settings..."
mkdir -p "$HOME/.vscode-server/data/Machine"
cat > "$HOME/.vscode-server/data/Machine/settings.json" <<EOL
{
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.fixAll": ["ruff"],
    "python.formatting.provider": "ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true,
        "source.organizeImports": true
    }
}
EOL

echo "✅ Development environment setup complete!" 
