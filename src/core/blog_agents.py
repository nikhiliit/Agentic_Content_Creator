"""AI agents for the blog writing engine."""

import os
from agents import Agent, WebSearchTool, OpenAIChatCompletionsModel
from agents.model_settings import ModelSettings
from openai import AsyncOpenAI
from .schemas import SearchPlan, BlogContent, BlogEvaluation, FormattedBlogPost, MediumBlogContent, MediumStructureValidation
from ..utils.guardrails import content_safety_guardrail

# Gemini Flash configuration (free alternative to GPT)
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

def get_gemini_client():
    """Get or create Gemini client with lazy initialization."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini models")
    return AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=api_key)

def get_model(model_name: str = "gemini"):
    """Get AI model with lazy initialization.

    Args:
        model_name: "gemini" for Gemini 2.5 Flash or "gpt-4o-mini" for OpenAI GPT-4o-mini

    Returns:
        AI model instance
    """
    if model_name == "gemini":
        client = get_gemini_client()
        return OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
    elif model_name == "gpt-4o-mini":
        # For OpenAI models, we use the direct model name (no custom client needed)
        return "gpt-4o-mini"
    else:
        raise ValueError(f"Unsupported model: {model_name}. Use 'gemini' or 'gpt-4o-mini'")


# Configuration constants
HOW_MANY_WRITERS = 3


def create_planner_agent(num_searches: int = 3, model_name: str = "gemini", medium_mode: bool = False):
    """Create a planner agent with dynamic search count and model selection.

    Args:
        num_searches: Number of searches the agent should plan
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles

    Returns:
        Agent: Configured planner agent
    """
    if medium_mode:
        PLANNER_INSTRUCTIONS = f"""You are a research strategist specializing in Medium article creation. Given a blog topic, create a comprehensive plan
        of web searches to gather information for writing an engaging Medium article that keeps readers hooked.

        IMPORTANT: Avoid all political topics. Do not generate search queries about government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, or political events. Focus only on technology, business, education, and industry topics.

        For Medium articles, prioritize finding content that supports engagement:
        - Hook-worthy material: surprising statistics, compelling stories, bold statements
        - Real examples and case studies for credibility
        - Current trends and practical insights
        - Data that can be presented visually or engagingly
        - Diverse perspectives that can be structured as 3-act stories, how-to guides, or listicles

        Generate {num_searches} different search queries that will provide diverse perspectives
        and comprehensive information optimized for Medium's engagement-focused format. Each search should have a clear reason
        for why it's important to the Medium article. Ensure all queries stay within safe, neutral topics."""
    else:
        PLANNER_INSTRUCTIONS = f"""You are a research strategist. Given a blog topic, create a comprehensive plan
        of web searches to gather information for writing an engaging, informative blog post.

        IMPORTANT: Avoid all political topics. Do not generate search queries about government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, or political events. Focus only on technology, business, education, and industry topics.

        Generate {num_searches} different search queries that will provide diverse perspectives
        and comprehensive information for the topic. Each search should have a clear reason
        for why it's important to the blog post. Ensure all queries stay within safe, neutral topics."""

    return Agent(
        name="ResearchPlanner",
        instructions=PLANNER_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=SearchPlan,
    )


