"""Orchestration functions for the complete blog writing pipeline."""

import asyncio
import re
from typing import List
from agents import Runner, trace
from .schemas import SearchPlan, SearchItem, BlogContent, BlogEvaluation, MediumBlogContent, MediumStructureValidation
from .blog_agents import create_planner_agent, create_search_agent, get_writer_agents, get_picker_agent, get_formatter_agent
from ..utils.guardrails import is_content_safe


def parse_draft_selection(agent_response: str, num_drafts: int) -> int:
    """Parse the ContentEditor agent's response to determine which draft was selected.

    Args:
        agent_response: The agent's evaluation response
        num_drafts: Total number of drafts available

    Returns:
        int: Index of selected draft (0-based)
    """
    # Common patterns the agent might use
    patterns = [
        r'select draft (\d+)',
        r'choose draft (\d+)',
        r'recommend draft (\d+)',
        r'i recommend draft (\d+)',
        r'draft (\d+) should be selected',
        r'selected draft (\d+)',
        r'best.*draft (\d+)',
        r'draft (\d+).*best',
        r'choose.*draft (\d+)',
        r'select.*draft (\d+)'
    ]

    # Try to find a draft number in the response
    for pattern in patterns:
        matches = re.findall(pattern, agent_response, re.IGNORECASE)
        if matches:
            draft_num = int(matches[0])
            # Convert to 0-based index and validate
            if 1 <= draft_num <= num_drafts:
                return draft_num - 1

    # If no clear pattern found, look for ordinal indicators
    ordinal_patterns = [
        (r'\b(first|1st)\b', 0),
        (r'\b(second|2nd)\b', 1),
        (r'\b(third|3rd)\b', 2),
        (r'\b(fourth|4th)\b', 3),
        (r'\b(fifth|5th)\b', 4)
    ]

    for pattern, index in ordinal_patterns:
        if re.search(pattern, agent_response, re.IGNORECASE) and index < num_drafts:
            return index

    # Last resort: look for any mention of draft numbers
    all_draft_mentions = re.findall(r'draft (\d+)', agent_response, re.IGNORECASE)
    if all_draft_mentions:
        # Take the last mentioned draft as the recommendation
        draft_num = int(all_draft_mentions[-1])
        if 1 <= draft_num <= num_drafts:
            return draft_num - 1

    # If all parsing fails, default to first draft
    print("⚠️  Could not parse ContentEditor recommendation, defaulting to first draft")
    return 0


async def plan_blog_research(topic: str, num_searches: int = 3, model_name: str = "gemini", medium_mode: bool = False) -> SearchPlan:
    """Plan web searches for comprehensive blog research.

    Args:
        topic: The blog topic to research
        num_searches: Number of searches to plan
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles

    Returns:
        SearchPlan: Structured plan with search queries and reasons
    """
    mode_desc = "Medium articles" if medium_mode else "blog posts"
    print(f"Planning research for {mode_desc}: {topic} using {model_name}")

    # Create a planner agent configured for the requested number of searches and model
    planner_agent = create_planner_agent(num_searches, model_name, medium_mode)

    result = await Runner.run(planner_agent, f"Blog topic: {topic}")
    print(f"Created {len(result.final_output.searches)} search queries")
    return result.final_output


