# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load
ZSH_THEME="robbyrussell"

# Add plugins
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
)

# Source oh-my-zsh
source $ZSH/oh-my-zsh.sh

# User configuration
export LANG=en_US.UTF-8

# Aliases
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Set PATH
export PATH=$HOME/.local/bin:$PATH 