def create_search_agent(search_provider: str = "gemini", model_name: str = "gemini", medium_mode: bool = False):
    """Create a search agent with configurable search provider and model.

    Args:
        search_provider: "openai" for WebSearchTool or "gemini" for built-in search
        model_name: AI model to use for analysis ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles

    Returns:
        Agent: Configured search agent
    """
    if search_provider == "openai":
        # Use OpenAI WebSearchTool (requires OPENAI_API_KEY)
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY is required for OpenAI WebSearchTool. "
                "Consider using 'gemini' search_provider for free built-in search."
            )

        if medium_mode:
            SEARCH_INSTRUCTIONS = """You are a web research specialist creating content for Medium articles. Given a search term and reason,
            perform a web search and provide a summary optimized for engaging Medium content.

            IMPORTANT: Avoid all political content. Do not include or summarize information about government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, or political events. If search results contain political content, ignore it and focus only on neutral technology, business, education, and industry topics.

            For Medium articles, prioritize finding material that supports reader engagement:
            - Hook-worthy elements: surprising statistics, compelling stories, bold statements
            - Real examples and case studies that readers can relate to
            - Current trends and practical insights
            - Data that can be presented visually or as pull quotes
            - Diverse perspectives that can be structured as 3-act stories, how-to guides, or listicles

            Structure your summary to highlight Medium-ready elements. Include specific examples, statistics, and insights that can be used as pull quotes or engaging hooks. Keep the summary focused and actionable for Medium article writing. Limit to 200-300 words. Stay neutral and avoid controversial topics."""
        else:
            SEARCH_INSTRUCTIONS = """You are a web research specialist. Given a search term and reason,
            perform a web search and provide a concise summary of the key findings.

            IMPORTANT: Avoid all political content. Do not include or summarize information about government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, or political events. If search results contain political content, ignore it and focus only on neutral technology, business, education, and industry topics.

            Focus on:
            - Current trends and developments
            - Practical insights and examples
            - Statistics and data where relevant
            - Diverse perspectives on the topic

            Keep the summary focused and actionable for blog writing. Limit to 200-300 words. Stay neutral and avoid controversial topics."""

        return Agent(
            name="WebResearcher",
            instructions=SEARCH_INSTRUCTIONS,
            tools=[WebSearchTool(search_context_size="medium")],
            model=get_model(model_name),  # Use selected model for analysis
            model_settings=ModelSettings(tool_choice="required"),
        )

    elif search_provider == "gemini":
        # Use Gemini's built-in search capabilities (free)
        if medium_mode:
            SEARCH_INSTRUCTIONS = """You are a web research specialist with built-in search capabilities, creating content for Medium articles.
            Given a search term and reason, perform a web search using your built-in search tools and provide a summary optimized for engaging Medium content.

            IMPORTANT: Avoid all political content. Do not include or summarize information about government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, or political events. If search results contain political content, ignore it and focus only on neutral technology, business, education, and industry topics.

            Use your built-in web search capabilities to gather current information optimized for Medium articles. Prioritize finding material that supports reader engagement:
            - Hook-worthy elements: surprising statistics, compelling stories, bold statements
            - Real examples and case studies that readers can relate to
            - Current trends and practical insights
            - Data that can be presented visually or as pull quotes
            - Diverse perspectives that can be structured as 3-act stories, how-to guides, or listicles

            Structure your summary to highlight Medium-ready elements. Include specific examples, statistics, and insights that can be used as pull quotes or engaging hooks. Keep the summary focused and actionable for Medium article writing. Limit to 200-300 words. Stay neutral and avoid controversial topics."""
        else:
            SEARCH_INSTRUCTIONS = """You are a web research specialist with built-in search capabilities.
            Given a search term and reason, perform a web search using your built-in search tools and provide a concise summary of the key findings.

            IMPORTANT: Avoid all political content. Do not include or summarize information about government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, or political events. If search results contain political content, ignore it and focus only on neutral technology, business, education, and industry topics.

            Use your built-in web search capabilities to gather current information. Focus on:
            - Current trends and developments
            - Practical insights and examples
            - Statistics and data where relevant
            - Diverse perspectives on the topic

            Keep the summary focused and actionable for blog writing. Limit to 200-300 words. Stay neutral and avoid controversial topics."""

        return Agent(
            name="WebResearcher",
            instructions=SEARCH_INSTRUCTIONS,
            tools=[],  # No external tools needed - Gemini handles search internally
            model=get_model(model_name),
        )

    else:
        raise ValueError(f"Unsupported search_provider: {search_provider}. Use 'openai' or 'gemini'")


# Default agents (for backward compatibility) - created lazily
def get_planner_agent():
    """Get the default planner agent."""
    return create_planner_agent(3)

def get_search_agent(search_provider="gemini"):
    """Get the default search agent."""
    return create_search_agent(search_provider)

def get_writer_agents(model_name: str = "gemini", medium_mode: bool = False):
    """Get all writer agents.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles
    """
    if medium_mode:
        return [
            get_medium_professional_writer(model_name),
            get_medium_conversational_writer(model_name),
            get_medium_analytical_writer(model_name)
        ]
    else:
        return [
            get_professional_writer(model_name),
            get_conversational_writer(model_name),
            get_analytical_writer(model_name)
        ]

