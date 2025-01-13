from pydantic import BaseModel
from ai_models.llm import llm
from config.appconfig import env_config
from teams.resources.gen_mermaid import save_graph_mermaid
from teams.document_processing.agents import (
    document_check_graph,
)
from teams.create_agent import (
    AgentState,
    create_supervisor_node,
)
from teams.policy_review.agents import policy_review_graph
from teams.fraud_detection.agents import fraud_detection_graph
from teams.settlement_offer.agents import settlement_offer_graph
from teams.report.agents import report_graph
from teams.document_processing.agents import (
    document_check_graph,
)
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage



members = [
    "claim_form_screening_team",
    "policy_review_team",
    "fraud_detection_team",
    "settlement_offer_team",
    "summary_team",
]

options = ["FINISH"] + members

system_prompt = """
Role: Claims Processing Supervisor

As a claims processing supervisor, your role is to efficiently coordinate tasks among four departmental teams:{members}.

Workflow Steps:
1. Claims Form Screening Team
   - First action: Screen the submitted claims documents
   - If documents are incomplete or missing, report the specific deficiencies
   - Do NOT request additional information or clarify further

2. Policy Review Team
   - Receives the screening team's response
   - Verify the validity and status of the insurance policy
   - Ensure all policy terms are met and the policy is active
   - Report any discrepancies or issues found during the review
   - If issues are found, proceed directly to the summary team for reporting
   - Do NOT request additional information or clarify further

3. Fraud Detection Team
   - Receives the policy review team's response
   - Conduct a thorough investigation to identify any fraudulent activities
   - Utilize available tools to verify claimant identity, vehicle information, and policy details
   - Report any suspicious findings or confirm the legitimacy of the claim
   - If fraud is detected, proceed directly to the summary team for reporting
   - Do NOT request additional information or clarify further

4. Settlement Offer Team
   - Receives the all the team's response
   - Analyze the claim details, policy information and fraud score.
   - Determine a fair settlement offer based on the provided data
   - Utilize available tools to calculate the settlement offer range
   - Report the proposed settlement offer and any considerations
   - Do NOT request additional information or clarify further

4. Summary Team
   - Receives the all the team's response
   - Create a concise summary of all the team's findings
   - Highlight key issues including missing document types, policy essential details, policy verification reports etc.
   - Summarize findings from the fraud detection team
   - Include any identified fraudulent activities or confirm the legitimacy of the claim
   - Highlight any discrepancies or suspicious findings
   - Prepare a clear, professional summary for final review

3. Closure
   - You MUST ONLY respond with "FINISH", after the summary team completes their task.
   
Key Principles:
- Maintain a structured, systematic approach
- Ensure clear communication between teams
- Prioritize efficiency and accuracy
- Provide actionable insights for claims resolution

Teams Must:
- Provide precise, actionable information
- Avoid unnecessary back-and-forth communication
- Focus on document completeness and critical information

Final Objective: Streamline the claims processing workflow and present a clear summary to the reviewing human.

You always need the summary team to keep your work astute and presentable.

You MUST route:
 1. the screening team's response
 2. the policy review team's response
 3. the fraud detection team's response
 4. the settlement offer team's response
to the summary team before closing the task.

Given the following task and conversation history, the next worker to act MUST follow this flow: claim_form_screening_team -> policy_review_team -> fraud_detection_team -> summary_team.
Select one of: {options} 
\n{format_instructions}\n
"""


class Router(BaseModel):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal[*options]


teams_supervisor_node = create_supervisor_node(system_prompt, llm, Router, members)


def call_doc_team(state: AgentState) -> AgentState:
    response = document_check_graph.invoke(
        {
            "messages": [state["messages"][-1]],
            "agent_history": state["agent_history"],
            "claim_form_json": state["claim_form_json"],
        }
    )
    return {
        "messages": [
            HumanMessage(content=response["messages"][1].content, name=members[0])
        ]
    }


def call_pol_team(state: AgentState) -> AgentState:
    response = policy_review_graph.invoke(
        {
            "messages": [state["messages"][-1]],
            "agent_history": state["agent_history"],
            "claim_form_json": state["claim_form_json"],
        }
    )
    return {
        "messages": [
            HumanMessage(
                content=response["messages"][-1].content, name=members[1]
            )
        ]
    }


def call_fraud_team(state: AgentState) -> AgentState:
    response = fraud_detection_graph.invoke(
        {
            "messages": [state["messages"][-1]],
            "agent_history": state["agent_history"],
            "claim_form_json": state["claim_form_json"],
        }
    )
    return {
        "messages": [
            HumanMessage(content=response["messages"][-1].content, name=members[2])
        ]
    }


def call_settlement_offer_team(state: AgentState) -> AgentState:
    response = settlement_offer_graph.invoke(
        {
            "messages": [state["messages"][-1]],
            "agent_history": state["agent_history"],
            "claim_form_json": state["claim_form_json"],
        }
    )
    return {
        "messages": [
            HumanMessage(content=response["messages"][-1].content, name=members[3])
        ]
    }


def call_summary_team(state: AgentState) -> AgentState:
    response = report_graph.invoke(
        {
            "messages": [state["messages"][-1]],
            "agent_history": state["agent_history"],
            "claim_form_json": state["claim_form_json"],
        }
    )
    return {
        "messages": [
            HumanMessage(content=response["messages"][-1].content, name=members[4])
        ]
    }


def router(state) -> Literal[*options]:
    # if state.get("summary_team"):
    #     if HumanMessage.content in state.get("summary_team")["messages"]:
    #         return "__end__"
    if state.get("next") != "FINISH":
        return state.get("next")
    return "__end__"


# Define the graph.
super_builder = StateGraph(AgentState)
super_builder.add_node("supervisor", teams_supervisor_node)
super_builder.add_node(members[0], call_doc_team)
super_builder.add_node(members[1], call_pol_team)
super_builder.add_node(members[2], call_fraud_team)
super_builder.add_node(members[3], call_settlement_offer_team)
super_builder.add_node(members[4], call_summary_team)

# Define the control flow
super_builder.add_edge(START, "supervisor")
# We want our teams to ALWAYS "report back" to the top-level supervisor when done
super_builder.add_edge("supervisor", members[0])
super_builder.add_edge(members[0], members[1])
super_builder.add_edge(members[1], members[2])
super_builder.add_edge(members[2], members[3])
super_builder.add_edge(members[3], members[4])
super_builder.add_edge(members[4], END)

super_graph = super_builder.compile()
# if env_config.env == "local":
#     save_graph_mermaid(super_graph, output_file="display/super_langgraph.png")
