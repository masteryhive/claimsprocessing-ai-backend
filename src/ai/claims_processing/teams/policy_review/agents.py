from enum import Enum
import functools
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from pathlib import Path
from src.ai.claims_processing.teams.create_agent_utils import crew_nodes
from src.ai.claims_processing.llm import llm
from src.ai.resources.gen_mermaid import save_graph_mermaid
from src.ai.claims_processing.teams.policy_review.tools import *
from src.ai.claims_processing.teams.create_agent import *
from langgraph.graph import END, StateGraph, START
from src.utilities.helpers import load_yaml_file

agent1 = "insurance_policy_essential_data_retriever"
agent2 = "insurance_policy_verifier"
agentX = "team_task_summarizer"
members = [agent1,agent2, agentX]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path("src/ai/claims_processing/teams/policy_review/prompts/instruction.yaml")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
            "INSURANCE_CLAIM_VERIFICATION": yaml_data.get(
                "INSURANCE_CLAIM_VERIFICATION", ""
            ),
        "INSURANCE_CLAIM_POLICY_DATA": yaml_data.get("INSURANCE_CLAIM_POLICY_DATA", ""),
        "PROCESS_CLERK_PROMPT": yaml_data.get("PROCESS_CLERK_PROMPT", ""),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")



insurance_policy_verifier_agent = create_tool_agent(
    llm=llm,
    tools=[check_if_claim_is_within_insurance_period,check_if_claim_is_reported_within_insurance_period,
           check_geographical_coverage,check_premium_coverage],
    system_prompt=_load_prompt_template()[
        "INSURANCE_CLAIM_VERIFICATION"
    ],
)

insurance_policy_essential_data_agent = create_tool_agent(
    llm=llm,
    tools=[provide_policy_details],
    system_prompt=_load_prompt_template()[
        "INSURANCE_CLAIM_POLICY_DATA"
    ],
)


policy_review_clerk_agent = summarizer(
    _load_prompt_template()["PROCESS_CLERK_PROMPT"], llm
)

def comms_node(state):
    # read the last message in the message history.
    input = {
        "messages": [state["messages"][-1]],
        "agent_history": state["agent_history"],
    }
    result = policy_review_clerk_agent.invoke(input)
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

policy_review_supervisor_node = create_supervisor_node(
    _load_prompt_template()["STIRRINGAGENTSYSTEMPROMPT"], llm, Router, members
)



# def router(state) -> Literal[*options]:
#     # This is the router
#     if state.get("next"):
#         return state.get("next")
#     else:
#         return '__end__'

policy_review_builder = StateGraph(AgentState)

insurance_policy_essential_data_node = functools.partial(
    crew_nodes, crew_member=insurance_policy_essential_data_agent, name=agent1
)
insurance_policy_verifier_node = functools.partial(
    crew_nodes, crew_member=insurance_policy_verifier_agent, name=agent2
)

policy_review_builder.add_node("supervisor", policy_review_supervisor_node)
policy_review_builder.add_node(agent1, insurance_policy_essential_data_node)
policy_review_builder.add_node(agent2, insurance_policy_verifier_node)
policy_review_builder.add_node(agentX, comms_node)

# Define the control flow
policy_review_builder.set_entry_point("supervisor")
# We want our workers to ALWAYS "report back" to the supervisor when done
policy_review_builder.add_edge("supervisor",agent1)
policy_review_builder.add_edge(agent1, agent2)
policy_review_builder.add_edge(agent2, agentX)
policy_review_builder.add_edge(agentX, END)
# policy_review_builder.add_conditional_edges(  ## sup choice to go to email, or LLM or bye based on result of function decide_next_node
#     "supervisor",
#     router,
#     {members[0]:members[0],members[1]:members[1],
#          "__end__": END
#     },
# )
policy_review_graph = policy_review_builder.compile()
# save_graph_mermaid(policy_review_graph,output_file="display/policy_langgraph.png")