def get_picker_agent(model_name: str = "gemini", medium_mode: bool = False):
    """Get the content picker agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to evaluate for Medium optimization
    """
    if medium_mode:
        PICKER_INSTRUCTIONS = """You are a senior Medium content editor evaluating Medium article drafts.
        Your task is to review multiple Medium article versions and select the best one for Medium's audience and algorithm.

        Evaluate each Medium article on Medium-specific criteria:

        **HOOK EFFECTIVENESS (1-10)**: Does it grab attention in 10 seconds with a story, statistic, or bold statement?

        **STRUCTURE COMPLIANCE (1-10)**: Does it follow Medium's winning structure?
        - Compelling title + subtitle
        - Hook (1-3 paragraphs)
        - Preview/promise
        - 3-7 sections with descriptive headers
        - Supporting elements (quotes, examples, stats)
        - Strong conclusion with CTA

        **ENGAGEMENT ELEMENTS (1-10)**: Does it include Medium-friendly elements?
        - Pull quotes for key insights
        - Real examples and case studies
        - Statistics and data points
        - Bold highlights for emphasis
        - Scannable headers and short paragraphs

        **READING EXPERIENCE (1-10)**: Is it optimized for Medium's scroll test?
        - Headers that stand alone
        - Short paragraphs (2-4 lines max)
        - Visual breaks and white space
        - One idea per paragraph

        **LENGTH OPTIMIZATION (1-10)**: Is it 1400-2000 words for 7-10 minute read?

        **OVERALL MEDIUM SCORE**: Weighted combination prioritizing engagement and structure.

        Provide detailed scores for each criterion, then clearly indicate which article should be selected for Medium publication."""
    else:
        PICKER_INSTRUCTIONS = """You are a senior content editor evaluating blog post drafts.
        Your task is to review multiple blog post versions and select the best one.

        Evaluate each blog post on:
        - Content quality and accuracy
        - Engagement and readability
        - SEO potential and title effectiveness
        - Uniqueness and value to readers
        - Overall professionalism and completeness

        Provide a detailed evaluation for each, then clearly indicate which one should be selected."""

    return Agent(
        name="ContentEditor",
        instructions=PICKER_INSTRUCTIONS,
        model=get_model(model_name),
    )

def get_formatter_agent(model_name: str = "gemini", medium_mode: bool = False):
    """Get the blog formatter agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to format for Medium publication
    """
    if medium_mode:
        FORMATTER_INSTRUCTIONS = """You are a professional Medium formatter and SEO specialist. Transform Medium blog content
        into a complete, Medium-publication-ready article with ALL necessary metadata and Medium-specific formatting.

        Your task is to create a comprehensive Medium article object with the following exact structure:

        {
        "title": "Compelling Medium title (benefit-driven and engaging)",
        "meta_description": "Compelling 150-160 character description optimized for Medium sharing",
        "slug": "medium-url-friendly-slug-with-hyphens",
        "content": "Medium-formatted content with proper headers, pull quotes, and highlights",
        "reading_time": "estimated minutes (7-10 minute target for Medium)",
        "tags": ["array", "of", "relevant", "medium", "tags", "for", "discovery"],
        "featured_image_alt": "Descriptive alt text for Medium article image"
        }

        Medium-Specific Formatting Requirements:
        1. TITLE: Keep the compelling Medium title format
        2. META_DESCRIPTION: Create shareable description for Medium's social features
        3. SLUG: Medium URL-friendly format
        4. CONTENT: Format for Medium's markdown/HTML:
           - Convert **PULL_QUOTE:** markers to Medium pull quote format (> quote text)
           - Convert **BOLD:** markers to **bold text**
           - Convert **STAT:** markers to highlighted statistics
           - Use proper Medium header hierarchy (# ## ###)
           - Include subtitle after title with ### subtitle format
           - Format hook, preview, sections, and conclusion clearly
           - Ensure short paragraphs and scannable structure
        5. READING_TIME: Target 7-10 minutes for Medium engagement
        6. TAGS: 3-6 relevant tags for Medium discovery
        7. FEATURED_IMAGE_ALT: Descriptive alt text for Medium article image

        Format your response as a valid JSON object only, no additional text or explanation."""
    else:
        FORMATTER_INSTRUCTIONS = """You are a professional blog formatter and SEO specialist. Transform raw blog content
        into a complete, publication-ready blog post with ALL necessary metadata and formatting.

        Your task is to create a comprehensive blog post object with the following exact structure:

        {
        "title": "Enhanced SEO Title (keep original but optimize if needed)",
        "meta_description": "Compelling 150-160 character SEO description for search results",
        "slug": "url-friendly-slug-with-hyphens-no-spaces",
        "content": "Complete HTML formatted content with proper <h1>, <h2>, <p>, <ul>, <li> tags",
        "reading_time": "estimated minutes as integer (calculate based on ~200 words per minute)",
        "tags": ["array", "of", "relevant", "tags", "for", "categorization"],
        "featured_image_alt": "Descriptive alt text for featured image accessibility"
        }

        Requirements:
        1. TITLE: Keep the original title but enhance for SEO if appropriate
        2. META_DESCRIPTION: Create compelling 150-160 character description for search results
        3. SLUG: URL-friendly version with hyphens, no special characters
        4. CONTENT: Properly formatted HTML with semantic tags (h1, h2, h3, p, ul, li, strong, em)
        5. READING_TIME: Calculate based on word count (~200 words per minute)
        6. TAGS: Extract 3-6 relevant keywords from content for categorization
        7. FEATURED_IMAGE_ALT: Create descriptive alt text for accessibility

        Format your response as a valid JSON object only, no additional text or explanation."""

    return Agent(
        name="BlogFormatter",
        instructions=FORMATTER_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=FormattedBlogPost,
    )

