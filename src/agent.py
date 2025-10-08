import json
from llm_chat import call_chat_llm
from langgraph.graph import END, StateGraph
from dataclasses import dataclass

INPUT = "bonjour j'ai eu un accident de voiture aujourd'hui on m'est rentré dedans par derrière un feu rouge c'était à origac et j'ai des blessures légères pas de problème avec le véhicule et je n'ai pas fait de constat"

@dataclass
class State:
    input: str
    date_accident: str
    ville_accident: str
    degats_vehicule: str
    constat_realise: str
    complete: str
    answer: str

def extract_data(state: State) -> State:
    print("Étape : Extraction des données")
    with open("src/types/one-claim.json", "r", encoding="utf-8") as f:
        json_schema = json.load(f)
    print("État du state :", state)
    response, usage = call_chat_llm("You are a helpful assistant.", f"Here is an audio transcription. Extract the car claim insurance from the following input: {state.input}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
    print("Réponse du LLM :", response)
    update_fields = []
    if state.date_accident == "" and response.get("date_accident", ""):
        state.date_accident = response.get("date_accident", "")
        update_fields.append("date de l'accident")
    if state.ville_accident == "" and response.get("ville_accident", ""):
        state.ville_accident = response.get("ville_accident", "")
        update_fields.append("ville de l'accident")
    if state.degats_vehicule == "" and response.get("degats_vehicule", ""):
        state.degats_vehicule = response.get("degats_vehicule", "")
        update_fields.append("dégâts du véhicule")
    if state.constat_realise == "" and response.get("constat_realise", ""):
        state.constat_realise = response.get("constat_realise", "")
        update_fields.append("réalisation d'un constat")
    if update_fields:
        state.answer = state.answer + "J'ai mis à jour les informations suivantes : " + ", ".join(update_fields) + ".\n"
    return state

def check_completeness(state: State) -> State:
    print("Étape : Vérification des données")
    if state.date_accident and state.ville_accident and state.degats_vehicule and state.constat_realise:
        state.complete = True
        state.answer = state.answer + "Toutes les informations nécessaires ont été collectées avec succès."
    else:
        missing_elements = []
        if not state.date_accident:
            missing_elements.append("date de l'accident")
        if not state.ville_accident:
            missing_elements.append("ville de l'accident")
        if not state.degats_vehicule:        
            missing_elements.append("dégâts du véhicule")
        if not state.constat_realise:
            missing_elements.append("réalisation d'un constat")
        state.answer = state.answer + "Merci de préciser les éléments suivants : " + ", ".join(missing_elements) + ".\n"
    return state

def decide(state):
    return END if state.complete else "extraction"

def launch_agent(state: State) -> State:
    workflow = StateGraph(State)
    workflow.add_node("extraction", extract_data)
    workflow.add_node("verification", check_completeness)
    workflow.set_entry_point("extraction")
    workflow.add_edge("extraction", "verification")
    # workflow.add_conditional_edges("verification", decide)
    graph = workflow.compile()
    result = graph.invoke(state)
    print("✔️ Workflow terminé")
    return result

if __name__ == "__main__":
    etat_initial = State(
        input=INPUT,
        date_accident="",
        ville_accident="",
        degats_vehicule="",
        injuries="",
        constat_realise="",
        complete=False,
        answer=""
    )
    print(launch_agent(etat_initial))