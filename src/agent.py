import json
from llm_chat import call_chat_llm
from langgraph.graph import END, StateGraph
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
if not GMAIL_APP_PASSWORD:
    raise ValueError("Missing GMAIL_APP_PASSWORD")


INPUT = "bonjour j'ai eu un accident de voiture aujourd'hui on m'est rentré dedans par derrière un feu rouge. Je veux déclarer mon accident auprès d'axa : c'était à origac et j'ai des blessures légères pas de problème avec le véhicule et je n'ai pas fait de constat"
INPUT_INFO = "bonjour j'ai eu un accident de voiture et je ne sais pas quoi faire"


@dataclass
class State:
    input: str
    date_accident: str
    ville_accident: str
    degats_voiture: str
    constat_realise: str
    complete: str
    answer: str
    intent: str = ""  # Ajout du champ intent

def detect_intent(state: State) -> State:
    print("Étape : Détection de l'intention")
    with open("src/types/intent.json", "r", encoding="utf-8") as f:
        json_schema = json.load(f)
    if state.intent != "declaration":
        response, usage = call_chat_llm("You are a helpful assistant.", f"Here is an audio transcription of a customer who had a car accident. Detect if the customer want information about what to do or if he wants to want to declare a claim: {state.input}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
        state.intent = response.get("intent", "")
        print(f"Intention détectée : {state.intent}")
    return state

def decide_path(state: State) -> State:
    return state.intent

def answer_question(state: State) -> State:
    print("Étape : Réponse à la question")
    with open("src/types/answer.json", "r", encoding="utf-8") as f:
        json_schema = json.load(f)
    response, usage = call_chat_llm("You are a helpful assistant.", f"Here is an audio transcription of a customer who had a car accident. Answer him in french in a concise way: {state.input}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
    state.answer = response.get("answer", "")
    print(f"Réponse apportée : {state.answer}")
    return state

def extract_data(state: State) -> State:
    print("Étape : Extraction des données")
    with open("src/types/one-claim.json", "r", encoding="utf-8") as f:
        json_schema = json.load(f)
    response, usage = call_chat_llm("You are a helpful assistant.", f"Here is an audio transcription of a customer who had a car accident. Extract the claim insurance key data from the following input: {state.input}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
    update_fields = []
    if state.date_accident == "" and response.get("date_accident", ""):
        state.date_accident = response.get("date_accident", "")
        update_fields.append("date de l'accident")
    if state.ville_accident == "" and response.get("ville_accident", ""):
        state.ville_accident = response.get("ville_accident", "")
        update_fields.append("ville de l'accident")
    if state.degats_voiture == "" and response.get("degats_voiture", ""):
        state.degats_voiture = response.get("degats_voiture", "")
        update_fields.append("dégâts du véhicule")
    if state.constat_realise == "" and response.get("constat_realise", ""):
        state.constat_realise = response.get("constat_realise", "")
        update_fields.append("réalisation d'un constat")
    if update_fields:
        state.answer = state.answer + "J'ai mis à jour les informations suivantes : " + ", ".join(update_fields) + ".\n"
    return state

def check_completeness(state: State) -> State:
    print("Étape : Vérification des données")
    if state.date_accident and state.ville_accident and state.degats_voiture and state.constat_realise:
        state.complete = True
        state.answer = state.answer + "Toutes les informations nécessaires ont été collectées avec succès."
    else:
        missing_elements = []
        if not state.date_accident:
            missing_elements.append("date de l'accident")
        if not state.ville_accident:
            missing_elements.append("ville de l'accident")
        if not state.degats_voiture:        
            missing_elements.append("dégâts du véhicule")
        if not state.constat_realise:
            missing_elements.append("réalisation d'un constat")
        state.answer = state.answer + "Merci de préciser les éléments suivants : " + ", ".join(missing_elements) + "."
    return state

def send_email(state: State) -> State:
    print("Étape : Envoi de l'email")
    recipient = "alban.kerloch@gmail.com"
    subject = "Détails du sinistre automobile"
    body = f"Détails du sinistre :\n\n"
    body += f"Date de l'accident : {state.date_accident}\n"
    body += f"Ville de l'accident : {state.ville_accident}\n"
    body += f"Dégâts du véhicule : {state.degats_voiture}\n"
    body += f"Constat réalisé : {'Oui' if state.constat_realise else 'Non'}\n"
    body += f"\n\nMerci de traiter cette déclaration de sinistre. Cordialement. AutoClaim Bot"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "no-reply@autoClaim.com"
    msg["To"] = recipient

    # Utilisation d'un serveur SMTP externe (exemple Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "alban.kerloch.exalt@gmail.com" 
    smtp_password = GMAIL_APP_PASSWORD

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], [recipient], msg.as_string())
        state.answer = state.answer + "\nUn email de confirmation a été envoyé à alban.kerloch@gmail.com avec les détails du sinistre."
    except Exception as e:
        state.answer = state.answer + f"\nErreur lors de l'envoi de l'email : {e}"

    state.intent = "information"

    return state

def decide(state):
    return END if not state.complete else "mail"

def launch_agent(state: State) -> State:
    workflow = StateGraph(State)
    workflow.add_node("detection", detect_intent)
    workflow.add_node("information", answer_question)
    workflow.add_node("declaration", extract_data)
    workflow.add_node("verification", check_completeness)
    workflow.add_node("mail", send_email)
    workflow.set_entry_point("detection")
    workflow.add_conditional_edges("detection", decide_path)
    workflow.add_edge("information", END)
    workflow.add_edge("declaration", "verification")
    workflow.add_conditional_edges("verification", decide)
    workflow.add_edge("mail", END)

    graph = workflow.compile()
    result = graph.invoke(state)
    print("✔️ Workflow terminé")
    return result

if __name__ == "__main__":
    etat_initial = State(
        input=INPUT,
        date_accident="",
        ville_accident="",
        degats_voiture="",
        constat_realise="",
        complete=False,
        answer="",
        intent=""
    )
    result = launch_agent(etat_initial)
    print(result["answer"])