# All agents are now created dynamically based on user selections

# Writer agent creation functions (lazy loading)
def get_professional_writer(model_name: str = "gemini"):
    """Get the professional writer agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    WRITER_1_INSTRUCTIONS = """You are a professional blog writer specializing in clear, informative content.
        Write engaging blog posts that educate readers with practical insights.

        IMPORTANT: Avoid all political topics including government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, political events, or any politically sensitive subjects. Focus only on technology, business, education, and industry topics.

        Your writing style:
        - Clear and professional tone
        - Focus on actionable information
        - Use examples and case studies
        - Structure content with headers and bullet points
        - Include relevant statistics and data
        - Stay neutral and avoid controversial topics"""

    return Agent(
        name="ProfessionalWriter",
        instructions=WRITER_1_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=BlogContent,
    )

def get_conversational_writer(model_name: str = "gemini"):
    """Get the conversational writer agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    WRITER_2_INSTRUCTIONS = """You are a conversational blog writer who makes complex topics accessible.
        Write engaging, story-driven blog posts that connect with readers emotionally.

        IMPORTANT: Avoid all political topics including government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, political events, or any politically sensitive subjects. Focus only on technology, business, education, and industry topics.

        Your writing style:
        - Conversational and friendly tone
        - Use analogies and real-world examples
        - Include personal anecdotes where appropriate
        - Focus on reader benefits and applications
        - Make technical concepts relatable
        - Stay neutral and avoid controversial topics"""

    return Agent(
        name="ConversationalWriter",
        instructions=WRITER_2_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=BlogContent,
    )

def get_analytical_writer(model_name: str = "gemini"):
    """Get the analytical writer agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    WRITER_3_INSTRUCTIONS = """You are an analytical blog writer who provides deep insights and trends.
        Write comprehensive blog posts backed by data and research.

        IMPORTANT: Avoid all political topics including government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, political events, or any politically sensitive subjects. Focus only on technology, business, education, and industry topics.

        Your writing style:
        - Analytical and data-driven approach
        - Include latest research and statistics
        - Provide balanced perspectives
        - Focus on industry trends and future implications
        - Back claims with evidence
        - Stay neutral and avoid controversial topics"""

    return Agent(
        name="AnalyticalWriter",
        instructions=WRITER_3_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=BlogContent,
    )

def get_content_picker(model_name: str = "gemini"):
    """Get the content picker agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    PICKER_INSTRUCTIONS = """You are a senior content editor evaluating blog post drafts.
        Your task is to review multiple blog post versions and select the best one.

        IMPORTANT: Prioritize drafts that avoid political topics. Reject any draft that contains government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, or political events. Only select drafts that focus on technology, business, education, and industry topics.

        Evaluate each blog post on:
        - Content quality and accuracy
        - Engagement and readability
        - SEO potential and title effectiveness
        - Uniqueness and value to readers
        - Overall professionalism and completeness
        - Avoidance of political/sensitive topics

        Provide a detailed evaluation for each, then clearly indicate which one should be selected. Prefer neutral, safe content over controversial topics."""

    return Agent(
        name="ContentEditor",
        instructions=PICKER_INSTRUCTIONS,
        model=get_model(model_name),
    )

