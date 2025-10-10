# AutoClaim, an AXA Assistant

<p>
  <a href="LICENSE">
    <img alt="Licence MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"/>
  </a>
</p>

## Launch the app

### Using Python locally

- python3 -m venv .venv

- source .venv/bin/activate

- pip install -r requirements.txt

- streamlit run src/app.py


### Deploy on Connect Posit Cloud (account : alban.kerloch@gmail.com)

- push a new commit to main

- this url is updated automatically : https://0199c879-4565-15ff-d356-d19689459be9.share.connect.posit.cloud/

## Architecture

### Architecture Actuelle

![Diagramme d'architecture](doc/archi-actuelle.png)

### Architecture Cible

| Description | Vue  |
|---:|---|
| Agent N8N | ![Vue 1](doc/archi-n8n.png) |
| Seveur MCP N8N | ![Vue 2](doc/archi-mcp.png) |


## Licence

- MIT License (Open source) — voir le fichier [LICENSE](LICENSE)

