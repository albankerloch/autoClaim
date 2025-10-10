# evaluation of DC generated

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

![Diagramme d'architecture](doc/achi-actuelle.png)

### Architecture Cible

| Vue | Description |
|---:|---|
| ![Vue 1](doc/achi-n8n.png) | Agent N8N |
| ![Vue 2](doc/achi-mcp.png) | Seveur MCP N8N |

4. Pour contrôler la taille ou ajouter des attributs, utilisez HTML :
<img src="doc/diagram.png" alt="Diagramme" width="600"/>

5. Remarques :
- Évitez les espaces dans les noms de fichiers (préférez `screenshot-1.png`), ou encodez-les (`%20`).
- Les chemins relatifs fonctionnent sur GitHub et dans la plupart des visualiseurs Markdown : `doc/mon_image.png`.
- Optimisez la taille des images pour un rendu rapide.

## Licence

- MIT License (Open source)
