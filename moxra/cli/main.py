# -*- coding: utf-8 -*-
"""
Moxra - Command Line Interface
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from moxra.core.config import Config
from moxra.core.detector import MoxraDetector


def main():
    """
    Main entry point for command line interface
    
    This function processes command line arguments and runs detection
    """
    parser = argparse.ArgumentParser(
        description="Moxra - Command line interface for NSFW content detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m moxra.cli.main --input image.jpg
  python -m moxra.cli.main --input image.gif --format json
  python -m moxra.cli.main --input video.mp4 --sample-rate 0.05 --max-frames 200
  python -m moxra.cli.main --input image.jpg --output result.json
        """
    )
    
    # Required arguments
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to image, GIF, or video file"
    )
    
    # Model options
    parser.add_argument(
        "-t", "--type",
        choices=["d", "m2", "i3"],
        default="d",
        help="Model type: d (default), m2, i3"
    )
    parser.add_argument(
        "-m", "--model",
        help="Custom model path"
    )
    parser.add_argument(
        "-d", "--device",
        choices=["cpu", "cuda", "tensorrt", "dml", "coreml", "openvino"],
        default="cpu",
        help="Execution device (default: cpu)"
    )
    
    # Video options
    parser.add_argument(
        "-s", "--sample-rate",
        type=float,
        default=0.1,
        help="Video sampling rate (0 to 1), default: 0.1"
    )
    parser.add_argument(
        "-f", "--max-frames",
        type=int,
        default=100,
        help="Maximum video frames to process, default: 100"
    )
    
    # Output options
    parser.add_argument(
        "--format",
        choices=["json", "pretty", "simple"],
        default="pretty",
        help="Output format (default: pretty)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save output to file"
    )
    
    # Other options
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: File not found: {args.input}")
        sys.exit(1)
    
    try:
        # Configuration
        config = Config()
        config.model_type = args.type
        config.model_path = args.model
        config.device = args.device
        
        # Initialize detector
        if args.verbose:
            print("🔧 Initializing Moxra...")
        
        detector = MoxraDetector(config)
        
        if args.verbose:
            print(f"✅ Model loaded: {args.type}")
            print(f"   Device: {args.device}")
            print(f"   Image dimensions: {detector.image_dim}x{detector.image_dim}")
            print()
        
        # Process file based on type
        file_ext = Path(args.input).suffix.lower()
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        gif_ext = ['.gif']
        
        if file_ext in video_exts:
            if args.verbose:
                print(f"🎬 Processing video: {args.input}")
            result = detector.predict_video(
                args.input,
                sample_rate=args.sample_rate,
                max_frames=args.max_frames
            )
        elif file_ext in gif_ext:
            if args.verbose:
                print(f"🎞️ Processing GIF: {args.input}")
            result = detector.predict_gif(args.input)
        else:
            if args.verbose:
                print(f"🖼️ Processing image: {args.input}")
            result = detector.predict_image(args.input)
        
        if not result:
            print("❌ Processing failed")
            sys.exit(1)
        
        # Format output
        output = format_output(result, args.format, args.no_color)
        
        # Save or print
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                if args.format == "json":
                    json.dump(result, f, indent=2)
                else:
                    f.write(output)
            print(f"✅ Saved to: {args.output}")
        else:
            print(output)
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def format_output(result: dict, format_type: str, no_color: bool) -> str:
    """
    Format output for display
    
    Args:
        result: Detection result dictionary
        format_type: Output format (json, pretty, simple)
        no_color: Disable colors
    
    Returns:
        Formatted string for display
    """
    if format_type == "json":
        return json.dumps(result, indent=2)
    
    if format_type == "simple":
        if "average" in result:
            return json.dumps(result.get("average", {}), indent=2)
        return json.dumps(result, indent=2)
    
    # Pretty output with colors
    colors = {
        'green': '\033[92m' if not no_color else '',
        'yellow': '\033[93m' if not no_color else '',
        'red': '\033[91m' if not no_color else '',
        'blue': '\033[94m' if not no_color else '',
        'purple': '\033[95m' if not no_color else '',
        'reset': '\033[0m' if not no_color else ''
    }
    
    lines = []
    lines.append("=" * 50)
    lines.append("Moxra - Detection Result")
    lines.append("=" * 50)
    
    if "average" in result:
        # Video result
        avg = result.get("average", {})
        meta = result.get("metadata", {})
        
        lines.append(f"📹 Video Analysis")
        lines.append(f"   Total frames: {meta.get('total_frames', 0)}")
        lines.append(f"   Processed frames: {meta.get('processed_frames', 0)}")
        lines.append(f"   Duration: {meta.get('duration', 0):.2f} seconds")
        lines.append("")
        lines.append("Average predictions:")
        for cat, prob in avg.items():
            color = get_color(cat, colors)
            bar = "█" * int(prob * 40)
            lines.append(f"   {color}{cat:10}{colors['reset']} {prob*100:5.1f}% {bar}")
    
    elif "predictions" in result:
        # Image result with score
        preds = result.get("predictions", {})
        score = result.get("nsfw_score", 0)
        is_nsfw = result.get("is_nsfw", False)
        
        lines.append(f"📄 File: {result.get('filename', 'Unknown')}")
        lines.append(f"📊 NSFW Score: {score*100:.1f}% {'⚠️ NSFW' if is_nsfw else '✅ Safe'}")
        lines.append("")
        lines.append("Predictions:")
        for cat, prob in preds.items():
            color = get_color(cat, colors)
            bar = "█" * int(prob * 40)
            lines.append(f"   {color}{cat:10}{colors['reset']} {prob*100:5.1f}% {bar}")
    
    else:
        # Simple result
        for cat, prob in result.items():
            color = get_color(cat, colors)
            bar = "█" * int(prob * 40)
            lines.append(f"   {color}{cat:10}{colors['reset']} {prob*100:5.1f}% {bar}")
    
    lines.append("=" * 50)
    return "\n".join(lines)


def get_color(category: str, colors: dict) -> str:
    """
    Get color for each category
    
    Args:
        category: Category name
        colors: Color dictionary
    
    Returns:
        ANSI color code
    """
    color_map = {
        'neutral': colors['green'],
        'sexy': colors['yellow'],
        'porn': colors['red'],
        'hentai': colors['purple'],
        'drawing': colors['blue']
    }
    return color_map.get(category, colors['reset'])


if __name__ == "__main__":
    main()