async def perform_blog_research(search_plan: SearchPlan, search_provider: str = "gemini", model_name: str = "gemini", medium_mode: bool = False) -> List[str]:
    """Execute all planned web searches concurrently.

    Args:
        search_plan: The research plan with search queries
        search_provider: "openai" for WebSearchTool or "gemini" for built-in search
        model_name: AI model to use for analysis ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles

    Returns:
        List[str]: List of research summaries from each search
    """
    mode_desc = "Medium article" if medium_mode else "blog post"
    print(f"Performing web research for {mode_desc} using {search_provider} search with {model_name} analysis...")

    # Create the appropriate search agent
    search_agent = create_search_agent(search_provider, model_name, medium_mode)

    # Create concurrent tasks for all searches
    tasks = [asyncio.create_task(execute_search(item, search_agent)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)

    print(f"Completed {len(results)} research queries")
    return results


async def execute_search(search_item: SearchItem, search_agent) -> str:
    """Execute a single web search and return summary.

    Args:
        search_item: Individual search with query and reason
        search_agent: The search agent to use for this query

    Returns:
        str: Research summary from the web search
    """
    input_text = f"Search query: {search_item.query}\nReason: {search_item.reason}"
    result = await Runner.run(search_agent, input_text)
    return result.final_output


async def generate_blog_drafts(topic: str, research_results: List[str], model_name: str = "gemini", medium_mode: bool = False):
    """Generate multiple blog post drafts using different writing styles.

    Args:
        topic: The blog topic
        research_results: List of research summaries
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles

    Returns:
        List[BlogContent] or List[MediumBlogContent]: Multiple blog post drafts
    """
    mode_desc = "Medium article" if medium_mode else "blog post"
    print(f"Generating {mode_desc} drafts using {model_name}...")

    # Prepare context for writers
    research_context = "\n\n".join(research_results)
    writer_input = f"Topic: {topic}\n\nResearch findings:\n{research_context}"

    # Generate drafts concurrently from all writer agents
    writer_agents = get_writer_agents(model_name, medium_mode)
    tasks = [asyncio.create_task(generate_draft(writer, writer_input)) for writer in writer_agents]
    drafts = await asyncio.gather(*tasks)

    print(f"Generated {len(drafts)} {mode_desc} drafts")
    return drafts


async def generate_draft(writer_agent, input_text: str) -> BlogContent:
    """Generate a single blog post draft from a writer agent.

    Args:
        writer_agent: The agent to use for writing
        input_text: The input context with topic and research

    Returns:
        BlogContent: Structured blog content
    """
    result = await Runner.run(writer_agent, input_text)
    return result.final_output


async def evaluate_and_select_blog(drafts, model_name: str = "gemini", medium_mode: bool = False):
    """Evaluate multiple blog drafts and select the best one.

    Args:
        drafts: List of blog post drafts to evaluate
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to evaluate for Medium optimization

    Returns:
        BlogContent or MediumBlogContent: The selected best blog post
    """
    mode_desc = "Medium article" if medium_mode else "blog post"
    print(f"Evaluating {mode_desc} drafts using {model_name}...")

    # Safety check: Filter out any drafts with sensitive content
    safe_drafts = []
    for draft in drafts:
        if medium_mode:
            # MediumBlogContent schema
            content_to_check = f"{draft.title} {draft.subtitle} {draft.hook} {draft.preview}"
            content_to_check += f" {draft.sections_content} {draft.conclusion} {draft.call_to_action}"
        else:
            # BlogContent schema
            content_to_check = f"{draft.title} {draft.summary} {draft.main_content}"

        safety_check = is_content_safe(content_to_check)
        if safety_check.is_safe:
            safe_drafts.append(draft)
        else:
            print(f"⚠️  Filtered out draft with sensitive content: {safety_check.issues_found}")

    if not safe_drafts:
        print("❌ All drafts contained sensitive content. Using first draft as fallback.")
        safe_drafts = drafts

    # Use safe drafts for evaluation
    drafts = safe_drafts

    # Format drafts for the picker agent
    drafts_text = ""
    for i, draft in enumerate(drafts, 1):
        drafts_text += f"\n\n--- DRAFT {i} ---\n"

        if medium_mode:
            # MediumBlogContent formatting
            drafts_text += f"Title: {draft.title}\n"
            drafts_text += f"Subtitle: {draft.subtitle}\n"
            drafts_text += f"Hook: {draft.hook[:200]}...\n"
            drafts_text += f"Preview: {draft.preview}\n"
            drafts_text += f"Sections Content: {draft.sections_content[:500]}...\n"
            drafts_text += f"Conclusion: {draft.conclusion[:200]}...\n"
            drafts_text += f"Call to Action: {draft.call_to_action}\n"
        else:
            # BlogContent formatting
            drafts_text += f"Title: {draft.title}\n"
            drafts_text += f"Summary: {draft.summary}\n"
            drafts_text += f"Content:\n{draft.main_content}\n"

    content_type = "Medium article" if medium_mode else "blog post"
    evaluation_prompt = f"""Please evaluate these {len(drafts)} {content_type} drafts and select the best one.

{drafts_text}

Provide your evaluation and clearly indicate which draft (1, 2, or 3) should be selected as the final {content_type}."""

    picker_agent = get_picker_agent(model_name, medium_mode)
    result = await Runner.run(picker_agent, evaluation_prompt)

    # Parse the ContentEditor agent's recommendation
    agent_response = result.final_output.lower() if hasattr(result, 'final_output') else str(result.final_output).lower()

    print(f"🤖 ContentEditor evaluation: {agent_response[:200]}...")

    # Parse which draft was recommended
    selected_index = parse_draft_selection(agent_response, len(drafts))

    selected_draft = drafts[selected_index]
    print(f"✅ Selected Draft {selected_index + 1}: '{selected_draft.title[:50]}...'")
    print(f"   Selection reason: Based on ContentEditor AI evaluation")

    # Medium structure validation
    if medium_mode:
        from ..utils.guardrails import validate_medium_structure
        validation_result = validate_medium_structure(selected_draft)
        print(f"📊 Medium Structure Score: {validation_result.overall_score}/10")
        if validation_result.issues_found:
            print(f"⚠️  Structure Issues: {len(validation_result.issues_found)}")
            for issue in validation_result.issues_found[:3]:  # Show first 3 issues
                print(f"   - {issue}")
        else:
            print("✅ Structure validation passed")

    return selected_draft


async def format_blog_post(blog_content, model_name: str = "gemini", medium_mode: bool = False):
    """Format the selected blog content into professional blog post structure.

    Args:
        blog_content: The selected blog content
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to format for Medium publication

    Returns:
        FormattedBlogPost: Complete formatted blog post
    """
    mode_desc = "Medium article" if medium_mode else "blog post"
    print(f"Formatting {mode_desc} for publication using {model_name}...")

    # The BlogFormatter agent handles ALL formatting and metadata generation
    formatter_agent = get_formatter_agent(model_name, medium_mode)

    # Create a structured prompt with the blog content
    if medium_mode:
        # MediumBlogContent formatting
        format_prompt = f"""Transform this Medium article content into a complete, Medium-publication-ready article.

        Title: {blog_content.title}
        Subtitle: {blog_content.subtitle}
        Hook: {blog_content.hook}
        Preview: {blog_content.preview}

        Sections Content:
        {blog_content.sections_content}

        Conclusion: {blog_content.conclusion}
        Call to Action: {blog_content.call_to_action}
        Target Word Count: {blog_content.target_word_count}

        Generate a complete FormattedBlogPost object with Medium-optimized formatting."""
    else:
        # BlogContent formatting
        format_prompt = f"""Transform this blog content into a complete, publication-ready blog post.

        Blog Title: {blog_content.title}
        Blog Summary: {blog_content.summary}
        Blog Content:
        {blog_content.main_content}

        Generate a complete FormattedBlogPost object with all required fields."""

    result = await Runner.run(formatter_agent, format_prompt)

    print("Blog post formatted and ready for publication")
    # Agent now returns complete FormattedBlogPost directly
    return result.final_output


async def generate_complete_blog(topic: str, num_searches: int = 3, search_provider: str = "gemini", model_name: str = "gemini", medium_mode: bool = False):
    """Execute the complete blog generation pipeline.

    Args:
        topic: The blog topic to write about
        num_searches: Number of web searches to perform
        search_provider: "openai" for WebSearchTool or "gemini" for built-in search
        model_name: AI model to use for all agents ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles

    Returns:
        FormattedBlogPost: Complete formatted blog post
    """
    mode_desc = "Medium article" if medium_mode else "blog post"
    print(f"🚀 Starting {mode_desc} generation for topic: {topic} using {model_name} model")

    with trace("BlogGeneration"):
        # Phase 1: Plan research
        search_plan = await plan_blog_research(topic, num_searches, model_name, medium_mode)

        # Phase 2: Perform research
        research_results = await perform_blog_research(search_plan, search_provider, model_name, medium_mode)

        # Phase 3: Generate drafts
        blog_drafts = await generate_blog_drafts(topic, research_results, model_name, medium_mode)

        # Phase 4: Evaluate and select
        selected_blog = await evaluate_and_select_blog(blog_drafts, model_name, medium_mode)

        # Phase 5: Format for publication
        final_blog_post = await format_blog_post(selected_blog, model_name, medium_mode)

    print("✅ Blog generation completed successfully!")
    return final_blog_post
