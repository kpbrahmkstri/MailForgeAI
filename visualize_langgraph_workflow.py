"""
Visualizes the LangGraph workflow as a Mermaid diagram image.

This script generates a PNG visualization of the email assistant's workflow
and saves it to a file for easy reference.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.workflow.langgraph_flow import GRAPH


def visualize_workflow(output_file: str = "workflow_diagram.png"):
    """
    Generate and save the workflow graph as a PNG image.
    
    Args:
        output_file: Path to save the generated PNG image
    """
    try:
        # Generate the graph image
        print("Generating LangGraph workflow visualization...")
        graph_image = GRAPH.get_graph().draw_mermaid_png()
        
        # Save to file
        with open(output_file, "wb") as f:
            f.write(graph_image)
        
        print(f"✅ Workflow diagram saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error generating workflow visualization: {e}")
        raise


def display_workflow():
    """
    Display the workflow visualization in Jupyter/IPython environment.
    
    Use this if running in a Jupyter notebook.
    """
    try:
        from IPython.display import Image, display
        
        print("Generating LangGraph workflow visualization...")
        graph_image = GRAPH.get_graph().draw_mermaid_png()
        
        display(Image(graph_image))
        print("✅ Workflow diagram displayed")
    except ImportError:
        print("IPython not available. Use visualize_workflow() to save as PNG instead.")
    except Exception as e:
        print(f"❌ Error displaying workflow: {e}")
        raise


if __name__ == "__main__":
    # Generate and save the workflow diagram
    visualize_workflow()
    
    print("\n💡 Tip: You can also use display_workflow() in a Jupyter notebook to view it inline.")
