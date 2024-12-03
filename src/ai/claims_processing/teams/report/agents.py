from pathlib import Path
from enum import Enum
from pydantic import BaseModel
from enum import Enum
from src.ai.claims_processing.llm import llm
from src.ai.resources.gen_mermaid import save_graph_mermaid
from src.ai.claims_processing.teams.create_agent import AgentState, create_ordinary_agent,create_supervisor_node
from langgraph.graph import END, StateGraph, START
from src.utilities.helpers import load_yaml_file

agent1 = "claims_adjuster_1"

members = [agent1]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path("src/ai/claims_processing/teams/report/prompts/instruction.yaml")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
            "CLAIM_ADJUSTER_SUMMARY_PROMPT": yaml_data.get(
                "CLAIM_ADJUSTER_SUMMARY_PROMPT", ""
            ),

        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")


claim_adjuster_1_agent = create_ordinary_agent(
    _load_prompt_template()["CLAIM_ADJUSTER_SUMMARY_PROMPT"], llm
)


def comms_node(state):
    # read the last message in the message history.
    input = {
        "messages": [state["messages"][-1]],
        "agent_history": state["agent_history"],
    }
    result = claim_adjuster_1_agent.invoke(input)
    # respond back to the user.
    return {"messages": [result]}


# create options map for the supervisor output parser.
member_options = {member: member for member in members}

# create Enum object
MemberEnum = Enum("MemberEnum", member_options)


class SupervisorOutput(BaseModel):
    # defaults to communication agent
    next: MemberEnum = MemberEnum.claims_adjuster_1


supervisor_chain = create_supervisor_node(
    _load_prompt_template()["STIRRINGAGENTSYSTEMPROMPT"], llm, SupervisorOutput, members
)


workflow = StateGraph(AgentState)


workflow.add_node(agent1, comms_node)

workflow.add_node("Supervisor", supervisor_chain)
# set it as entrypoint to the graph.
workflow.set_entry_point("Supervisor")

workflow.add_edge("Supervisor", agent1)

workflow.add_conditional_edges("Supervisor", lambda state: state["next"])

report_graph = workflow.compile()
# save_graph_mermaid(report_graph,output_file='display/summary_langgraph.png')
