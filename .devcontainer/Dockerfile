FROM python:3.9.16

RUN apt update && apt install -y \
    sudo vim git zip cloc dnsutils \
    zsh zsh-syntax-highlighting zsh-doc \
    less liquidprompt \
    inetutils-ping

RUN apt -y dist-upgrade

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

RUN pip install --upgrade pip
RUN pip install black autopep8 dotbot linode_api4 ruamel.yaml Pyyaml lxml jsonrpclib cvprac pyeapi pylint apscheduler bandit numpy

USER $USERNAME
# set home
ENV HOME /home/$USERNAME

ENV TERM xterm

ENV SHELL /bin/zsh
ENV ZSH=/home/$USERNAME/.oh-my-zsh

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
RUN ln -s /workspaces/config-tool /home/$USERNAME/config-tool
