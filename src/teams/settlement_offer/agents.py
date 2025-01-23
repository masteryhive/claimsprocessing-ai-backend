from enum import Enum
import functools
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from pathlib import Path
from src.teams.settlement_offer.tools import *
from src.teams.create_agent_utils import crew_nodes
from src.ai_models.llm import llm
from src.teams.resources.gen_mermaid import save_graph_mermaid
from src.teams.create_agent import *
from langgraph.graph import END, StateGraph, START
from src.utilities.helpers import load_yaml_file
from src.config.appconfig import env_config


agent1 = "offer_analyst"
agentX = "team_task_summarizer"
members = [agent1, agentX]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path(
            "src/teams/settlement_offer/prompts/instruction.yaml"
        )
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
            
            "OFFER_ANALYST_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "OFFER_ANALYST_AGENT_SYSTEM_PROMPT", ""
            ),
            "PROCESS_CLERK_PROMPT": yaml_data.get("PROCESS_CLERK_PROMPT", ""),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")


offer_analyst_agent = create_tool_agent(
    llm=llm,
    tools=[determine_settlement_offer_range,determine_settlement_offer]
)

async def offer_analyst_node(state:dict):
    # read the last message in the message history.
    input = {
        "messages": [SystemMessage(content=_load_prompt_template()["OFFER_ANALYST_AGENT_SYSTEM_PROMPT"])] + [state["messages"][-1]],
        "claim_form_json":state["claim_form_json"],
    }
    result = await offer_analyst_agent.ainvoke(input)
    # respond back to the user.
    return {"offer_analyst_result": [result]}

async def comms_node(state:dict):
    offer_analyst = [c.content for c in state["offer_analyst_result"] if isinstance(c,AIMessage)]

    
    team_mates = HumanMessage(
                content=(f"\n\nClaim Offer Analysis Result:\n{offer_analyst[-1]}\n\n"
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


settlement_offer_supervisor_node = create_supervisor_node(
    _load_prompt_template()["STIRRINGAGENTSYSTEMPROMPT"], llm, Router, members
)


settlement_offer_builder = StateGraph(SettlementOfferTeamAgentState)


settlement_offer_builder.add_node("supervisor", settlement_offer_supervisor_node)
settlement_offer_builder.add_node(agent1, offer_analyst_node)
settlement_offer_builder.add_node(agentX, comms_node)

# Define the control flow
settlement_offer_builder.set_entry_point("supervisor")
# We want our workers to ALWAYS "report back" to the supervisor when done
settlement_offer_builder.add_edge("supervisor", agent1)
settlement_offer_builder.add_edge(agent1, agentX)
settlement_offer_builder.add_edge(agentX, END)

settlement_offer_graph = settlement_offer_builder.compile()
# if env_config.env == "local":
#     save_graph_mermaid(fraud_detection_graph, output_file="display/fraud_langgraph.png")
