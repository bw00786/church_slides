import os
from crewai import Agent, Task, Crew, Process
from src.tools.pptx_creator_tool import create_service_slides

LLM_MODEL = "ollama/gemma3"

def select_background_folder(base_path: str, theme: str) -> str:
    theme_folder = theme.strip().lower().replace(" ", "_")
    themed_path = os.path.join(base_path, theme_folder)
    default_path = os.path.join(base_path, "default")
    if os.path.exists(themed_path):
        print(f"🎨 Using theme backgrounds: {themed_path}")
        return themed_path
    elif os.path.exists(default_path):
        print(f"🎨 Using default backgrounds: {default_path}")
        return default_path
    else:
        print(f"⚠️ No specific backgrounds found, using: {base_path}")
        return base_path


def build_crew(backgrounds_path: str, output_dir: str, theme: str, service_date: str):
    """Create CrewAI workflow that converts the YAML service order into a PPTX."""
    theme_backgrounds_path = select_background_folder(backgrounds_path, theme)

    # === AGENTS ===
    planner = Agent(
        role="Service Planner",
        goal="Convert YAML service order into structured JSON slide data exactly as provided.",
        backstory="Expert in organizing church service content and ensuring each element appears in presentation order.",
        verbose=True,
        allow_delegation=False,
        llm=LLM_MODEL,
    )

    formatter = Agent(
        role="Content Formatter",
        goal="Split long content into multiple slides when it exceeds 6 lines. Add (Part 1), (Part 2) suffixes to titles.",
        backstory="Specializes in making text fit presentation slides while preserving original content.",
        verbose=True,
        allow_delegation=False,
        llm=LLM_MODEL,
    )

    designer = Agent(
        role="Slide Designer",
        goal=f"Assign appropriate background images from {theme_backgrounds_path} based on slide type.",
        backstory="Expert at matching slide content with appropriate visual backgrounds.",
        verbose=True,
        allow_delegation=False,
        llm=LLM_MODEL,
    )

    creator = Agent(
        role="Presentation Creator",
        goal="Generate PowerPoint using the pptx_creator tool with correct parameters.",
        backstory="Technical expert who executes tools with precise parameter formatting.",
        verbose=True,
        allow_delegation=False,
        llm=LLM_MODEL,
        tools=[create_service_slides]
    )

    # === TASKS ===
    plan_task = Task(
        description=(
            "Convert this YAML service order into a JSON list of slides:\n\n"
            "{service_data}\n\n"
            "Each slide must have: 'type', 'title', 'content' (use empty string if no content).\n"
            "PRESERVE the exact order from the YAML. Use data EXACTLY as provided - no inventions.\n"
            "Return ONLY valid JSON array."
        ),
        expected_output="JSON array of slides: [{'type','title','content'}]",
        agent=planner,
    )

    format_task = Task(
        description=(
            "Process the planner's JSON output and split any slide content exceeding 6 lines into multiple slides.\n"
            "For split slides: add '(Part 1)', '(Part 2)' to the title.\n"
            "Example: If 'Call to Worship' has 12 lines, create 'Call to Worship (Part 1)' and 'Call to Worship (Part 2)'.\n"
            "PRESERVE original content - only split, don't edit or invent.\n"
            "Return formatted JSON with same structure."
        ),
        expected_output="JSON array with split slides when needed: [{'type','title','content'}]",
        agent=formatter,
        context=[plan_task],
    )

    design_task = Task(
        description=(
            f"CRITICAL: You MUST use FULL ABSOLUTE PATHS for background images.\n"
            f"The background images are located in: '{theme_backgrounds_path}'\n\n"
            "EXACT PATH FORMAT REQUIRED:\n"
            f"- countdown -> '{theme_backgrounds_path}/countdown.jpg'\n"
            f"- song -> '{theme_backgrounds_path}/song.jpg'\n"
            f"- hymn -> '{theme_backgrounds_path}/hymn.jpg'\n"
            f"- prayer -> '{theme_backgrounds_path}/prayer.jpg'\n"
            f"- scripture -> '{theme_backgrounds_path}/scripture.jpg'\n"
            f"- sermon -> '{theme_backgrounds_path}/sermon.jpg'\n"
            f"- communion -> '{theme_backgrounds_path}/communion.jpg'\n"
            f"- offering -> '{theme_backgrounds_path}/offering.jpg'\n"
            f"- children_message -> '{theme_backgrounds_path}/children.jpg'\n"
            f"- liturgy -> '{theme_backgrounds_path}/liturgy.jpg'\n"
            f"- text -> '{theme_backgrounds_path}/general.jpg'\n"
            f"- dismissal -> '{theme_backgrounds_path}/general.jpg'\n\n"
            "DO NOT use just filenames like 'countdown.jpg'. Use the complete path as shown above.\n"
            "Return JSON with 'background_path' field containing the FULL path."
        ),
        expected_output="Final JSON: [{'type','title','content','background_path'}] with FULL background paths",
        agent=designer,
        context=[format_task],
    )

    theme_sanitized = theme.strip().replace(" ", "")
    output_path = os.path.join(output_dir, f"{service_date}_{theme_sanitized}_ServiceSlides.pptx")

    pptx_task = Task(
        description=(
            "Generate the PowerPoint presentation. "
            f"The output file should be saved at: {output_path}\n"
            "Use the slides data from the previous task."
        ),
        expected_output=f"PowerPoint presentation created at: {output_path}",
        agent=creator,
        context=[design_task],
    )

    crew = Crew(
        agents=[planner, formatter, designer, creator],
        tasks=[plan_task, format_task, design_task, pptx_task],
        process=Process.sequential,
    )

    return crew, theme_backgrounds_path, output_path