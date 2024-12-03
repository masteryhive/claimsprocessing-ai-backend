from typing import List, Literal
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage, trim_messages
from langgraph.prebuilt import create_react_agent
from pathlib import Path
from langchain_google_vertexai import ChatVertexAI
from src.ai.resources.gen_mermaid import save_graph_mermaid
from src.ai.claims_processing.teams.policy_review.tools import *
from langgraph.graph import END, StateGraph, START
from src.utilities.helpers import load_yaml_file


llm = ChatVertexAI(model_name="gemini-pro", kwargs={"temperature": 0.2})

agent1 = "policy_valid_checker"

members = [agent1]


def _load_prompt_template() -> str:
    """Load the instruction prompt template from YAML file."""
    try:
        prompt_path = Path("src/ai/claims_processing/teams/policy_review/prompts/instruction.yaml")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        yaml_data = load_yaml_file(prompt_path)
        return {
            "STIRRINGAGENTSYSTEMPROMPT": yaml_data.get("STIRRINGAGENTSYSTEMPROMPT", ""),
"POLICY_CHECK_VERIFIER_AGENT_SYSTEM_PROMPT":yaml_data.get("POLICY_CHECK_VERIFIER_AGENT_SYSTEM_PROMPT"),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt template: {str(e)}")


# The agent state is the input to each node in the graph
class AgentState(MessagesState):
    # The 'next' field indicates where to route to next
    next: str


def make_supervisor_node(llm: BaseChatModel, members: list[str]) -> str:
    options = ["FINISH"] + members
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )


    class Router(BaseModel):
        """
        Worker to route to the next step. If no workers are needed, route to FINISH.
        """

        next: List[str] = options

    def supervisor_node(state: MessagesState) -> MessagesState:
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        if response is not None:
            next_ = response.next
            return {"next": next_[0]}

    return supervisor_node


policy_claim_verifier_agent = create_react_agent(
    llm,
    tools=[policy_validity],
    state_modifier=_load_prompt_template()[
        "POLICY_CHECK_VERIFIER_AGENT_SYSTEM_PROMPT"
    ],
)



def policy_claim_verifier_node(state: AgentState) -> AgentState:
    result = policy_claim_verifier_agent.invoke(state)
    return {
        "messages": [HumanMessage(content=result["messages"][-1].content, name=agent1)]
    }



policy_check_supervisor_node = make_supervisor_node(llm, members)


policy_check_builder = StateGraph(MessagesState)
policy_check_builder.add_node("supervisor", policy_check_supervisor_node)
policy_check_builder.add_node(agent1, policy_claim_verifier_node)


# Define the control flow
policy_check_builder.add_edge(START, "supervisor")
# We want our workers to ALWAYS "report back" to the supervisor when done

policy_check_builder.add_edge("supervisor", agent1)
policy_check_builder.add_edge(agent1,END)

policy_check_graph = policy_check_builder.compile()
save_graph_mermaid(policy_check_graph,output_file='display/policy_langgraph.png')
