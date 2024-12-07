import json
import time
from typing import Dict, Any
from colorama import init, Fore, Style, Back
import textwrap
from sqlalchemy.orm import Session
from src.database.schemas import Task, TaskStatus
from src.ai.resources.db_ops import (
    save_claim_report_database,
    update_claim_report_database,
    update_claim_status_database,
)
from src.datamodels.claim_processing import CreateClaimsReport, ProcessClaimTask
from src.database.pd_db import create_claim_report
from src.ai.claims_processing.utilities.parser import (
    extract_claim_data,
    extract_claim_summary,
    extract_from_claim_processing,
    extract_from_policy_details,
)
from src.ai.claims_processing.stirring_agent import members
from langchain_core.messages import HumanMessage

# Initialize colorama for cross-platform color support
init()


def print_header(text: str) -> None:
    """Print a styled header with a border."""
    width = 80
    print(f"\n{Fore.CYAN}{'='*width}")
    print(f"{text.center(width)}")
    print(f"{'='*width}{Style.RESET_ALL}\n")


def print_section(title: str, content: str, indent: int = 2) -> None:
    """Print a formatted section with title and indented content."""
    print(f"{Fore.GREEN}➤ {title}{Style.RESET_ALL}")
    wrapped_content = textwrap.fill(
        content, width=76, initial_indent=" " * indent, subsequent_indent=" " * indent
    )
    print(f"{wrapped_content}\n")


def print_tool_info(tool: str, tool_input: str, log: str) -> None:
    """Print formatted tool information."""
    print(f"{Fore.YELLOW}⚙ Tool used:{Style.RESET_ALL} {tool}")
    print(f"{Fore.YELLOW}⮊ Data sent into tool:{Style.RESET_ALL} {tool_input}")
    print(f"{Fore.YELLOW}📝 Log:{Style.RESET_ALL}")
    # for line in log.split('\n'):
    #     print(f"   {line}")
    # print()


def control_workflow(
    db: Session,
    claim: dict,
    claim_id: int,
    claim_request: ProcessClaimTask,
    task: Task,
    process_call: Dict[str, Any],
    team_summaries: dict,
) -> None:
    """Main function to handle fancy printing of the workflow."""
    if "__end__" not in process_call:
        print_header("CO AI Workflow Status")
        # Print the current state
        # print_section("Current State", str(s))
        agent = list(process_call.keys())[0]
        if agent == "summary_team":
            time.sleep(0.4)
            update_claim_status_database(
                claim_id=claim_id, status="Creating Report Summary"
            )
            messages = process_call[agent]["messages"]
            print(messages)
            content = [m.content for m in messages if isinstance(m, HumanMessage)]
            print_header(f"{agent} Response")
            time.sleep(0.3)
            update_claim_status_database(
                claim_id=claim_id, status="Preparing Report Summary"
            )
            result = extract_claim_summary(content[0],team_summaries)
            update_claim_report_database(claim_id,result)
            # Update task record
            task.status = TaskStatus.COMPLETED
            db.commit()
            db.refresh(task)
            print_section(content[0], "")
            update_claim_status_database(
                claim_id=claim_id, status=result["operationStatus"]
            )
            return
        # Handle supervisor case
        if agent == "supervisor":
            next_agent = process_call["supervisor"]["next"]
            print(f"{Fore.MAGENTA}🔄 Task Assignment:{Style.RESET_ALL}")
            print(
                f"   Assigning task to: {Fore.WHITE} {next_agent} {Style.RESET_ALL}\n"
            )

        # Process agent history
        print_header(agent)

        if agent == members[0]:
            messages = process_call[agent]["messages"]
            content = [m.content for m in messages if isinstance(m, HumanMessage)]
            update_claim_status_database(
                claim_id=claim_id, status="Examining claim form"
            )
            # Print AI Message content
            ai_message_content = content[0]
            print_header(f"{agent} Response")
            print_section(ai_message_content, "")
            doc_data = extract_from_claim_processing(ai_message_content)
            discoveries = doc_data.get("discoveries")
            doc_data["claimId"] = claim_id
            doc_data["incidentDetails"] = claim["incidentDetails"]
            save_claim_report_database(doc_data)
            team_summaries["discoveries"] = discoveries
            team_summaries["doc"] = doc_data
            print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
        elif agent == members[1]:
            messages = process_call[agent]["messages"]
            content = [m.content for m in messages if isinstance(m, HumanMessage)]
            update_claim_status_database(
                claim_id=claim_id, status="Claim Form Examination Complete!"
            )
            time.sleep(0.5)
            update_claim_status_database(
                claim_id=claim_id, status="Reviewing claim policy"
            )
            # Print AI Message content
            policy_review_team_ai_message_content = content[0]
            print_header(f"{agent} Response")
            print_section(policy_review_team_ai_message_content, "")
            policy_data = extract_from_policy_details(
                policy_review_team_ai_message_content,
                team_summaries["discoveries"]
            )
            team_summaries["doc"].update(policy_data)
            update_claim_report_database(claim_id,team_summaries["doc"])
            print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
        elif agent == members[2]:
            update_claim_status_database(claim_id=claim_id, status="Policy checked!")
            time.sleep(0.3)
            update_claim_status_database(
                claim_id=claim_id, status="Running fraud checks"
            )
            messages = process_call[agent]["messages"]
            content = [m.content for m in messages if isinstance(m, HumanMessage)]
            fraud_detection_team_ai_message_content = content[0]
            print_header(f"{agent} Response")
            print_section(fraud_detection_team_ai_message_content, "")
            print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
