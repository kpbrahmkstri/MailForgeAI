#!/usr/bin/env python3
"""
Generate PNG workflow diagram directly using Pillow (PIL).
No external dependencies beyond what's likely already installed.
"""

import os
import sys


def generate_png_with_pillow():
    """Generate PNG using PIL/Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    
    # Create image with white background
    width, height = 1200, 1400
    background_color = (255, 255, 255)
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        node_font = ImageFont.truetype("arial.ttf", 14)
        label_font = ImageFont.truetype("arial.ttf", 12)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        title_font = node_font = label_font = small_font = ImageFont.load_default()
    
    # Colors
    light_blue = (225, 245, 255)
    dark_blue = (1, 87, 155)
    light_green = (232, 245, 233)
    light_orange = (255, 243, 224)
    light_pink = (252, 228, 236)
    light_yellow = (241, 248, 224)
    light_purple = (243, 229, 245)
    light_green_end = (200, 230, 201)
    dark_green = (46, 125, 50)
    
    dark_text = (0, 0, 0)
    light_text = (100, 100, 100)
    
    def draw_rounded_rect(draw, xy, fill, outline, width=2, radius=8):
        """Draw a rectangle with rounded corners."""
        x1, y1, x2, y2 = xy
        # Main rectangle
        draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill, outline=None)
        draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill, outline=None)
        # Corners
        draw.ellipse([x1, y1, x1+radius*2, y1+radius*2], fill=fill, outline=None)
        draw.ellipse([x2-radius*2, y1, x2, y1+radius*2], fill=fill, outline=None)
        draw.ellipse([x1, y2-radius*2, x1+radius*2, y2], fill=fill, outline=None)
        draw.ellipse([x2-radius*2, y2-radius*2, x2, y2], fill=fill, outline=None)
        # Border
        if outline:
            draw.rectangle([x1+radius, y1, x2-radius, y2], outline=outline, width=width)
            draw.rectangle([x1, y1+radius, x2, y2-radius], outline=outline, width=width)
            draw.arc([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=outline, width=width)
            draw.arc([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=outline, width=width)
            draw.arc([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=outline, width=width)
            draw.arc([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=outline, width=width)
    
    # Title
    draw.text((600, 20), "MailForgeAI LangGraph Workflow Diagram", font=title_font, fill=dark_blue, anchor="mm")
    
    # Nodes positions and info
    nodes = [
        (600, 100, "INPUT PARSER", "Parse user prompt\nExtract intent hints", light_blue, dark_blue),
        (600, 185, "INTENT DETECTION", "Classify email type\nAnalyze intent", light_blue, dark_blue),
        (600, 270, "TONE STYLIST", "Determine tone\nSet writing style", light_orange, (255, 127, 0)),
        (600, 355, "RETRIEVAL (RAG)", "Fetch templates\nGet knowledge base", light_purple, (156, 39, 176)),
        (600, 440, "PERSONALIZATION", "Add context\nUser profile data", light_green, (46, 125, 50)),
        (600, 525, "DRAFT WRITER", "Generate email\nCreate content", light_orange, (255, 127, 0)),
        (600, 610, "REVIEW", "Check quality\nValidate output", light_pink, (229, 57, 53)),
        (600, 695, "ROUTER", "Decision logic\nRoute next step", light_yellow, (174, 189, 47)),
    ]
    
    # Draw nodes and connecting lines
    node_width, node_height = 240, 70
    
    for i, (x, y, title, desc, color, border) in enumerate(nodes):
        # Draw rectangle
        draw_rounded_rect(draw, 
            (x - node_width//2, y - node_height//2, x + node_width//2, y + node_height//2),
            fill=color, outline=border, width=2, radius=6)
        
        # Draw text
        draw.text((x, y - 12), title, font=node_font, fill=dark_text, anchor="mm")
        draw.text((x, y + 12), desc, font=small_font, fill=light_text, anchor="mm")
        
        # Draw arrow to next node (except last)
        if i < len(nodes) - 1:
            next_y = nodes[i + 1][1]
            arrow_start = y + node_height//2 + 2
            arrow_end = next_y - node_height//2 - 2
            draw.line([(x, arrow_start), (x, arrow_end)], fill=dark_text, width=2)
            # Arrowhead
            draw.polygon([(x, arrow_end), (x-8, arrow_end-12), (x+8, arrow_end-12)], fill=dark_text)
    
    # Feedback loop: Router back to Draft Writer
    draft_y = nodes[5][1]
    router_x = 600
    feedback_x = 750
    
    # Curved line going right then up
    draw.line([(router_x + 20, 695), (feedback_x, 695)], fill=(255, 127, 0), width=2)
    draw.line([(feedback_x, 695), (feedback_x, draft_y)], fill=(255, 127, 0), width=2)
    draw.line([(feedback_x, draft_y), (router_x + 20, draft_y)], fill=(255, 127, 0), width=2)
    # Arrowhead
    draw.polygon([(router_x + 20, draft_y), (router_x - 8, draft_y - 8), (router_x - 8, draft_y + 8)], 
                 fill=(255, 127, 0))
    draw.text((750 + 30, 640), "revise", font=small_font, fill=(255, 127, 0))
    
    # End node
    end_x, end_y = 250, 695
    draw.ellipse([end_x - 40, end_y - 40, end_x + 40, end_y + 40], fill=light_green_end, outline=dark_green, width=2)
    draw.text((end_x, end_y), "END", font=node_font, fill=dark_text, anchor="mm")
    
    # Line from router to END
    draw.line([(450, 695), (290, 695)], fill=dark_text, width=2)
    draw.polygon([(290, 695), (308, 687), (308, 703)], fill=dark_text)
    draw.text((360, 680), "ask_user / final", font=small_font, fill=light_text)
    
    # Legend
    legend_y = 900
    draw.text((50, legend_y), "Legend:", font=label_font, fill=dark_text)
    
    # Legend items - simplified without rounded corners
    draw.rectangle([50, legend_y + 30, 70, legend_y + 50], fill=light_blue, outline=dark_blue, width=1)
    draw.text((85, legend_y + 40), "Processing Agent", font=small_font, fill=dark_text, anchor="lm")
    
    draw.rectangle([50, legend_y + 65, 70, legend_y + 85], fill=light_yellow, outline=(174, 189, 47), width=1)
    draw.text((85, legend_y + 75), "Router/Decision Node", font=small_font, fill=dark_text, anchor="lm")
    
    draw.ellipse([50, legend_y + 100, 70, legend_y + 120], fill=light_green_end, outline=dark_green, width=1)
    draw.text((85, legend_y + 110), "End Node", font=small_font, fill=dark_text, anchor="lm")
    
    draw.line([(50, legend_y + 145), (70, legend_y + 145)], fill=dark_text, width=2)
    draw.text((85, legend_y + 145), "Data Flow", font=small_font, fill=dark_text, anchor="lm")
    
    draw.line([(50, legend_y + 170), (70, legend_y + 170)], fill=(255, 127, 0), width=2)
    draw.text((85, legend_y + 170), "Feedback Loop", font=small_font, fill=dark_text, anchor="lm")
    
    # Info box
    info_y = 1100
    info_text = [
        "Workflow Features:",
        "  • 8-node linear pipeline with conditional routing",
        "  • Shared EmailState for data across agents",
        "  • Feedback loop: Router can revise drafts",
        "  • End points: User clarification or final email",
    ]
    
    for i, line in enumerate(info_text):
        draw.text((50, info_y + i * 25), line, font=small_font, fill=dark_text, anchor="lm")
    
    # Save image
    output_file = "workflow_diagram.png"
    img.save(output_file, "PNG", quality=95)
    return output_file


def main():
    """Main execution."""
    print("\n" + "="*70)
    print("Generating PNG Workflow Diagram with Pillow")
    print("="*70 + "\n")
    
    try:
        output_file = generate_png_with_pillow()
        if output_file and os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            print(f"✅ Successfully created: {output_file}")
            print(f"📊 Image size: 1200x1400 pixels")
            print(f"📁 File size: {size:.1f} KB")
            print(f"\n✨ Your PNG is ready to download!")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
