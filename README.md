# homeassistant-oekofen
Oekofen HomeAssistant integration via [oekofen-api](https://github.com/ckarrie/oekofen-api)

# Disclaimer
**Use at own risk**

# Installation

- add repository `https://github.com/ckarrie/homeassistant-oekofen` in your HACS
- restart HomeAssistant
- add integration

# ToDo

- add `sk` domain (solar)
- add csv log support (`http://192.168.178.222:4321/PASSWORD/log`)
- allow user to choose domains to update (device config)

## Developement

### init
- start Visual Studio Code
- open `zsh` Tab
  - `cd /workspaces/`
  - `git clone https://github.com/ckarrie/homeassistant-oekofen`
  - `cd /workspaces/homeassistant-core/config/custom_components`
  - `ln -s /workspaces/homeassistant-oekofen/custom_components/ha_oekofen .`

## update
- start Visual Studio Code
- push changes to git
- open `zsh` Tab
  - `cd /workspaces/homeassistant-oekofen`
  - `git pull`
- Menu > Ausühren > Ohne Debugger
- http://0.0.0.0:8123/lovelace/0

