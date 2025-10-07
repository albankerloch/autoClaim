import json
from llm_chat import call_chat_llm
from langgraph.graph import END, StateGraph
from dataclasses import dataclass

INPUT = "bonjour j'ai eu un accident de voiture aujourd'hui on m'est rentré dedans par derrière un feu rouge c'était à origac et j'ai des blessures légères pas de problème avec le véhicule et je n'ai pas fait de constat"

@dataclass
class State:
	description: str
	date_of_accident: str
	location: str
	vehicle_damage: str
	injuries: str
	accident_report: str
	complete: str

def extract_data(state: State) -> State:
	print("Étape : Extraction des données")
	with open("src/types/one-claim.json", "r", encoding="utf-8") as f:
		json_schema = json.load(f)
	response, usage = call_chat_llm("You are a helpful assistant.", f"Here is an audio transcription. Extract the car claim insurance from the following input: {state.input}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
	state.description = response.get("description", "")
	state.date_of_accident = response.get("date_of_accident", "")
	state.location = response.get("location", "")
	state.vehicle_damage = response.get("vehicle_damage", "")
	state.injuries = response.get("injuries", "")
	state.accident_report = response.get("accident_report", "")
	return state

def check_completeness(state: State) -> State:
	print("Étape : Vérification des données")
	if state.description and state.date_of_accident and state.location and state.vehicle_damage and state.injuries and state.accident_report:
		state.complete = True
	return state

def decide(state):
	return END if state.complete else "extraction"

if __name__ == "__main__":
	
	workflow = StateGraph(State)
	workflow.add_node("extraction", extract_data)
	workflow.add_node("verification", check_completeness)
	workflow.set_entry_point("extraction")
	workflow.add_edge("extraction", "verification")
	workflow.add_conditional_edges("verification", decide)
	graph = workflow.compile()

	etat_initial = State(
		input=INPUT,
		description="",
		date_of_accident="",
		location="",
		vehicle_damage="",
		injuries="",
		accident_report="",
		complete=False
	)
	result = graph.invoke(etat_initial)
	print("✔️ Données validées, workflow terminé")
