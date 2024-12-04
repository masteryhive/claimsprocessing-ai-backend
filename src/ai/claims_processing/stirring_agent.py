
from pydantic import BaseModel
from src.ai.claims_processing.llm import llm
from src.ai.resources.gen_mermaid import save_graph_mermaid
from src.ai.claims_processing.teams.document_processing.agents import (
    document_check_graph,
)
from src.config.settings import get_setting
from src.ai.claims_processing.teams.create_agent import (
    AgentState,
    create_supervisor_node,
)
from src.ai.claims_processing.teams.policy_review.agents import policy_review_graph
from src.ai.claims_processing.teams.report.agents import report_graph
from src.ai.claims_processing.teams.document_processing.agents import (
    document_check_graph,
)
from typing import Literal
from langgraph.graph import StateGraph,  START, END
from langchain_core.messages import HumanMessage, AIMessage

# Get application settings
settings = get_setting()

members = ["claim_form_screening_team", "policy_review_team", "summary_team"]

options = ["FINISH"] + members

# system_prompt = """You are a claims processing supervisor responsible for managing a conversation between the following departmental teams: {members}. Your primary objective is to efficiently coordinate tasks while minimizing unnecessary back-and-forth communication.


# Operational Hierarchy:
# STAGE 1 - Document Checking

# Assign the claim_form_screening_team to verify the completeness and validity of documents and supporting evidence.
# If the claim_form_screening_team reports missing documents or inappropriate evidence, immediately skip to STAGE 3.
# If all documents are valid and complete, skip directly to STAGE 2.

# STAGE 3 - Operations Summary

# Assign the summary_team to prepare a comprehensive report summarizing the status of operations from all teams.
# Provide the summary_team with the claimant's data for inclusion in the report.
# FINISH

# When the summary_team completes their report, respond with "FINISH" to indicate the process is complete.
# Instructions:
# Do not engage in unnecessary conversations or revalidate previous results.
# Accept the claim_form_screening_team's report as-is and transition directly to the appropriate next stage.
# Given the task and responses below, determine the next team to act based on the hierarchy and report outcomes.
# Always respond with one of the following options: {options}.
# Additional Guidelines:
# If the claim_form_screening_team identifies issues, skip STAGE 2 and proceed directly to STAGE 3 for reporting.
# Avoid redundant communication with teams that have already provided their results.
# Do not use special characters like *, #, etc., in your response.
# Example Workflow:
# STAGE 1:

# claim_form_screening_team responds: "Documents are complete and valid. Status: Verified."
# Skip to policy_review_team for STAGE 2.
# STAGE 2:

# policy_review_team responds: "Policy is valid and active. Status: Approved."
# Proceed to summary_team for STAGE 3.
# STAGE 3:

# summary_team responds: "Operations report prepared. Status: Completed."
# Respond with "FINISH".
# Handling Issues:

# If the claim_form_screening_team reports missing/incomplete documents, skip STAGE 2 and proceed directly to the summary_team for a report.
# If the policy_review_team identifies any policy issues, proceed immediately to the summary_team to create a report and stop further processing.

# Given the following task, respond with the team to act next. Each team will perform a task and respond with their results and status. 
# \n{format_instructions}\n
# """

system_prompt = """ Claims Processing Workflow Instructions

Role: Claims Processing Supervisor

As a claims processing supervisor, your role is to efficiently coordinate tasks among three departmental teams:{members}.

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

2. Summary Team
   - Receives the all the team's response
   - Create a concise summary of all the team's findings
   - Highlight key issues including missing document types, policy essential details, policy verification reports etc.
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
to the summary team before closing the task.

Given the following task and conversation history, the next worker to act MUST follow this flow: 
 - claim_form_screening_team -> policy_review_team -> summary_team.
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
        }
    )
    return {
        "messages": [
            HumanMessage(
                content=response["messages"][-1].content, name="policy_review_team"
            )
        ]
    }


def call_summary_team(state: AgentState) -> AgentState:
    response = report_graph.invoke(
        {
            "messages": [state["messages"][-1]],
            "agent_history": state["agent_history"],
        }
    )
    return {
        "messages": [
            HumanMessage(content=response["messages"][-1].content, name="summary_team")
        ]
    }


def router(state) -> Literal[*options]:
    print(state)
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
super_builder.add_node(members[2], call_summary_team)
# Define the control flow
super_builder.add_edge(START, "supervisor")
# We want our teams to ALWAYS "report back" to the top-level supervisor when done
super_builder.add_edge("supervisor",members[0])
super_builder.add_edge(members[0], members[1])
super_builder.add_edge(members[1], members[2])
super_builder.add_edge(members[2], END)

#super_builder.add_edge("supervisor", END)
# super_builder.add_conditional_edges(  ## sup choice to go to email, or LLM or bye based on result of function decide_next_node
#     "supervisor",
#     router,
#     {
#         members[0]: members[0],
#         members[1]: members[1],
#         members[2]: members[2],
#         "__end__": END,
#     },
# )

super_graph = super_builder.compile()
# save_graph_mermaid(super_graph, output_file="display/super_langgraph.png")