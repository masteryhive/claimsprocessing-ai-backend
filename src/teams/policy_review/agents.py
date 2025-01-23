from enum import Enum
import functools
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from pathlib import Path
from src.teams.create_agent_utils import crew_nodes
from src.ai_models.llm import llm
from src.teams.resources.gen_mermaid import save_graph_mermaid
from src.teams.policy_review.tools import *
from src.teams.create_agent import *
from langgraph.graph import END, StateGraph, START
from src.utilities.helpers import load_yaml_file
from src.config.appconfig import env_config

agent1 = "policy_essential_data_retriever"
agent2 = "policy_period_verifier"
agent3 = "insurance_policy_verifier"
agentX = "team_task_summarizer"
members = [agent1, agent2,  agent3, agentX]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path(
            "src/teams/policy_review/prompts/instruction.yaml"
        )
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
                        "INSURANCE_CLAIM_POLICY_DATA": yaml_data.get(
                "INSURANCE_CLAIM_POLICY_DATA", ""
            ),
            "PERIOD_VERIFICATION": yaml_data.get(
                "PERIOD_VERIFICATION", ""
            ),
            "POLICY_VERIFICATION": yaml_data.get(
                "POLICY_VERIFICATION", ""
            ),
            "PROCESS_CLERK_PROMPT": yaml_data.get("PROCESS_CLERK_PROMPT", ""),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")

insurance_policy_essential_data_agent = create_tool_agent(
    llm=llm,
    tools=[retrieve_all_essential_details_from_policy]
)

async def insurance_policy_essential_data_node(state):
    # read the last message in the message history.
    input = {
        "messages": [SystemMessage(content=_load_prompt_template()["INSURANCE_CLAIM_POLICY_DATA"])] + [state["messages"][-1]],
        "claim_form_json":state["claim_form_json"],
    }
    result = await insurance_policy_essential_data_agent.ainvoke(input)
    # respond back to the user.
    return {"policy_essential_data_retriever_result": [result]}


insurance_policy_period_verifier_agent = create_tool_agent(
    llm=llm,
    tools=[
        check_if_this_claim_is_within_insurance_period,
        check_if_this_claim_is_reported_within_insurance_period,
    ]
)

async def insurance_policy_period_verifier_node(state):
        # read the last message in the message history.
    input = {
        "messages": [SystemMessage(content=_load_prompt_template()["PERIOD_VERIFICATION"])] + [state["messages"][-1]],
        "claim_form_json":state["claim_form_json"],
    }
    result = await insurance_policy_period_verifier_agent.ainvoke(input)
    # respond back to the user.
    return {"policy_period_verifier_result": [result]}


insurance_policy_verifier_agent = create_tool_agent(
    llm=llm,
    tools=[
        # check_if_the_incident_occurred_within_the_geographical_coverage,
        # check_if_the_damage_cost_does_not_exceed_authorised_repair_limit,
    ]
)

async def insurance_policy_verifier_node(state):
        # read the last message in the message history.
    input = {
        "messages": [SystemMessage(content=_load_prompt_template()["POLICY_VERIFICATION"])] + [state["messages"][-1]],
        "claim_form_json":state["claim_form_json"],
    }
    result = await insurance_policy_verifier_agent.ainvoke(input)
    # respond back to the user.
    return {"insurance_policy_verifier_result": [result]}



async def comms_node(state:PolicyReviewTeamAgentState):
    policy_essential_data = [c.content for c in state["policy_essential_data_retriever_result"] if isinstance(c,AIMessage)]
    policy_period_data = [c.content for c in state["policy_period_verifier_result"] if isinstance(c,AIMessage)]
    insurance_policy_data = [c.content for c in state["insurance_policy_verifier_result"] if isinstance(c,AIMessage)]
    
    team_mates = HumanMessage(
                content=(f"\n\nPolicy Essential Data Result:\n{policy_essential_data[-1]}\n\n"
                         f"Policy Period Verification Result:\n{policy_period_data[-1]}\n\n"
                         f"Insurance Policy Verification Result:\n{insurance_policy_data[-1]}"
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


policy_review_supervisor_node = create_supervisor_node(
    _load_prompt_template()["STIRRINGAGENTSYSTEMPROMPT"], llm, Router, members
)


# def router(state) -> Literal[*options]:
#     # This is the router
#     if state.get("next"):
#         return state.get("next")
#     else:
#         return '__end__'

policy_review_builder = StateGraph(PolicyReviewTeamAgentState)


policy_review_builder.add_node("supervisor", policy_review_supervisor_node)
policy_review_builder.add_node(agent1, insurance_policy_essential_data_node)
policy_review_builder.add_node(agent2, insurance_policy_period_verifier_node)
policy_review_builder.add_node(agent3, insurance_policy_verifier_node)
policy_review_builder.add_node(agentX, comms_node)

# Define the control flow
policy_review_builder.set_entry_point("supervisor")
# We want our workers to ALWAYS "report back" to the supervisor when done
policy_review_builder.add_edge("supervisor", agent1)
policy_review_builder.add_edge(agent1, agent2)
policy_review_builder.add_edge(agent2, agent3)
policy_review_builder.add_edge(agent3, agentX)
policy_review_builder.add_edge(agentX, END)
# policy_review_builder.add_conditional_edges(  ## sup choice to go to email, or LLM or bye based on result of function decide_next_node
#     "supervisor",
#     router,
#     {members[0]:members[0],members[1]:members[1],
#          "__end__": END
#     },
# )
policy_review_graph = policy_review_builder.compile()
# if env_config.env == "local":
#     save_graph_mermaid(policy_review_graph, output_file="display/policy_langgraph.png")
