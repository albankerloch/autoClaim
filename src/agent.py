import json
from llm_chat import call_chat_llm
from langgraph.graph import END, StateGraph
from dataclasses import dataclass

INPUT = "bonjour j'ai eu un accident de voiture aujourd'hui on m'est rentré dedans par derrière un feu rouge c'était à origac et j'ai des blessures légères pas de problème avec le véhicule et je n'ai pas fait de constat"

@dataclass
class State:
    input: str
    description: str
    date_of_accident: str
    location: str
    vehicle_damage: str
    injuries: str
    constat_accident: str
    complete: str

def extract_data(state: State) -> State:
    print("Étape : Extraction des données")
    with open("src/types/one-claim.json", "r", encoding="utf-8") as f:
        json_schema = json.load(f)
    response, usage = call_chat_llm("You are a helpful assistant.", f"Here is an audio transcription. Extract the car claim insurance from the following input: {state.input}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
    if state.description == "" and response.get("description", "") is not None:
        state.description = response.get("description", "")
    if state.date_of_accident == "" and response.get("date_of_accident", "") is not None:
        state.date_of_accident = response.get("date_of_accident", "")
    if state.location == "" and response.get("location", "") is not None:
        state.location = response.get("location", "")
    if state.vehicle_damage == "" and response.get("vehicle_damage", "") is not None:
        state.vehicle_damage = response.get("vehicle_damage", "")
    if state.injuries == "" and response.get("injuries", "") is not None:
        state.injuries = response.get("injuries", "")
    if state.constat_accident == "" and response.get("constat_accident", "") is not None:
        state.constat_accident = response.get("constat_accident", "")
    return state

def check_completeness(state: State) -> State:
    print("Étape : Vérification des données")
    if state.description and state.date_of_accident and state.location and state.vehicle_damage and state.injuries and state.constat_accident:
        state.complete = True
    return state

def decide(state):
    return END if state.complete else "extraction"

def launch_agent(input_string: str):
    workflow = StateGraph(State)
    workflow.add_node("extraction", extract_data)
    workflow.add_node("verification", check_completeness)
    workflow.set_entry_point("extraction")
    workflow.add_edge("extraction", "verification")
    # workflow.add_conditional_edges("verification", decide)
    graph = workflow.compile()

    etat_initial = State(
        input=input_string,
        description="",
        date_of_accident="",
        location="",
        vehicle_damage="",
        injuries="",
        constat_accident="",
        complete=False
    )
    result = graph.invoke(etat_initial)
    print("✔️ Données validées, workflow terminé")
    print(result)
    pass

if __name__ == "__main__":
    launch_agent(INPUT)