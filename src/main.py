import argparse
import yaml
import os
import json
from .service_crew import build_crew
from .tools.pptx_creator_tool import create_service_slides


def recursive_date_to_str(data):
    """Recursively converts datetime/date objects to ISO strings for CrewAI compatibility."""
    if isinstance(data, dict):
        return {k: recursive_date_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_date_to_str(item) for item in data]
    elif hasattr(data, "isoformat") and callable(getattr(data, "isoformat")):
        return data.isoformat()
    else:
        return data


def load_service_order(service_date: str):
    """Loads service order data and ensures all date objects are converted to strings."""
    file_path = os.path.join("service_orders", f"{service_date}.yaml")
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Service order file not found: {file_path}\n"
            "Please ensure your file name matches YYYY-MM-DD.yaml"
        )
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)
    return recursive_date_to_str(raw_data)


def extract_slides_json(crew_result):
    """
    Extracts the JSON slides array from the crew result.
    Handles various return formats from CrewAI.
    """
    try:
        # Case 1: Result is already a list
        if isinstance(crew_result, list):
            return crew_result
        
        # Case 2: Result is a JSON string
        if isinstance(crew_result, str):
            # Try to find JSON array in the string
            crew_result = crew_result.strip()
            
            # Remove markdown code blocks if present
            if crew_result.startswith("```json"):
                crew_result = crew_result.replace("```json", "").replace("```", "").strip()
            elif crew_result.startswith("```"):
                crew_result = crew_result.replace("```", "").strip()
            
            return json.loads(crew_result)
        
        # Case 3: Result has .raw attribute (CrewAI output object)
        if hasattr(crew_result, 'raw'):
            return extract_slides_json(crew_result.raw)
        
        # Case 4: Result has .result attribute
        if hasattr(crew_result, 'result'):
            return extract_slides_json(crew_result.result)
        
        # Case 5: Result is a dict with the slides data
        if isinstance(crew_result, dict):
            # Check if it's the slides array wrapped in a dict
            if 'slides' in crew_result:
                return crew_result['slides']
            # Otherwise assume it's a single slide, wrap it
            return [crew_result]
        
        raise ValueError(f"Could not extract slides from result type: {type(crew_result)}")
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw result: {crew_result[:500]}...")  # Print first 500 chars
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-date", required=True, help="Service date, e.g. 2025-09-28")
    parser.add_argument("--skip-pptx", action="store_true", help="Skip PowerPoint generation (debugging)")
    args = parser.parse_args()

    service_date = args.service_date

    try:
        service_data = load_service_order(service_date)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return

    theme = service_data.get("theme", "default")
    backgrounds_path = "backgrounds"
    output_dir = "output"

    # Build the crew (now without the PPTX creator agent)
    crew, theme_backgrounds_path, output_path = build_crew(
        backgrounds_path=backgrounds_path,
        output_dir=output_dir,
        theme=theme,
        service_date=service_date,
    )

    print(f"\n🎉 Generating slides for {service_date} (Theme: {theme})\n")

    # Run the crew (stops at the designer agent)
    result = crew.kickoff(
        inputs={
            "service_date": service_date,
            "service_data": service_data,
            "backgrounds_path": theme_backgrounds_path,
            "output_dir": output_dir,
        }
    )

    print("\n✅ Crew processing complete!")
    print(f"Result type: {type(result)}\n")

    # Extract the slides JSON from the crew result
    try:
        slides_json = extract_slides_json(result)
        print(f"📋 Extracted {len(slides_json)} slides from crew output")
        
        # Debug: Print first slide
        if slides_json and len(slides_json) > 0:
            print(f"\n📝 First slide preview:")
            print(f"   Type: {slides_json[0].get('type')}")
            print(f"   Title: {slides_json[0].get('title')}")
            print(f"   Background: {slides_json[0].get('background_path')}")
        
        if args.skip_pptx:
            print("\n⏭️  Skipping PowerPoint generation (--skip-pptx flag)")
            # Optionally save JSON for debugging
            json_path = output_path.replace(".pptx", ".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(slides_json, f, indent=2)
            print(f"💾 Saved JSON to: {json_path}")
            return
        
        # Create the PowerPoint directly (bypass agent)
        print(f"\n🖼️  Creating PowerPoint presentation...")
        confirmation = create_service_slides(slides_json, output_path)
        
        print(f"\n{confirmation}")
        print(f"📁 Saved to: {output_path}\n")
        
    except Exception as e:
        print(f"\n❌ Error processing slides: {e}")
        print(f"\nRaw crew result:")
        print(result)
        raise


if __name__ == "__main__":
    main()