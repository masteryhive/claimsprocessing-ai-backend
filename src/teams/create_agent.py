import operator
from typing import Annotated, Sequence, Any
from typing_extensions import TypedDict
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import BaseMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.output_parsers import JsonOutputParser

class ClaimFormScreeningTeamAgentState(TypedDict):
    messages: Annotated[list, add_messages]

    claim_form_json: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]

    document_verifier_result: str

    supporting_document_verifier_result: str

class PolicyReviewTeamAgentState(TypedDict):
    messages: Annotated[list, add_messages]

    claim_form_json: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]

    policy_essential_data_retriever_result: str

    policy_period_verifier_result: str

    insurance_policy_verifier_result:str


class FraudTeamAgentState(TypedDict):
    messages: Annotated[list, add_messages]

    claim_form_json: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next 
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]

    claim_form_fraud_investigator_result: str

    vehicle_fraud_investigator_result: str
    
    damage_cost_fraud_investigator_result: str

    fraud_risk_analyst_result: str

class SettlementOfferTeamAgentState(TypedDict):
    messages: Annotated[list, add_messages]

    claim_form_json: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]

    offer_analyst_result: str


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]

    claim_form_json: Annotated[Sequence[BaseMessage],operator.add]
    # The 'next' field indicates where to route to next
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]


def create_supervisor_node(system_prompt:str,llm:ChatVertexAI,SupervisorOutput:type,members:list):
    supervisor_parser = JsonOutputParser(pydantic_object=SupervisorOutput)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_history"),
        ]
    ).partial(
        options=str(members),
        members=", ".join(members),
        format_instructions=supervisor_parser.get_format_instructions(),
    )

    return prompt | llm | supervisor_parser



def create_tool_agent(llm: ChatVertexAI, tools: list, system_prompt: str):
    """Helper function to create agents with custom tools and system prompt
    Args:
        llm (ChatVertexAI): LLM for the agent
        tools (list): list of tools the agent will use
        system_prompt (str): text describing specific agent purpose

    Returns:
        executor (AgentExecutor): Runnable for the agent created.
    """

    # Each worker node will be given a name and some tools.

    system_prompt_template = PromptTemplate(
        template=system_prompt
        + """
                ONLY respond to the part of query relevant to your purpose.
                IGNORE tasks you can't complete. 
                The claim form submitted by the claimant to give you full access to the JSON form: \n{claim_form_json}\n.
                Use the following context to answer your query 
                if available: \n {agent_history} \n
                """,
        input_variables=["agent_history","claim_form_json"],
    )

    # define system message
    system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="claim_form_json"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent, tools=tools, return_intermediate_steps=False, verbose=False
    )
    return executor

def create_tool_analyst_agent(llm: ChatVertexAI, tools: list, system_prompt: str):
    """Helper function to create agents with custom tools and system prompt
    Args:
        llm (ChatVertexAI): LLM for the agent
        tools (list): list of tools the agent will use
        system_prompt (str): text describing specific agent purpose

    Returns:
        executor (AgentExecutor): Runnable for the agent created.
    """

    # Each worker node will be given a name and some tools.

    system_prompt_template = PromptTemplate(
        template=system_prompt
        + """
                ONLY respond to the part of query relevant to your purpose.
                The claim form submitted by the claimant to give you full access to the JSON form: \n{claim_form_json}\n.
                IGNORE tasks you can't complete.
                Use the following context to compute the risk score based on the weights: \n {agent_history} \n
                """,
        input_variables=["agent_history","claim_form_json"],
    )

    # define system message
    system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent, tools=tools, return_intermediate_steps=False, verbose=False
    )
    return executor

def summarizer(system_prompt:str,llm: ChatVertexAI):
    system_prompt_template = PromptTemplate(
        template=system_prompt,
        input_variables=["agent_history"],
    )

    system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm

def create_report_agent(system_prompt:str,llm: ChatVertexAI):
    system_prompt_template = PromptTemplate(
        template=system_prompt,
        input_variables=["agent_history"],
    )

    system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm