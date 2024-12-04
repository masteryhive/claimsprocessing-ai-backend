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
from src.ai.claims_processing.stirring_agent import members
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, trim_messages
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

def control_workflow(db: Session,claim_id:int,claim_request: ProcessClaimTask,task: Task,process_call: Dict[str, Any]) -> None:
    """Main function to handle fancy printing of the workflow."""
    if "__end__" not in process_call:
        print_header("CO AI Workflow Status")
        # Print the current state
        # print_section("Current State", str(s))
        agent = list(process_call.keys())[0]
        if agent == "summary_team":
            time.sleep(2)
            update_claim_status_database(claim_id=claim_id,status="Creating Report Summary")
            messages = process_call[agent]['messages']
            print(messages)
            content = [m.content for m in messages if isinstance(m, HumanMessage)]
            print_header(f"{agent} Response")
            time.sleep(2)
            update_claim_status_database(claim_id=claim_id,status="Preparing Report Summary")
            result = extract_claim_summary(content[0])
            save_claim_report_database({
                "claimId": claim_id,
                "fraudScore": result['fraud_score'],
                "discoveries":result["discoveries"],
               # "fraudIndicators": result['fraud_indicators'],
                 "fraudIndicators": result['claim_validation_factors'],
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
            print_section(content[0],"")
            update_claim_status_database(claim_id=claim_id,status=result['operationStatus'])
            return
        # Handle supervisor case
        if agent == "supervisor":
            next_agent = process_call["supervisor"]['next']
            print(f"{Fore.MAGENTA}🔄 Task Assignment:{Style.RESET_ALL}")
            print(f"   Assigning task to: {Fore.WHITE} {next_agent} {Style.RESET_ALL}\n")

        # Process agent history
        print_header(agent)

        if agent == members[0]:
            messages = process_call[agent]['messages']
            content = [m.content for m in messages if isinstance(m, HumanMessage)]
            update_claim_status_database(claim_id=claim_id,status="Examining claim form")
            # Print AI Message content
            ai_message_content = content[0]
            print_header(f"{agent} Response")
            print_section(ai_message_content,"")
            
            print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
        elif agent == members[1]:
            messages = process_call[agent]['messages']
            content = [m.content for m in messages if isinstance(m, HumanMessage)]
            update_claim_status_database(claim_id=claim_id,status="Claim Form Examination Complete!")
            time.sleep(0.6)
            update_claim_status_database(claim_id=claim_id,status="Reviewing claim policy")
            # Print AI Message content
            ai_message_content = content[0]
            print_header(f"{agent} Response")
            print_section(ai_message_content,"")
            print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")

        # elif agent == members[2]:
        #     update_claim_status_database(claim_id=claim_id,status="Evaluation Complete!")
        #     time.sleep(1)
        #     update_claim_status_database(claim_id=claim_id,status="Running document fraud checks")
        #     for entry in agent_history:
        #         intermediate_steps = entry.additional_kwargs.get('intermediate_steps', [])
                
        #         if intermediate_steps:
        #             print_header("Tool Executions")
        #             for step in intermediate_steps:
        #                 print_tool_info(
        #                     step[0].tool,
        #                     step[0].tool_input,
        #                     step[0].log
        #                 )
                
        #         # Print AI Message content
        #         ai_message_content = entry.content
        #         print_header(f"{agent} Response")
        #         print_section(ai_message_content,"")
                
        #         print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
        #         return
        # elif agent == members[3]:
        #     update_claim_status_database(claim_id=claim_id,status="Document fraud checks Done!")
        #     time.sleep(1)
        #     update_claim_status_database(claim_id=claim_id,status="Running vehicle fraud checks")
        #     for entry in agent_history:
        #         intermediate_steps = entry.additional_kwargs.get('intermediate_steps', [])
                
        #         if intermediate_steps:
        #             print_header("Tool Executions")
        #             for step in intermediate_steps:
        #                 print_tool_info(
        #                     step[0].tool,
        #                     step[0].tool_input,
        #                     step[0].log
        #                 )
                
        #         # Print AI Message content
        #         ai_message_content = entry.content
        #         print_header(f"{agent} Response")
        #         print_section(ai_message_content,"")
                
        #         print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
        #         return
            