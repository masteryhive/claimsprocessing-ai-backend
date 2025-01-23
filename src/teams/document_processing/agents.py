from enum import Enum
import functools
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from pathlib import Path
from src.teams.create_agent_utils import crew_nodes
from src.ai_models.llm import llm
from src.teams.resources.gen_mermaid import save_graph_mermaid
from src.teams.document_processing.tools import *
from src.teams.create_agent import *
from langgraph.graph import END, StateGraph, START
from src.utilities.helpers import load_yaml_file
from src.config.appconfig import env_config
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage

agent1 = "claim_form_checker"
agent2 = "supporting_evidence_checker"
agentX = "claims_document_processing_clerk"
members = [agent1, agent2, agentX]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path(
            "src/teams/document_processing/prompts/instruction.yaml"
        )
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
            "CLAIMS_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "CLAIMS_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT", ""
            ),
            "SUPPORTING_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "SUPPORTING_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT", ""
            ),
            "PROCESS_CLERK_PROMPT": yaml_data.get("PROCESS_CLERK_PROMPT", ""),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")


claims_document_verifier_agent = create_tool_agent(
    llm=llm,
    tools=[],
)

async def claims_document_verifier_node(state):
    # read the last message in the message history.
    input = {
        "messages": [SystemMessage(content=_load_prompt_template()[
        "CLAIMS_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT"
    ])] + [state["messages"][-1]],
        "claim_form_json":state["claim_form_json"],
    }
    result = await claims_document_verifier_agent.ainvoke(input)
    # respond back to the user.
    return {"document_verifier_result": [result]}


supporting_document_verifier_agent = create_tool_agent(
    llm,
    tools=[],
)

async def supporting_document_verifier_node(state):
    # read the last message in the message history.
    input = {
        "messages": [SystemMessage(content=_load_prompt_template()[
        "SUPPORTING_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT"
    ])] +[state["messages"][-1]],
        "claim_form_json":state["claim_form_json"],
    }
    result = await supporting_document_verifier_agent.ainvoke(input)
    # respond back to the user.
    return {"supporting_document_verifier_result": [result]}


async def comms_node(state:ClaimFormScreeningTeamAgentState):
    doc_content = [c.content for c in state["document_verifier_result"] if isinstance(c,AIMessage)]
    supporting_doc_content = [c.content for c in state["supporting_document_verifier_result"] if isinstance(c,AIMessage)]

    team_mates = HumanMessage(
                content=(f"\n\nDocument Verification Result:\n{doc_content[-1]}\n\n"
                         f"Supporting Document Verification Result:\n{supporting_doc_content[-1]}"
                         f"the claimants form in JSON format: {state["claim_form_json"]}"
                )
            )
    return await summarizer(state,llm,_load_prompt_template()["PROCESS_CLERK_PROMPT"],team_mates,agentX)


# create options map for the supervisor output parser.
member_options = {member: member for member in members}

# create Enum object
MemberEnum = Enum("MemberEnum", member_options)


class Router(BaseModel):
    """
    Worker to route to the next step. If no workers are needed, route to FINISH.
    """

    next: MemberEnum


document_check_supervisor_node = create_supervisor_node(
    _load_prompt_template()["STIRRINGAGENTSYSTEMPROMPT"], llm, Router, members
)


# def router(state) -> Literal[*options]:
#     # This is the router
#     if state.get("next"):
#         return state.get("next")
#     else:
#         return '__end__'

document_check_builder = StateGraph(ClaimFormScreeningTeamAgentState)

document_check_builder.add_node("supervisor", document_check_supervisor_node)
document_check_builder.add_node(agent1, claims_document_verifier_node)
document_check_builder.add_node(agent2, supporting_document_verifier_node)
document_check_builder.add_node(agentX, comms_node)

# Define the control flow
document_check_builder.set_entry_point("supervisor")

# We want our workers to ALWAYS "report back" to the supervisor when done
document_check_builder.add_edge("supervisor", agent1)
document_check_builder.add_edge(agent1, agent2)
document_check_builder.add_edge(agent2, agentX)
document_check_builder.add_edge(agentX, END)

document_check_graph = document_check_builder.compile()
# if env_config.env == "local":
#     save_graph_mermaid(document_check_graph, output_file="display/doc_langgraph.png")
