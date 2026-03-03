#!/usr/bin/env python3
"""
Convert SVG workflow diagram to PNG using cairosvg or alternative methods.
"""

import subprocess
import os
import sys


def convert_svg_to_png_cairosvg():
    """Convert SVG to PNG using cairosvg."""
    try:
        import cairosvg
        cairosvg.svg2png(url="workflow_diagram_svg.svg", write_to="workflow_diagram.png")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error with cairosvg: {e}")
        return False


def convert_svg_to_png_pillow():
    """Convert SVG to PNG using PIL and wand."""
    try:
        from PIL import Image
        from io import BytesIO
        
        # Try using wand (ImageMagick Python wrapper)
        try:
            from wand.image import Image as WandImage
            with WandImage(filename="workflow_diagram_svg.svg", format="svg") as img:
                img.format = "png"
                img.save(filename="workflow_diagram.png")
            return True
        except ImportError:
            pass
        
        return False
    except Exception as e:
        print(f"Error with pillow: {e}")
        return False


def convert_svg_to_png_batik():
    """Convert SVG to PNG using Batik (Java-based)."""
    try:
        result = subprocess.run(
            ["java", "-jar", "batik-rasterizer.jar", "-d", ".", "workflow_diagram_svg.svg"],
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False


def convert_svg_to_png_inkscape():
    """Convert SVG to PNG using Inkscape."""
    try:
        result = subprocess.run(
            ["inkscape", "--export-type=png", "workflow_diagram_svg.svg", "-o", "workflow_diagram.png"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True
        
        # Try old syntax
        result = subprocess.run(
            ["inkscape", "-z", "-e", "workflow_diagram.png", "workflow_diagram_svg.svg"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error with Inkscape: {e}")
        return False


def convert_svg_to_png_imagemagick():
    """Convert SVG to PNG using ImageMagick."""
    try:
        result = subprocess.run(
            ["convert", "workflow_diagram_svg.svg", "workflow_diagram.png"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error with ImageMagick: {e}")
        return False


def generate_png_from_mermaid():
    """Generate PNG directly from Mermaid using various methods."""
    methods = [
        ("cairosvg", convert_svg_to_png_cairosvg),
        ("Inkscape", convert_svg_to_png_inkscape),
        ("ImageMagick", convert_svg_to_png_imagemagick),
        ("Pillow + Wand", convert_svg_to_png_pillow),
    ]
    
    print("\n" + "="*70)
    print("Converting SVG to PNG")
    print("="*70 + "\n")
    
    for name, method in methods:
        print(f"Attempting {name}...", end=" ")
        if method():
            if os.path.exists("workflow_diagram.png"):
                size = os.path.getsize("workflow_diagram.png") / 1024
                print(f"✅ Success!")
                print(f"✅ Created: workflow_diagram.png ({size:.1f} KB)")
                return True
        print("❌ Not available")
    
    return False


def install_cairosvg():
    """Install cairosvg library."""
    print("\n📦 Installing cairosvg...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "cairosvg"],
            capture_output=True,
            timeout=120
        )
        return True
    except Exception:
        return False


def main():
    """Main execution."""
    # Check if SVG exists
    if not os.path.exists("workflow_diagram_svg.svg"):
        print("❌ SVG file not found. Run generate_png_diagram.py first.")
        sys.exit(1)
    
    # Try existing methods
    if generate_png_from_mermaid():
        return
    
    # Try installing and using cairosvg
    print("\nAttempting to install cairosvg...")
    if install_cairosvg():
        print("Retrying PNG conversion with cairosvg...")
        if convert_svg_to_png_cairosvg():
            size = os.path.getsize("workflow_diagram.png") / 1024
            print(f"✅ Successfully created: workflow_diagram.png ({size:.1f} KB)")
            return
    
    # Final fallback
    print("\n" + "="*70)
    print("⚠️  Could not convert SVG to PNG automatically")
    print("="*70)
    print("\nHowever, your SVG file is ready: workflow_diagram_svg.svg")
    print("\nOptions to convert SVG to PNG:")
    print("\n1. Online Converter (No installation needed):")
    print("   Visit: https://cloudconvert.com/svg-to-png")
    print("   Upload: workflow_diagram_svg.svg")
    print("\n2. Install ImageMagick:")
    print("   Windows: choco install imagemagick")
    print("   Then: convert workflow_diagram_svg.svg workflow_diagram.png")
    print("\n3. Install Inkscape:")
    print("   Windows: choco install inkscape")
    print("   Then: inkscape --export-type=png workflow_diagram_svg.svg")
    print("\n4. Install cairosvg library:")
    print("   pip install cairosvg")
    print("   Then run this script again.")


if __name__ == "__main__":
    main()
