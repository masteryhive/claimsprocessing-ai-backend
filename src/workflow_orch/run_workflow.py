from typing import Dict, Any
from colorama import init, Fore, Style
import textwrap
from sqlalchemy.orm import Session
from src.parsers.settlement_team_parser import extract_from_settlement_offer
from src.parsers.fraud_team_parser import extract_from_fraud_checks
from src.database.schemas import Task, TaskStatus
from src.database.db_ops import (
    save_claim_report_database,
    update_claim_report_database,
    update_claim_status_database,
)
from src.models.claim_processing import ProcessClaimTask, UpdateClaimsReportModel
from src.parsers.doc_team_parser import extract_from_claim_processing
from src.parsers.policy_review_team_parser import extract_from_policy_details
from src.parsers.parser import extract_claim_summary
from src.teams.stirring_agent import members
from langchain_core.messages import HumanMessage
from src.config.appconfig import env_config
from src.error_trace.errorlogger import system_logger

# Initialize colorama for cross-platform color support
init()

HEADER_WIDTH = 80

def print_header(text: str) -> None:
    if env_config.env == "local":
        """Print a styled header with a border."""
        print(f"\n{Fore.CYAN}{'=' * HEADER_WIDTH}")
        print(f"{text.center(HEADER_WIDTH)}")
        print(f"{'=' * HEADER_WIDTH}{Style.RESET_ALL}\n")


def print_section(title: str, content: str, indent: int = 2) -> None:
    if env_config.env == "local":
        """Print a formatted section with title and indented content."""
        print(f"{Fore.GREEN}➤ {title}{Style.RESET_ALL}")
        wrapped_content = textwrap.fill(
            content, width=76, initial_indent=" " * indent, subsequent_indent=" " * indent
        )
        print(f"{wrapped_content}\n")


def handle_agent_response(agent: str, messages: list, claim:dict, team_summaries: UpdateClaimsReportModel, claim_id: int, db: Session, x_tenant_id: str = None) -> UpdateClaimsReportModel:
    """Process and handle responses from agents."""
    try:
        content = [m.content for m in messages if isinstance(m, HumanMessage)]
        ai_message_content = content[0]
        # Ensure team_summaries is initialized
        team_summaries = team_summaries or UpdateClaimsReportModel()
        if agent == members[0]:
            update_claim_status_database(claim_id=claim_id, status="Examining claim form", x_tenant_id=x_tenant_id)
            print_header(f"{agent} Response")
            print_section(ai_message_content, "")
            doc_data = extract_from_claim_processing(ai_message_content)
            doc_data.update({"claimId": claim_id, "details": claim.get("incidentDetails")})
            save_claim_report_database(doc_data, x_tenant_id=x_tenant_id)
            team_summaries = UpdateClaimsReportModel(**doc_data)
            update_claim_status_database(claim_id=claim_id, status="Reviewing claim policy", x_tenant_id=x_tenant_id)
            return team_summaries
        elif agent == members[1]:
            print_header(f"{agent} Response")
            print_section(ai_message_content, "")
            policy_data = extract_from_policy_details(ai_message_content, team_summaries.discoveries)
            team_summaries=team_summaries.model_copy(update=policy_data)
            update_claim_report_database(claim_id, team_summaries, x_tenant_id=x_tenant_id)
            update_claim_status_database(claim_id=claim_id, status="Running fraud checks", x_tenant_id=x_tenant_id)
            return team_summaries
        elif agent == members[2]:
            print_header(f"{agent} Response")
            print_section(ai_message_content, "")
            fraud_checks_data = extract_from_fraud_checks(ai_message_content, team_summaries.discoveries)
            team_summaries=team_summaries.model_copy(update=fraud_checks_data)
            update_claim_report_database(claim_id, team_summaries, x_tenant_id=x_tenant_id)
            update_claim_status_database(claim_id=claim_id, status="Computing likely offer", x_tenant_id=x_tenant_id)
            return team_summaries
        elif agent == members[3]:
            print_header(f"{agent} Response")
            print_section(ai_message_content, "")
            settlement_offer_data = extract_from_settlement_offer(ai_message_content, team_summaries.discoveries)
            team_summaries=team_summaries.model_copy(update=settlement_offer_data)
            update_claim_report_database(claim_id, team_summaries, x_tenant_id=x_tenant_id)
            update_claim_status_database(claim_id=claim_id, status="Creating Report Summary", x_tenant_id=x_tenant_id)
            return team_summaries
        print(f"{Fore.CYAN}{'─' * HEADER_WIDTH}{Style.RESET_ALL}\n")
    except Exception as e:
        system_logger.error(error=f"[Tenant: {x_tenant_id}] Error in handle_agent_response: {str(e)}")


def control_workflow(
    db: Session,
    claim: dict,
    claim_id: int,
    claim_request: ProcessClaimTask,
    task: Task,
    process_call: Dict[str, Any],
    team_summaries: UpdateClaimsReportModel,
    endworkflow:bool,
    x_tenant_id: str = None
) -> UpdateClaimsReportModel:
    """Main function to handle workflow."""
    if "__end__" in process_call:
        return

    print_header("CO AI Workflow Status")
    agent = list(process_call.keys())[0]

    if agent == "summary_team":
        team_summaries = handle_summary_team(process_call, claim_id, team_summaries, db, task, x_tenant_id)
        endworkflow = True
    elif agent == "supervisor":
        next_agent = process_call["supervisor"]["next"]
        print(f"{Fore.MAGENTA}🔄 Task Assignment:{Style.RESET_ALL}")
        print(f"   Assigning task to: {Fore.WHITE}{next_agent}{Style.RESET_ALL}\n")
    else:
        messages = process_call[agent]["messages"]
        team_summaries = handle_agent_response(agent, messages, claim, team_summaries, claim_id, db, x_tenant_id)

    return team_summaries, endworkflow


def handle_summary_team(
    process_call: Dict[str, Any],
    claim_id: int,
    team_summaries: UpdateClaimsReportModel,
    db: Session,
    task: Task,
    x_tenant_id: str = None
) -> UpdateClaimsReportModel:
    """Handle the summary team process."""
    try:
        print_header("summary_team Response")
        update_claim_status_database(claim_id=claim_id, status="Preparing Report Summary", x_tenant_id=x_tenant_id)
        messages = process_call["summary_team"]["messages"]
        content = [m.content for m in messages if isinstance(m, HumanMessage)]
        print_section(content[0], "")
        claim_processing_summary = extract_claim_summary(content[0], team_summaries.discoveries)
        team_summaries=team_summaries.model_copy(update=claim_processing_summary)
        update_claim_report_database(claim_id, team_summaries, x_tenant_id=x_tenant_id)
        update_claim_status_database(claim_id=claim_id, status=claim_processing_summary["operationStatus"], x_tenant_id=x_tenant_id)
        # Update task record
        task.status = TaskStatus.COMPLETED
        db.commit()
        db.refresh(task)
        
        return team_summaries
    except Exception as e:
        system_logger.error(error=f"[Tenant: {x_tenant_id}] Error in handle_summary_team: {str(e)}")
