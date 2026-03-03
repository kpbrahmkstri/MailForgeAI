#!/usr/bin/env python3
"""
Generate a PNG diagram of the LangGraph workflow using Mermaid.
Requires: npm install -g @mermaid-js/mermaid-cli
"""

import subprocess
import os
from pathlib import Path


def generate_png_diagram():
    """Generate PNG diagram from Mermaid diagram."""
    
    # Mermaid diagram content
    mermaid_content = """graph TD
    A["<b>INPUT PARSER</b><br/>Parse user prompt<br/>Extract intent hints"] --> B["<b>INTENT DETECTION</b><br/>Classify email type<br/>Analyze intent"]
    B --> C["<b>TONE STYLIST</b><br/>Determine tone<br/>Set writing style"]
    C --> D["<b>RETRIEVAL</b><br/>Fetch templates<br/>Get knowledge base"]
    D --> E["<b>PERSONALIZATION</b><br/>Add context<br/>User profile data"]
    E --> F["<b>DRAFT WRITER</b><br/>Generate email<br/>Create content"]
    F --> G["<b>REVIEW</b><br/>Check quality<br/>Validate output"]
    G --> H["<b>ROUTER</b><br/>Decision logic<br/>Route next step"]
    H -->|revise| F
    H -->|ask_user| END["<b>END</b><br/>Return to user"]
    H -->|final| END
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#fff3e0
    style D fill:#f3e5f5
    style E fill:#e8f5e9
    style F fill:#fff3e0
    style G fill:#fce4ec
    style H fill:#f1f8e9
    style END fill:#c8e6c9"""
    
    # Save diagram to .mmd file
    mmd_file = "workflow_diagram.mmd"
    output_file = "workflow_diagram.png"
    
    with open(mmd_file, "w") as f:
        f.write(mermaid_content)
    
    print(f"✅ Saved Mermaid diagram to: {mmd_file}")
    
    # Try to generate PNG using mmdc (mermaid-cli)
    try:
        result = subprocess.run(
            ["mmdc", "-i", mmd_file, "-o", output_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / 1024  # KB
                print(f"✅ PNG diagram generated successfully!")
                print(f"📁 File: {output_file}")
                print(f"📊 Size: {file_size:.1f} KB")
                return True
        else:
            print(f"❌ Error running mmdc:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ mermaid-cli (mmdc) not found. Installing...")
        print("\nTo generate PNG, please run:")
        print("  npm install -g @mermaid-js/mermaid-cli")
        print("\nOnce installed, run this script again.")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout while generating PNG")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def generate_svg_fallback():
    """Generate SVG diagram as fallback (uses built-in Python)."""
    import base64
    
    # Create a simple SVG representation
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="1000" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      .node { fill: #e1f5ff; stroke: #01579b; stroke-width: 2; }
      .node-router { fill: #f1f8e9; stroke: #558b2f; stroke-width: 2; }
      .node-end { fill: #c8e6c9; stroke: #2e7d32; stroke-width: 2; }
      .text { font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }
      .label { font-weight: bold; font-size: 13px; }
      .edge { stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
      .edge-label { font-size: 11px; fill: #666; }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#333" />
    </marker>
  </defs>
  
  <!-- Title -->
  <text x="600" y="30" class="label" style="font-size: 20px;">MailForgeAI LangGraph Workflow Diagram</text>
  
  <!-- Nodes -->
  <!-- Input Parser -->
  <rect x="450" y="80" width="300" height="80" class="node" rx="5"/>
  <text x="600" y="110" class="text label">Input Parser</text>
  <text x="600" y="128" class="text">Parse user prompt, extract hints</text>
  <text x="600" y="143" class="text" style="font-size: 10px;">>> parsed_request</text>
  
  <!-- Intent Detection -->
  <rect x="450" y="200" width="300" height="80" class="node" rx="5"/>
  <text x="600" y="230" class="text label">Intent Detection</text>
  <text x="600" y="248" class="text">Classify email type</text>
  <text x="600" y="263" class="text" style="font-size: 10px;">>> intent</text>
  
  <!-- Tone Stylist -->
  <rect x="450" y="320" width="300" height="80" class="node" rx="5"/>
  <text x="600" y="350" class="text label">Tone Stylist</text>
  <text x="600" y="368" class="text">Determine tone & style</text>
  <text x="600" y="383" class="text" style="font-size: 10px;">>> tone_contract</text>
  
  <!-- Retrieval -->
  <rect x="450" y="440" width="300" height="80" class="node" rx="5"/>
  <text x="600" y="470" class="text label">Retrieval (RAG)</text>
  <text x="600" y="488" class="text">Fetch templates &amp; KB</text>
  <text x="600" y="503" class="text" style="font-size: 10px;">>> retrieved_templates</text>
  
  <!-- Personalization -->
  <rect x="450" y="560" width="300" height="80" class="node" rx="5"/>
  <text x="600" y="590" class="text label">Personalization</text>
  <text x="600" y="608" class="text">Add user context</text>
  <text x="600" y="623" class="text" style="font-size: 10px;">>> user_profile</text>
  
  <!-- Draft Writer -->
  <rect x="450" y="680" width="300" height="80" class="node" rx="5"/>
  <text x="600" y="710" class="text label">Draft Writer</text>
  <text x="600" y="728" class="text">Generate email content</text>
  <text x="600" y="743" class="text" style="font-size: 10px;">>> draft</text>
  
  <!-- Review -->
  <rect x="450" y="800" width="300" height="80" class="node" rx="5"/>
  <text x="600" y="830" class="text label">Review</text>
  <text x="600" y="848" class="text">Quality assurance</text>
  <text x="600" y="863" class="text" style="font-size: 10px;">>> review_notes</text>
  
  <!-- Router -->
  <rect x="450" y="920" width="300" height="80" class="node-router" rx="5"/>
  <text x="600" y="950" class="text label">Router</text>
  <text x="600" y="968" class="text">Decision: revise/ask/final</text>
  
  <!-- END -->
  <circle cx="250" cy="960" r="40" class="node-end"/>
  <text x="250" y="965" class="text label">END</text>
  
  <!-- Edges -->
  <path d="M 600 160 L 600 200" class="edge"/>
  <path d="M 600 280 L 600 320" class="edge"/>
  <path d="M 600 400 L 600 440" class="edge"/>
  <path d="M 600 520 L 600 560" class="edge"/>
  <path d="M 600 640 L 600 680" class="edge"/>
  <path d="M 600 760 L 600 800" class="edge"/>
  <path d="M 600 880 L 600 920" class="edge"/>
  
  <!-- Feedback loop: Router to Draft Writer -->
  <path d="M 750 960 Q 850 850 750 760" class="edge" stroke="#ff6f00" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="820" y="850" class="edge-label" fill="#ff6f00">revise</text>
  
  <!-- Router to END -->
  <path d="M 450 960 L 290 960" class="edge"/>
  <text x="370" y="945" class="edge-label">ask_user / final</text>
  
  <!-- Legend -->
  <text x="50" y="100" style="font-size: 12px; font-weight: bold;">Legend:</text>
  <rect x="50" y="120" width="20" height="20" class="node"/>
  <text x="80" y="135" class="text" style="text-anchor: start;">Processing Agent</text>
  
  <rect x="50" y="160" width="20" height="20" class="node-router"/>
  <text x="80" y="175" class="text" style="text-anchor: start;">Router/Decision Node</text>
  
  <circle cx="60" cy="210" r="10" class="node-end"/>
  <text x="80" y="215" class="text" style="text-anchor: start;">End Node</text>
  
  <line x1="50" y1="250" x2="70" y2="250" class="edge"/>
  <text x="80" y="255" class="text" style="text-anchor: start;">Data Flow</text>
  
  <line x1="50" y1="290" x2="70" y2="290" class="edge" stroke="#ff6f00" stroke-dasharray="5,5"/>
  <text x="80" y="295" class="text" style="text-anchor: start;">Feedback Loop</text>
</svg>'''
    
    output_file = "workflow_diagram_svg.svg"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"✅ SVG fallback generated: {output_file}")
    print("   (Convert SVG to PNG using an online converter or Inkscape)")
    return output_file


def main():
    """Main execution."""
    print("\n" + "="*70)
    print("Generating Workflow Diagram as PNG")
    print("="*70 + "\n")
    
    # Try to generate PNG
    success = generate_png_diagram()
    
    if not success:
        print("\n⚠️  mermaid-cli not installed. Generating SVG fallback...")
        svg_file = generate_svg_fallback()
        print("\n💡 To convert SVG to PNG, you can:")
        print("   1. Use online tool: https://cloudconvert.com/svg-to-png")
        print("   2. Install Inkscape and run: inkscape workflow_diagram_svg.svg --export-type=png")
        print("   3. Use ImageMagick: convert workflow_diagram_svg.svg workflow_diagram.png")
        print("\n📝 Or to use mermaid-cli, install with:")
        print("   npm install -g @mermaid-js/mermaid-cli")
        print("   Then run this script again.")


if __name__ == "__main__":
    main()
