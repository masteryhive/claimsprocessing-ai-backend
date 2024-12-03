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
from src.ai.claims_processing.toolkit.tools import *
from src.ai.claims_processing.toolkit.fraud_tools import *
from ai.claims_processing.old.agents import *
from langgraph.graph import END, StateGraph, START
from langchain_google_vertexai import ChatVertexAI
from src.ai.claims_processing.toolkit import *
from src.utilities.helpers import load_yaml_file
from ai.claims_processing.teams.create_agent_utils import *


llm = ChatVertexAI(model_name="gemini-pro", kwargs={"temperature": 0.2})

agent1 = "claims_document_checker"
agent2 = "evidence_document_checker"
agent3 = "claims_preliminary_investigator"  # New agent added
agent4 = "claims_vehicle_investigator"
agent5 = "claims_fraud_risk_analyst"
agentX = "claims_adjuster_1"

members = [agent1, agent2, agent3, agent4, agent5, agentX]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path("src/ai/claims_processing/prompts/instruction.yaml")
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
            "CLAIMS_PRELIMINARY_INVESTIGATOR_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "CLAIMS_PRELIMINARY_INVESTIGATOR_AGENT_SYSTEM_PROMPT", ""
            ),
            "CLAIM_ADJUSTER_SUMMARY_PROMPT": yaml_data.get(
                "CLAIM_ADJUSTER_SUMMARY_PROMPT", ""
            ),
            "CLAIMS_VEHICLE_INVESTIGATOR_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "CLAIMS_VEHICLE_INVESTIGATOR_AGENT_SYSTEM_PROMPT", ""
            ),
            "CLAIMS_FRAUD_RISK_AGENT_SYSTEM_PROMPT": yaml_data.get(
                "CLAIMS_FRAUD_RISK_AGENT_SYSTEM_PROMPT", ""
            ),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")


claims_document_verifier_agent = create_tool_agent(
    llm=llm,
    tools=[claims_document_completeness],
    system_prompt=_load_prompt_template()[
        "CLAIMS_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT"
    ],
)

supporting_document_verifier_agent = create_tool_agent(
    llm=llm,
    tools=[supporting_document_understanding],
    system_prompt=_load_prompt_template()[
        "SUPPORTING_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT"
    ],
)


claims_preliminary_investigator_agent = create_tool_agent(
    llm=llm,
    tools=[
        claimant_exists,
        policy_status_check,
        item_insurance_check,
        item_pricing_benmarking,
        # item_pricing_evaluator,
    ],
    system_prompt=_load_prompt_template()[
        "CLAIMS_PRELIMINARY_INVESTIGATOR_AGENT_SYSTEM_PROMPT"
    ],
)

claims_vehicle_investigator_agent = create_tool_agent(
    llm=llm,
    tools=[
        drivers_license_status_check,
        rapid_policy_claims_check,
        vehicle_registration_match,
    ],
    system_prompt=_load_prompt_template()["CLAIMS_VEHICLE_INVESTIGATOR_AGENT_SYSTEM_PROMPT"],
)

claims_fraud_risk_analyst_agent = create_tool_analyst_agent(
    llm=llm,
    tools=[fraud_detection_tool],
    system_prompt=_load_prompt_template()["CLAIMS_FRAUD_RISK_AGENT_SYSTEM_PROMPT"],
)

claim_adjuster_1_agent = adjuster(
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
supporting_document_verifier_node = functools.partial(
    crew_nodes, crew_member=supporting_document_verifier_agent, name=agent2
)
claims_preliminary_investigator_node = functools.partial(
    crew_nodes, crew_member=claims_preliminary_investigator_agent, name=agent3
)
claims_vehicle_investigator_node = functools.partial(
    crew_nodes, crew_member=claims_vehicle_investigator_agent, name=agent4
)
claims_fraud_risk_analyst_node = functools.partial(
    crew_nodes, crew_member=claims_fraud_risk_analyst_agent, name=agent5
)

workflow.add_node(agent1, claims_document_verifier_node)
workflow.add_node(agent2, supporting_document_verifier_node)
workflow.add_node(agent3, claims_preliminary_investigator_node)
workflow.add_node(agent4, claims_vehicle_investigator_node)
workflow.add_node(agent5, claims_fraud_risk_analyst_node)
workflow.add_node(agentX, comms_node)

workflow.add_node("Supervisor", supervisor_chain)
# set it as entrypoint to the graph.
workflow.set_entry_point("Supervisor")

workflow.add_edge("Supervisor", agent1)
workflow.add_edge(agent1, agent2)
workflow.add_edge(agent2, agent3)
workflow.add_edge(agent3, agent4)
workflow.add_edge(agent4, agent5)
workflow.add_edge(agent5, agentX)
workflow.add_edge(agentX, END)

workflow.add_conditional_edges(
    "Supervisor", lambda x: x["next"], member_options.pop(agentX)
)

graph = workflow.compile()