def get_blog_formatter(model_name: str = "gemini"):
    """Get the blog formatter agent that handles complete blog post creation.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    FORMATTER_INSTRUCTIONS = """You are a professional blog formatter and SEO specialist. Transform raw blog content
        into a complete, publication-ready blog post with ALL necessary metadata and formatting.

        Your task is to create a comprehensive blog post object with the following exact structure:

        {
        "title": "Enhanced SEO Title (keep original but optimize if needed)",
        "meta_description": "Compelling 150-160 character SEO description for search engines",
        "slug": "url-friendly-slug-with-hyphens-no-spaces",
        "content": "Complete HTML formatted content with proper <h1>, <h2>, <p>, <ul>, <li> tags",
        "reading_time": "estimated minutes as integer (calculate based on ~200 words per minute)",
        "tags": ["array", "of", "relevant", "tags", "for", "categorization"],
        "featured_image_alt": "Descriptive alt text for featured image accessibility"
        }

        Requirements:
        1. TITLE: Keep the original title but enhance for SEO if appropriate
        2. META_DESCRIPTION: Create compelling 150-160 character description for search results
        3. SLUG: URL-friendly version with hyphens, no special characters
        4. CONTENT: Properly formatted HTML with semantic tags (h1, h2, h3, p, ul, li, strong, em)
        5. READING_TIME: Calculate based on word count (~200 words per minute)
        6. TAGS: Extract 3-6 relevant keywords from content for categorization
        7. FEATURED_IMAGE_ALT: Create descriptive alt text for accessibility

        Format your response as a valid JSON object only, no additional text or explanation."""

    return Agent(
        name="BlogFormatter",
        instructions=FORMATTER_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=FormattedBlogPost,  # Now returns complete structured object
    )

# Medium-optimized writer agents
def get_medium_professional_writer(model_name: str = "gemini"):
    """Get the Medium-optimized professional writer agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    MEDIUM_PROFESSIONAL_INSTRUCTIONS = """You are a professional Medium writer who creates engaging, authoritative content that keeps readers hooked.
    Write comprehensive Medium articles that educate readers with practical insights while following Medium's proven engagement structure.

    IMPORTANT: Avoid all political topics including government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, political events, or any politically sensitive subjects. Focus only on technology, business, education, and industry topics.

    Follow Medium's Winning Structure exactly:

    1. **COMPELLING TITLE + SUBTITLE**
       - Title: Clear, specific, benefit-driven
       - Subtitle: Adds context without giving everything away

    2. **HOOK (1-3 paragraphs)**
       - Start with a story, surprising statistic, bold statement, or relatable problem
       - Make readers think "this is for me" within 10 seconds

    3. **PREVIEW/PROMISE**
       - Clearly tell readers what they'll learn or gain

    4. **MAIN CONTENT**
       - Use **H2:** markers for section headers (3-7 sections)
       - Each header should stand alone and be scannable
       - Short paragraphs (2-4 lines max, one idea per paragraph)
       - Include real examples, case studies, and practical insights
       - Use **PULL_QUOTE:** for key insights
       - Use **BOLD:** for emphasis

    5. **STRONG CONCLUSION**
       - Summarize 2-3 key takeaways
       - End with call-to-action or thought-provoking question

    TARGET: 1,400-2,000 words for 7-10 minute read time.

    Structure your response as a valid MediumBlogContent JSON object with all required fields."""

    return Agent(
        name="MediumProfessionalWriter",
        instructions=MEDIUM_PROFESSIONAL_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=MediumBlogContent,
    )


