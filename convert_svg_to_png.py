#!/usr/bin/env python3
"""
Convert SVG workflow diagram to PNG using cairosvg or alternative methods.
"""

import subprocess
import sys
from pathlib import Path
from src.utils.path_utils import get_output_dir


def convert_svg_to_png_cairosvg():
    """Convert SVG to PNG using cairosvg."""
    output_dir = get_output_dir()
    svg_file = output_dir / "workflow_diagram_svg.svg"
    png_file = output_dir / "workflow_diagram.png"
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_file), write_to=str(png_file))
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error with cairosvg: {e}")
        return False


def convert_svg_to_png_pillow():
    """Convert SVG to PNG using PIL and wand."""
    output_dir = get_output_dir()
    svg_file = output_dir / "workflow_diagram_svg.svg"
    png_file = output_dir / "workflow_diagram.png"
    try:
        from PIL import Image
        from io import BytesIO
        
        # Try using wand (ImageMagick Python wrapper)
        try:
            from wand.image import Image as WandImage
            with WandImage(filename=str(svg_file), format="svg") as img:
                img.format = "png"
                img.save(filename=str(png_file))
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
    output_dir = get_output_dir()
    svg_file = output_dir / "workflow_diagram_svg.svg"
    png_file = output_dir / "workflow_diagram.png"
    try:
        result = subprocess.run(
            ["inkscape", "--export-type=png", str(svg_file), "-o", str(png_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True
        
        # Try old syntax
        result = subprocess.run(
            ["inkscape", "-z", "-e", str(png_file), str(svg_file)],
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
    output_dir = get_output_dir()
    svg_file = output_dir / "workflow_diagram_svg.svg"
    png_file = output_dir / "workflow_diagram.png"
    try:
        result = subprocess.run(
            ["convert", str(svg_file), str(png_file)],
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
    output_dir = get_output_dir()
    png_file = output_dir / "workflow_diagram.png"
    
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
            if png_file.exists():
                size = png_file.stat().st_size / 1024
                print(f"✅ Success!")
                print(f"✅ Created: {png_file} ({size:.1f} KB)")
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
    output_dir = get_output_dir()
    svg_file = output_dir / "workflow_diagram_svg.svg"
    
    # Check if SVG exists
    if not svg_file.exists():
        print(f"\u274c SVG file not found at {svg_file}. Run generate_png_diagram.py first.")
        sys.exit(1)
    
    # Try existing methods
    if generate_png_from_mermaid():
        return
    
    # Try installing and using cairosvg
    print("\nAttempting to install cairosvg...")
    if install_cairosvg():
        print("Retrying PNG conversion with cairosvg...")
        if convert_svg_to_png_cairosvg():
            png_file = output_dir / "workflow_diagram.png"
            if png_file.exists():
                size = png_file.stat().st_size / 1024
                print(f"✅ Successfully created: {png_file} ({size:.1f} KB)")
                return
    
    # Final fallback
    print("\n" + "="*70)
    print("⚠️  Could not convert SVG to PNG automatically")
    print("="*70)
    print("\nHowever, your SVG file is ready: {}".format(svg_file))
    print("\nOptions to convert SVG to PNG:")
    print("\n1. Online Converter (No installation needed):")
    print("   Visit: https://cloudconvert.com/svg-to-png")
    print(f"   Upload: {svg_file}")
    print("\n2. Install ImageMagick:")
    print("   Windows: choco install imagemagick")
    print(f"   Then: convert {svg_file} {{svg_file.parent / 'workflow_diagram.png'}}")
    print("\n3. Install Inkscape:")
    print("   Windows: choco install inkscape")
    print("   Then: inkscape --export-type=png workflow_diagram_svg.svg")
    print("\n4. Install cairosvg library:")
    print("   pip install cairosvg")
    print("   Then run this script again.")


if __name__ == "__main__":
    main()
