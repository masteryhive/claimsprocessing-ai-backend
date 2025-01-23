from enum import Enum
import functools
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from pathlib import Path
from src.teams.create_agent_utils import crew_nodes
from src.ai_models.llm import llm
from src.teams.resources.gen_mermaid import save_graph_mermaid
from src.teams.fraud_detection.tools import *
from src.teams.create_agent import *
from langgraph.graph import END, StateGraph, START
from src.utilities.helpers import load_yaml_file
from src.config.appconfig import env_config
from langchain_core.messages import AIMessage


agent1 = "claims_form_fraud_investigator"  # New agent added
agent2 = "vehicle_fraud_investigator"
agent3 = "damage_cost_fraud_investigator"
agent4 = "fraud_risk_analyst"
agentX = "team_task_summarizer"
members = [agent1, agent2, agent3, agent4, agentX]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path("src/teams/fraud_detection/prompts/instruction.yaml")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
            "CLAIMS_FORM_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "CLAIMS_FORM_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT", ""
            ),
            "VEHICLE_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "VEHICLE_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT", ""
            ),
            "DAMAGE_COST_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "DAMAGE_COST_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT", ""
            ),
            "FRAUD_RISK_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "FRAUD_RISK_AGENT_SYSTEM_PROMPT", ""
            ),
            "PROCESS_CLERK_PROMPT": yaml_data.get("PROCESS_CLERK_PROMPT", ""),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")


claim_form_fraud_investigator_agent = create_tool_agent(
    llm=llm,
    tools=[
        verify_this_claimant_exists_as_a_customer,
        investigate_if_this_claimant_is_attempting_a_rapid_policy_claim,
    ],
    system_prompt=_load_prompt_template()[
        "CLAIMS_FORM_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT"
    ],
)

vehicle_fraud_investigator_agent = create_tool_agent(
    llm=llm,
    tools=[
        validate_if_this_is_a_real_vehicle,
        # check_NIID_database_,
        # ssim,
    ],
    system_prompt=_load_prompt_template()[
        "VEHICLE_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT"
    ],
)

damage_cost_fraud_investigator_agent = create_tool_agent(
    llm=llm,
    tools=[
        #item_cost_price_benchmarking_in_local_market,
          # item_pricing_evaluator
           ],
    system_prompt=_load_prompt_template()[
        "DAMAGE_COST_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT"
    ],
)

fraud_risk_analyst_agent = create_tool_agent(
    llm=llm,
    tools=[],
    system_prompt=_load_prompt_template()["FRAUD_RISK_AGENT_SYSTEM_PROMPT"],
)


fraud_detection_clerk_agent = summarizer(
    _load_prompt_template()["PROCESS_CLERK_PROMPT"], llm
)


def comms_node(state):
    # read the last message in the message history.
    claim_form_fraud = [c.content for c in state["claims_form_fraud_investigator_result"] if isinstance(c,AIMessage)]
    vehicle_fraud = [c.content for c in state["vehicle_fraud_investigator_result"] if isinstance(c,AIMessage)]
    damage_cost_fraud = [c.content for c in state["damage_cost_fraud_investigator_result"] if isinstance(c,AIMessage)]
    fraud_risk = [c.content for c in state["fraud_risk_analyst_result"] if isinstance(c,AIMessage)]
    # print(vehicle_fraud)
    team_mates =(f"\n\nClaim Form Fraud Investigation Result:\n{claim_form_fraud[-1]}\n\n"
                         f"Vehicle Fraud Investigation Result:\n{vehicle_fraud[-1]}\n\n"
                         f"Damage Cost Fraud Investigation Result:\n{damage_cost_fraud[-1]}\n\n"
                         f"Fraud Risk Analysis Result:\n{fraud_risk[-1]}"
                         f"the claimants form in JSON format: {state["claim_form_json"]}")
    input = {
        "messages": [state["messages"][-1]+team_mates],
        "agent_history": state["agent_history"],
        "claim_form_json":state["claim_form_json"]
    }

    result = fraud_detection_clerk_agent.invoke(input)
    # respond back to the user.
    return {"messages": [result]}


# create options map for the supervisor output parser.
member_options = {member: member for member in members}

# create Enum object
MemberEnum = Enum("MemberEnum", member_options)


class Router(BaseModel):
    """
    Worker to route to the next step. If no workers are needed, route to FINISH.
    """

    next: MemberEnum


fraud_detection_supervisor_node = create_supervisor_node(
    _load_prompt_template()["STIRRINGAGENTSYSTEMPROMPT"], llm, Router, members
)


fraud_detection_builder = StateGraph(FraudTeamAgentState)

claim_form_fraud_investigator_node = functools.partial(
    crew_nodes, crew_member=claim_form_fraud_investigator_agent, name=agent1
)
vehicle_fraud_investigator_node = functools.partial(
    crew_nodes, crew_member=vehicle_fraud_investigator_agent, name=agent2
)
damage_cost_fraud_investigator_node = functools.partial(
    crew_nodes, crew_member=damage_cost_fraud_investigator_agent, name=agent3
)
fraud_risk_analyst_node = functools.partial(
    crew_nodes, crew_member=fraud_risk_analyst_agent, name=agent4
)


fraud_detection_builder.add_node("supervisor", fraud_detection_supervisor_node)
fraud_detection_builder.add_node(agent1, claim_form_fraud_investigator_node)
fraud_detection_builder.add_node(agent2, vehicle_fraud_investigator_node)
fraud_detection_builder.add_node(agent3, damage_cost_fraud_investigator_node)
fraud_detection_builder.add_node(agent4, fraud_risk_analyst_node)
fraud_detection_builder.add_node(agentX, comms_node)

# Define the control flow
fraud_detection_builder.set_entry_point("supervisor")
# We want our workers to ALWAYS "report back" to the supervisor when done
fraud_detection_builder.add_edge("supervisor", agent1)
fraud_detection_builder.add_edge(agent1, agent2)
fraud_detection_builder.add_edge(agent2, agent3)
fraud_detection_builder.add_edge(agent3, agent4)
fraud_detection_builder.add_edge(agent4, agentX)
fraud_detection_builder.add_edge(agentX, END)

fraud_detection_graph = fraud_detection_builder.compile()
# if env_config.env == "local":
#     save_graph_mermaid(fraud_detection_graph, output_file="display/fraud_langgraph.png")
