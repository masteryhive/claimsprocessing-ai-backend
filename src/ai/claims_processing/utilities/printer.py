from typing import Dict, Any
from colorama import init, Fore, Style, Back
import textwrap
from src.database.schemas import Task, TaskStatus
from src.ai.resources.db_ops import save_claim_report_database
from src.datamodels.co_ai import AIClaimsReport, ProcessClaimTask
from src.database.pd_db import create_claim_report
from src.ai.claims_processing.utilities.parser import extract_claim_data, extract_claim_summary
from src.config.db_setup import SessionLocal

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

def fancy_print(claim_request: ProcessClaimTask,s: Dict[str, Any], data: Dict[str, Any]) -> None:
    """Main function to handle fancy printing of the workflow."""
    db = SessionLocal()
    if "__end__" not in s:
        print_header("CO AI Workflow Status")
        # Print the current state
        # print_section("Current State", str(s))
        agent = list(s.keys())[0]
        if agent == "claims_adjuster_1":
            messages = data[agent]['messages']
            for message in messages:
                print_header(f"{agent} Response")
                result = extract_claim_summary(message.content)
                save_claim_report_database({
                    "claim":"",
                    "claimId": result['id'],
                    "fraudScore": result['fraud_score'],
                    "fraudIndicators": result['fraud_indicators'],
                    "aiRecommendation": result['ai_recommendation'],
                    "policyReview": result['policy_review'],
                    "evidenceProvided": result['evidence_provided'],
                    "coverageStatus": result['coverage_status'],
                    "typeOfIncident": result['type_of_incident'],
                    "details": result['details']
                })
                # Create new task record
                task = Task(
                    task_id=claim_request.task_id, task_type="co_ai", status=TaskStatus.COMPLETED
                )
                db.add(task)
                db.commit()
                db.refresh(task)
                print_section(message.content,"")
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
