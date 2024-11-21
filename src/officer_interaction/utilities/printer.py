from typing import Dict, Any
from colorama import init, Fore, Style, Back
import textwrap
from datamodels.co_ai import AIClaimsReport
from database.pd_db import create_claim_report
from officer_interaction.utilities.parser import extract_claim_data, extract_claim_summary
from config.db_setup import SessionLocal

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

def fancy_print(s: Dict[str, Any], data: Dict[str, Any]) -> None:
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
                # result = extract_claim_data(message.content)
                result = extract_claim_summary(message.content)
                print(result)
                create_claim_report(db,result['fraud_score'],result['fraud_indicators'],
                                    result['ai_recommendation'],result['policy_review'])
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
