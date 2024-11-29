import time
from typing import Dict, Any
from colorama import init, Fore, Style, Back
import textwrap
from sqlalchemy.orm import Session
from src.database.schemas import Task, TaskStatus
from src.ai.resources.db_ops import save_claim_report_database, update_claim_status_database
from src.datamodels.co_ai import AIClaimsReport, ProcessClaimTask
from src.database.pd_db import create_claim_report
from src.ai.claims_processing.utilities.parser import extract_claim_data, extract_claim_summary
from src.config.db_setup import SessionLocal
from src.ai.claims_processing.llm_flow import members

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
        content, 
        width=76, 
        initial_indent=' '*indent,
        subsequent_indent=' '*indent
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

def run_coordinator(db: Session,claim_id:str,claim_request: ProcessClaimTask,task: Task,s: Dict[str, Any], data: Dict[str, Any]) -> None:
    """Main function to handle fancy printing of the workflow."""
    if "__end__" not in s:
        print_header("CO AI Workflow Status")
        # Print the current state
        # print_section("Current State", str(s))
        agent = list(s.keys())[0]
        print(agent)
        if agent == "claims_adjuster_1":
            update_claim_status_database(claim_id=claim_id,status="Vehicle fraud checks completed!")
            time.sleep(3)
            update_claim_status_database(claim_id=claim_id,status="Calculating risk")
            time.sleep(3)
            update_claim_status_database(claim_id=claim_id,status="Generating fraud score")
            time.sleep(4)
            update_claim_status_database(claim_id=claim_id,status="Creating Report Summary")
            messages = data[agent]['messages']
            for message in messages:
                print_header(f"{agent} Response")
                time.sleep(2)
                update_claim_status_database(claim_id=claim_id,status="Preparing Report Summary")
                result = extract_claim_summary(message.content)
                save_claim_report_database({
                    "claimId": claim_id,
                    "fraudScore": result['fraud_score'],
                    "fraudIndicators": result['fraud_indicators'],
                    "aiRecommendation": result['ai_recommendation'],
                    "policyReview": result['policy_review'],
                    "evidenceProvided": result['evidence_provided'],
                    "coverageStatus": result['coverage_status'],
                    "typeOfIncident": result['type_of_incident'],
                    "details": result['details']
                })
                # Update task record
                task.status = TaskStatus.COMPLETED
                db.commit()
                db.refresh(task)
                print_section(message.content,"")
                update_claim_status_database(claim_id=claim_id,status=result['operationStatus'])
                return
        # Handle supervisor case
        if agent == "Supervisor":
            next_agent = s["Supervisor"]['next']
            print(f"{Fore.MAGENTA}🔄 Task Assignment:{Style.RESET_ALL}")
            print(f"   Assigning task to: {Fore.WHITE} {next_agent} {Style.RESET_ALL}\n")
            return

        # Process agent history
        print_header(agent)
        agent_history = data[agent]['agent_history']
        if agent == members[0]:
            update_claim_status_database(claim_id=claim_id,status="Examining claim form")
            for entry in agent_history:
                intermediate_steps = entry.additional_kwargs.get('intermediate_steps', [])
                
                if intermediate_steps:
                    print_header("Tool Executions")
                    for step in intermediate_steps:
                        print_tool_info(
                            step[0].tool,
                            step[0].tool_input,
                            step[0].log
                        )
                
                # Print AI Message content
                ai_message_content = entry.content
                print_header(f"{agent} Response")
                print_section(ai_message_content,"")
                
                print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
                return
        elif agent == members[1]:
            update_claim_status_database(claim_id=claim_id,status="Claim Form Examination Complete!")
            time.sleep(0.6)
            update_claim_status_database(claim_id=claim_id,status="Evaluating Supporing docs")
            for entry in agent_history:
                intermediate_steps = entry.additional_kwargs.get('intermediate_steps', [])
                
                if intermediate_steps:
                    print_header("Tool Executions")
                    for step in intermediate_steps:
                        print_tool_info(
                            step[0].tool,
                            step[0].tool_input,
                            step[0].log
                        )
                
                # Print AI Message content
                ai_message_content = entry.content
                print_header(f"{agent} Response")
                print_section(ai_message_content,"")
                print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
                return
        elif agent == members[2]:
            update_claim_status_database(claim_id=claim_id,status="Evaluation Complete!")
            time.sleep(1)
            update_claim_status_database(claim_id=claim_id,status="Running document fraud checks")
            for entry in agent_history:
                intermediate_steps = entry.additional_kwargs.get('intermediate_steps', [])
                
                if intermediate_steps:
                    print_header("Tool Executions")
                    for step in intermediate_steps:
                        print_tool_info(
                            step[0].tool,
                            step[0].tool_input,
                            step[0].log
                        )
                
                # Print AI Message content
                ai_message_content = entry.content
                print_header(f"{agent} Response")
                print_section(ai_message_content,"")
                
                print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
                return
        elif agent == members[3]:
            update_claim_status_database(claim_id=claim_id,status="Document fraud checks Done!")
            time.sleep(1)
            update_claim_status_database(claim_id=claim_id,status="Running vehicle fraud checks")
            for entry in agent_history:
                intermediate_steps = entry.additional_kwargs.get('intermediate_steps', [])
                
                if intermediate_steps:
                    print_header("Tool Executions")
                    for step in intermediate_steps:
                        print_tool_info(
                            step[0].tool,
                            step[0].tool_input,
                            step[0].log
                        )
                
                # Print AI Message content
                ai_message_content = entry.content
                print_header(f"{agent} Response")
                print_section(ai_message_content,"")
                
                print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
                return
            