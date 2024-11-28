import base64,requests
from langgraph.graph.state import CompiledStateGraph


def save_graph_mermaid(graph:CompiledStateGraph, output_file:str='langgraph.png'):
    # Get the Mermaid string from your graph
    mermaid_string = graph.get_graph().draw_mermaid()
    
    # Encode the Mermaid syntax
    graphbytes = mermaid_string.encode("ascii")
    base64_graph = base64.b64encode(graphbytes)
    
    # Create the API URL
    mermaid_url = f"https://mermaid.ink/img/{base64_graph.decode('ascii')}"
    
    # Download the image
    response = requests.get(mermaid_url)
    
    # Save the image
    with open(output_file, 'wb') as f:
        f.write(response.content)