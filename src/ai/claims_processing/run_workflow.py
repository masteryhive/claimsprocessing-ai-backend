import json
import time
from typing import Dict, Any
from colorama import init, Fore, Style
import textwrap
from sqlalchemy.orm import Session
from src.database.schemas import Task, TaskStatus
from src.ai.resources.db_ops import (
    save_claim_report_database,
    update_claim_report_database,
    update_claim_status_database,
)
from src.datamodels.claim_processing import ProcessClaimTask
from src.ai.claims_processing.parsers.doc_team_parser import extract_from_claim_processing
from src.ai.claims_processing.parsers.policy_review_team_parser import extract_from_policy_details
from src.ai.claims_processing.parsers.parser import extract_claim_summary
from src.ai.claims_processing.stirring_agent import members
from langchain_core.messages import HumanMessage

# Initialize colorama for cross-platform color support
init()

HEADER_WIDTH = 80

def print_header(text: str) -> None:
    """Print a styled header with a border."""
    print(f"\n{Fore.CYAN}{'=' * HEADER_WIDTH}")
    print(f"{text.center(HEADER_WIDTH)}")
    print(f"{'=' * HEADER_WIDTH}{Style.RESET_ALL}\n")


def print_section(title: str, content: str, indent: int = 2) -> None:
    """Print a formatted section with title and indented content."""
    print(f"{Fore.GREEN}➤ {title}{Style.RESET_ALL}")
    wrapped_content = textwrap.fill(
        content, width=76, initial_indent=" " * indent, subsequent_indent=" " * indent
    )
    print(f"{wrapped_content}\n")


def handle_agent_response(agent: str, messages: list, claim:dict, team_summaries: dict, claim_id: int, db: Session) -> None:
    """Process and handle responses from agents."""
    content = [m.content for m in messages if isinstance(m, HumanMessage)]
    ai_message_content = content[0]

    if agent == members[0]:
        update_claim_status_database(claim_id=claim_id, status="Examining claim form")
        print_header(f"{agent} Response")
        print_section(ai_message_content, "")
        doc_data = extract_from_claim_processing(ai_message_content)
        doc_data.update({"claimId": claim_id, "details": claim.get("incidentDetails")})
        save_claim_report_database(doc_data)
        team_summaries.update({"discoveries": doc_data.get("discoveries"), "pre_report": doc_data})
    elif agent == members[1]:
        update_claim_status_database(claim_id=claim_id, status="Reviewing claim policy")
        print_header(f"{agent} Response")
        print_section(ai_message_content, "")
        policy_data = extract_from_policy_details(ai_message_content, team_summaries["discoveries"])
        team_summaries["pre_report"].update(policy_data)
        update_claim_report_database(claim_id, team_summaries["pre_report"])
    elif agent == members[2]:
        update_claim_status_database(claim_id=claim_id, status="Running fraud checks")
        print_header(f"{agent} Response")
        print_section(ai_message_content, "")
    
    print(f"{Fore.CYAN}{'─' * HEADER_WIDTH}{Style.RESET_ALL}\n")


def control_workflow(
    db: Session,
    claim: dict,
    claim_id: int,
    claim_request: ProcessClaimTask,
    task: Task,
    process_call: Dict[str, Any],
    team_summaries: dict,
) -> None:
    """Main function to handle workflow."""
    if "__end__" in process_call:
        return

    print_header("CO AI Workflow Status")
    agent = list(process_call.keys())[0]

    if agent == "summary_team":
        handle_summary_team(process_call, claim_id, team_summaries, db, task)
    elif agent == "supervisor":
        next_agent = process_call["supervisor"]["next"]
        print(f"{Fore.MAGENTA}🔄 Task Assignment:{Style.RESET_ALL}")
        print(f"   Assigning task to: {Fore.WHITE}{next_agent}{Style.RESET_ALL}\n")
    else:
        messages = process_call[agent]["messages"]
        handle_agent_response(agent, messages,claim, team_summaries, claim_id, db)


def handle_summary_team(
    process_call: Dict[str, Any],
    claim_id: int,
    team_summaries: dict,
    db: Session,
    task: Task,
) -> None:
    """Handle the summary team process."""
    update_claim_status_database(claim_id=claim_id, status="Creating Report Summary")
    messages = process_call["summary_team"]["messages"]
    content = [m.content for m in messages if isinstance(m, HumanMessage)]
    print_header("summary_team Response")
    update_claim_status_database(claim_id=claim_id, status="Preparing Report Summary")
    result = extract_claim_summary(content[0], team_summaries)
    update_claim_report_database(claim_id, result)
    # Update task record
    task.status = TaskStatus.COMPLETED
    db.commit()
    db.refresh(task)
    print_section(content[0], "")
    update_claim_status_database(claim_id=claim_id, status=result["operationStatus"])