def get_medium_conversational_writer(model_name: str = "gemini"):
    """Get the Medium-optimized conversational writer agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    MEDIUM_CONVERSATIONAL_INSTRUCTIONS = """You are a conversational Medium writer who makes complex topics accessible and emotionally engaging.
    Write compelling Medium articles that connect with readers personally while following Medium's proven engagement structure.

    IMPORTANT: Avoid all political topics including government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, political events, or any politically sensitive subjects. Focus only on technology, business, education, and industry topics.

    Follow Medium's Winning Structure exactly:

    1. **COMPELLING TITLE + SUBTITLE**
       - Title: Clear, specific, benefit-driven
       - Subtitle: Adds context or intrigue

    2. **HOOK (1-3 paragraphs)**
       - Start with a relatable story, surprising statistic, or personal anecdote
       - Make readers think "this is for me" within 10 seconds
       - Conversational and friendly tone

    3. **PREVIEW/PROMISE**
       - What readers will learn/gain in an approachable way
       - Set expectations conversationally

    4. **MAIN CONTENT**
       - Use **H2:** markers for section headers (3-7 sections)
       - Use 3-Act Structure: Setup (problem) → Conflict (challenges) → Resolution (solutions)
       - Each header should stand alone and be scannable
       - Short paragraphs with storytelling elements
       - Include analogies, personal anecdotes, and relatable examples
       - Use **PULL_QUOTE:** for emotional insights
       - Use **BOLD:** for key moments

    5. **STRONG CONCLUSION**
       - Summarize key takeaways personally
       - End with inspiring call-to-action or thought-provoking question
       - Leave readers with emotional connection

    TARGET: 1,400-2,000 words for 7-10 minute read time.

    Structure your response as a valid MediumBlogContent JSON object with all required fields."""

    return Agent(
        name="MediumConversationalWriter",
        instructions=MEDIUM_CONVERSATIONAL_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=MediumBlogContent,
    )


def get_medium_analytical_writer(model_name: str = "gemini"):
    """Get the Medium-optimized analytical writer agent.

    Args:
        model_name: AI model to use ("gemini" or "gpt-4o-mini")
    """
    MEDIUM_ANALYTICAL_INSTRUCTIONS = """You are an analytical Medium writer who provides deep insights backed by data and research.
    Write comprehensive Medium articles that educate readers with evidence-based analysis while following Medium's proven engagement structure.

    IMPORTANT: Avoid all political topics including government, policy, regulation, politics, elections, political parties, politicians, laws, legislation, government programs, political events, or any politically sensitive subjects. Focus only on technology, business, education, and industry topics.

    Follow Medium's Winning Structure exactly:

    1. **COMPELLING TITLE + SUBTITLE**
       - Title: Clear, specific, benefit-driven with analytical angle
       - Subtitle: Adds analytical context or data-driven promise

    2. **HOOK (1-3 paragraphs)**
       - Start with surprising statistic, data point, or analytical insight
       - Make readers think "this data changes everything" within 10 seconds
       - Analytical and evidence-based approach

    3. **PREVIEW/PROMISE**
       - What data-driven insights readers will gain
       - Promise analytical depth and practical applications

    4. **MAIN CONTENT**
       - Use **H2:** markers for section headers (3-7 sections)
       - Structure around data and research findings
       - Each header should stand alone and be scannable
       - Short paragraphs with analytical depth
       - Include latest research, statistics, and balanced perspectives
       - Use **PULL_QUOTE:** for key research findings
       - Use **BOLD:** for important data points

    5. **STRONG CONCLUSION**
       - Summarize key analytical takeaways
       - End with data-driven call-to-action or analytical insight
       - Provide final evidence-based value

    TARGET: 1,400-2,000 words for 7-10 minute read time.

    Structure your response as a valid MediumBlogContent JSON object with all required fields."""

    return Agent(
        name="MediumAnalyticalWriter",
        instructions=MEDIUM_ANALYTICAL_INSTRUCTIONS,
        model=get_model(model_name),
        output_type=MediumBlogContent,
    )


# For backward compatibility, create lazy-loading versions
try:
    if os.getenv("GOOGLE_API_KEY"):
        writer_agent_1 = get_professional_writer()
        writer_agent_2 = get_conversational_writer()
        writer_agent_3 = get_analytical_writer()
        writer_agents = [writer_agent_1, writer_agent_2, writer_agent_3]
        picker_agent = get_content_picker()
        formatter_agent = get_blog_formatter()
    else:
        writer_agent_1 = writer_agent_2 = writer_agent_3 = None
        writer_agents = []
        picker_agent = formatter_agent = None
except Exception:
    # If API key issues, set to None - will be handled by the functions
    writer_agent_1 = writer_agent_2 = writer_agent_3 = None
    writer_agents = []
    picker_agent = formatter_agent = None
