import requests

def call_n8n_agent(payload: dict, webhook_url: str) -> dict:
    """
    Appelle un agent n8n via un webhook HTTP.
    Args:
        payload: Données à envoyer à n8n.
        webhook_url: URL du webhook n8n.
    Returns:
        La réponse JSON de n8n.
    """
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()
    return response.json()

# Exemple d'utilisation dans un chat
if __name__ == "__main__":
    webhook_url = "https://albankerloch.app.n8n.cloud/webhook/auto-claim-agent"
    # webhook_url = "https://albankerloch.app.n8n.cloud/webhook-test/auto-claim-agent"
    user_message = "Bonjour, je souhaite déclarer un sinistre : j'ai eu un accident de voiture aujourd'hui à Paris, mon véhicule a des dégâts importants et je n'ai pas fait de constat."
    session_id = "user-1234"  # identifiant unique pour la session
    payload = {
        "message": user_message,
        "session_id": session_id
    }
    n8n_response = call_n8n_agent(payload, webhook_url)
    print("Réponse de l'agent n8n :", n8n_response.get("output", ""))