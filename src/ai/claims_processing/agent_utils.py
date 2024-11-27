from langchain_core.messages import AIMessage

# For agents in the crew
def crew_nodes(state, crew_member, name):
    # read the last message in the message history.
    input = {
        "messages": [state["messages"][-1]],
        "agent_history": state["agent_history"],
    }
    result = crew_member.invoke(input)
    # add response to the agent history.
    return {
        "agent_history": [
            AIMessage(
                content=result["output"],
                additional_kwargs={"intermediate_steps": result["intermediate_steps"]},
                name=name,
            )
        ]
    }


