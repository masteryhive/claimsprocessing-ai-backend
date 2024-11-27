from pathlib import Path
from enum import Enum
import operator
from typing import Annotated
from pydantic import BaseModel
from typing_extensions import TypedDict
from langchain_google_vertexai import ChatVertexAI
from enum import Enum
import functools, operator, vertexai
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from src.ai.claims_processing.agents import *
from langgraph.graph import END, StateGraph, START
from langchain_google_vertexai import ChatVertexAI
from src.ai.claims_processing.toolkit import *
from src.utilities.helpers import load_yaml_file
from src.ai.claims_processing.agent_utils import *


llm = ChatVertexAI(model_name="gemini-pro")

agent1 = "claims_processor"
agent2 = "claims_preliminary_investigator"
agent3 = "claims_vehicle_investigator"
agent4 = "claims_fraud_risk_analyst"
agent5 = "claims_adjuster_1"

members = [agent1, agent2, agent3, agent4,agent5]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path(
            "src/ai/claims_processing/prompts/instruction.yaml"
        )
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
            "CLAIMSDOCUMENTVERIFIERAGENTSYSTEMPROMPT": yaml_data.get(
                "CLAIMSDOCUMENTVERIFIERAGENTSYSTEMPROMPT", ""
            ),
            "CLAIMSINVESTIGATORAGENTSYSTEMPROMPT": yaml_data.get(
                "CLAIMSINVESTIGATORAGENTSYSTEMPROMPT", ""
            ),
            "CLAIMADJUSTER1SYSTEMPROMPT": yaml_data.get(
                "CLAIMADJUSTER1SYSTEMPROMPT", ""
            ),
        "CLAIMSVEHICLEINVESTIGATORAGENTSYSTEMPROMPT": yaml_data.get(
            "CLAIMSVEHICLEINVESTIGATORAGENTSYSTEMPROMPT", ""
        ),
        "CLAIMSFRAUDRISKAGENTSYSTEMPROMPT": yaml_data.get(
            "CLAIMSFRAUDRISKAGENTSYSTEMPROMPT", ""
        ),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")


claims_document_verifier_agent = create_tool_agent(
    llm=llm,
    tools=[claims_document_completeness,supporting_document_understanding],
    system_prompt=_load_prompt_template()["CLAIMSDOCUMENTVERIFIERAGENTSYSTEMPROMPT"],
)

claims_preliminary_investigator_agent = create_tool_agent(
    llm=llm,
    tools=[
        claimant_exists,
        policy_status_check,
        item_insurance_check,
        item_pricing_benmarking,
        item_pricing_evaluator,
    ],
    system_prompt=_load_prompt_template()["CLAIMSINVESTIGATORAGENTSYSTEMPROMPT"],
)

claims_vehicle_investigator_agent = create_tool_agent(
    llm=llm,
    tools=[
        drivers_license_status_check,
        rapid_policy_claims_check,
        vehicle_registration_match,
    ],
    system_prompt=_load_prompt_template()["CLAIMSVEHICLEINVESTIGATORAGENTSYSTEMPROMPT"],
)

claims_fraud_risk_analyst_agent = create_tool_agent(
    llm=llm,
    tools=[
        fraud_detection_tool
    ],
    system_prompt=_load_prompt_template()["CLAIMSFRAUDRISKAGENTSYSTEMPROMPT"],
)

claim_adjuster_1_agent = adjuster(
    _load_prompt_template()["CLAIMADJUSTER1SYSTEMPROMPT"], llm
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


supervisor_chain = create_stirring_agent(
    _load_prompt_template()["STIRRINGAGENTSYSTEMPROMPT"], llm, SupervisorOutput, members
)

# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]


workflow = StateGraph(AgentState)

claims_document_verifier_node = functools.partial(
    crew_nodes, crew_member=claims_document_verifier_agent, name=agent1
)
claims_preliminary_investigator_node = functools.partial(
    crew_nodes, crew_member=claims_preliminary_investigator_agent, name=agent2
)
claims_vehicle_investigator_node = functools.partial(
    crew_nodes,crew_member=claims_vehicle_investigator_agent,name=agent3
)
claims_fraud_risk_analyst_node = functools.partial(
    crew_nodes,crew_member=claims_fraud_risk_analyst_agent,name=agent4
)
workflow.add_node(agent1, claims_document_verifier_node)
workflow.add_node(agent2, claims_preliminary_investigator_node)
workflow.add_node(agent3, claims_vehicle_investigator_node)
workflow.add_node(agent4, comms_node)

workflow.add_node("Supervisor", supervisor_chain)
# set it as entrypoint to the graph.
workflow.set_entry_point("Supervisor")

workflow.add_edge("Supervisor", agent1)
workflow.add_edge(agent1, agent2)
workflow.add_edge(agent2, agent3)
workflow.add_edge(agent3, agent4)
workflow.add_edge(agent4, END)

workflow.add_conditional_edges(
    "Supervisor", lambda x: x["next"], member_options.pop(agent4)
)

graph = workflow.compile()
