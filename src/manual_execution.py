import os
import json
from src.tools.pptx_creator_tool import execute_powerpoint_creation
from service_crew import build_crew

def manual_powerpoint_creation(service_date: str):
    """
    Manually execute the PowerPoint creation process, bypassing agent tool calling issues
    """
    print(f"🎯 Manual PowerPoint Creation for {service_date}")
    
    # Build crew to get the design task output
    theme = "Forgiveness"
    backgrounds_path = "backgrounds"
    output_dir = "output"
    
    crew, theme_backgrounds_path, output_path = build_crew(
        backgrounds_path=backgrounds_path,
        output_dir=output_dir,
        theme=theme,
        service_date=service_date,
    )
    
    print(f"📁 Output path: {output_path}")
    print(f"🎨 Backgrounds path: {theme_backgrounds_path}")
    
    # Execute only up to the design task
    try:
        # Get the agents
        agents = crew.agents
        planner, formatter, designer, creator = agents
        
        # Execute tasks sequentially
        print("📋 Running Service Planner...")
        plan_result = planner.execute_task(
            crew.tasks[0],
            context=None
        )
        
        print("📝 Running Content Formatter...")
        format_result = formatter.execute_task(
            crew.tasks[1], 
            context=[plan_result]
        )
        
        print("🎨 Running Slide Designer...")
        design_result = designer.execute_task(
            crew.tasks[2],
            context=[format_result]
        )
        
        print("✅ Design task completed successfully!")
        
        # Now manually create the PowerPoint using the design result
        print("🔄 Starting manual PowerPoint creation...")
        result = execute_powerpoint_creation(design_result, output_path, theme_backgrounds_path)
        
        print(f"\n{result}")
        return True
        
    except Exception as e:
        print(f"❌ Error during manual execution: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        service_date = sys.argv[1]
    else:
        service_date = "2025-10-12"  # Default date
    
    manual_powerpoint_creation(service_date)