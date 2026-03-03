#!/usr/bin/env python3
"""
Generate a PNG diagram of the LangGraph workflow using Mermaid.
Requires: npm install -g @mermaid-js/mermaid-cli
"""

import subprocess
from pathlib import Path
from src.utils.path_utils import get_output_dir


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
    output_dir = get_output_dir()
    mmd_file = output_dir / "workflow_diagram.mmd"
    output_file = output_dir / "workflow_diagram.png"
    
    with open(mmd_file, "w") as f:
        f.write(mermaid_content)
    
    print(f"✅ Saved Mermaid diagram to: {mmd_file}")
    
    # Try to generate PNG using mmdc (mermaid-cli)
    try:
        result = subprocess.run(
            ["mmdc", "-i", str(mmd_file), "-o", str(output_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if output_file.exists():
                file_size = output_file.stat().st_size / 1024  # KB
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
    output_dir = get_output_dir()
    output_file = output_dir / "workflow_diagram_svg.svg"
    with open(output_file, "w", encoding="utf-8") as f:
    
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
