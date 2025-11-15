"""Utility functions and tools for the blog writing engine."""

import re
from typing import List
from ..core.schemas import FormattedBlogPost


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time for text content.

    Args:
        text: The text content to analyze
        words_per_minute: Average reading speed (default: 200 WPM)

    Returns:
        int: Estimated reading time in minutes
    """
    # Remove HTML tags and extra whitespace
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    word_count = len(clean_text.split())
    reading_time = max(1, round(word_count / words_per_minute))

    return reading_time


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from a title.

    Args:
        title: The blog post title

    Returns:
        str: URL-friendly slug
    """
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
    slug = re.sub(r'[\s_]+', '-', slug)   # Replace spaces/underscores with hyphens
    slug = re.sub(r'-+', '-', slug)       # Replace multiple hyphens with single
    slug = slug.strip('-')                # Remove leading/trailing hyphens

    return slug


def extract_tags_from_content(content: str) -> List[str]:
    """Extract relevant tags from blog content using keyword analysis."""
    content_lower = content.lower()

    # Comprehensive keyword categories
    tech_keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'deep learning',
        'neural network', 'nlp', 'computer vision', 'robotics', 'automation',
        'blockchain', 'cryptocurrency', 'web3', 'metaverse', 'vr', 'ar',
        'iot', 'cloud computing', 'edge computing', 'quantum computing',
        'cybersecurity', 'data science', 'big data', 'analytics'
    ]

    business_keywords = [
        'business', 'startup', 'entrepreneurship', 'marketing', 'sales',
        'strategy', 'growth', 'scaling', 'product management', 'leadership',
        'management', 'consulting', 'finance', 'investment', 'venture capital'
    ]

    development_keywords = [
        'programming', 'coding', 'software development', 'web development',
        'mobile development', 'api', 'microservices', 'devops', 'agile',
        'scrum', 'testing', 'debugging', 'deployment', 'ci/cd'
    ]

    content_keywords = [
        'tutorial', 'guide', 'how-to', 'tips', 'best practices', 'examples',
        'case study', 'review', 'comparison', 'analysis', 'trends', 'future',
        'innovation', 'breakthrough', 'advancement', 'research'
    ]

    # Combine all keyword categories
    all_keywords = tech_keywords + business_keywords + development_keywords + content_keywords

    found_tags = []
    tag_scores = {}  # Track relevance scores

    for keyword in all_keywords:
        if keyword in content_lower:
            # Create clean tag format
            tag = keyword.replace(' ', '-').replace('/', '-')
            if tag not in tag_scores:
                # Score based on keyword specificity and content relevance
                score = len(keyword.split()) * 2  # Longer phrases are more specific
                if keyword in ['ai', 'ml', 'api', 'vr', 'ar', 'iot']:  # High-value acronyms
                    score += 3
                tag_scores[tag] = score
                found_tags.append(tag)

    # Sort by relevance score and return top tags
    if found_tags:
        # Sort by score (highest first), then alphabetically for ties
        found_tags.sort(key=lambda x: (-tag_scores.get(x, 0), x))
        return found_tags[:6]  # Return up to 6 most relevant tags

    # Fallback for content with no keyword matches
    return ['blog', 'content', 'article']


def generate_meta_description(summary: str, max_length: int = 160) -> str:
    """Generate an SEO-friendly meta description from a summary.

    Args:
        summary: The content summary
        max_length: Maximum character length for meta description

    Returns:
        str: SEO-optimized meta description
    """
    # Clean the summary and ensure it's within limits
    clean_summary = re.sub(r'\s+', ' ', summary).strip()

    if len(clean_summary) <= max_length:
        return clean_summary

    # Truncate at word boundary if possible
    truncated = clean_summary[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > max_length * 0.8:  # Don't cut too much
        truncated = truncated[:last_space]

    return truncated + '...'


def create_featured_image_alt(title: str, tags: List[str]) -> str:
    """Generate alt text for featured blog image.

    Args:
        title: Blog post title
        tags: List of content tags

    Returns:
        str: Descriptive alt text for featured image
    """
    # Create descriptive alt text based on title and primary tag
    primary_tag = tags[0] if tags else 'content'

    alt_text = f"Featured image for blog post: {title}"

    if primary_tag:
        alt_text += f" - {primary_tag.replace('-', ' ').title()}"

    return alt_text


def format_blog_html(content: str) -> str:
    """Convert markdown-style content to properly formatted HTML."""
    html = content

    # Headers (process in reverse order to avoid conflicts)
    html = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic (handle ** and * patterns)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

    # Inline code
    html = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', html)

    # Links [text](url)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Images ![alt](url)
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', html)

    # Blockquotes
    html = re.sub(r'^> (.*)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Horizontal rules
    html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)
    html = re.sub(r'^\*\*\*+$', r'<hr>', html, flags=re.MULTILINE)

    # Lists (unordered)
    lines = html.split('\n')
    in_list = False
    formatted_lines = []

    for line in lines:
        if re.match(r'^\s*[-*+]\s+', line):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            item_content = re.sub(r'^\s*[-*+]\s+', '', line)
            formatted_lines.append(f'<li>{item_content}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(line)

    if in_list:
        formatted_lines.append('</ul>')

    html = '\n'.join(formatted_lines)

    # Ordered lists
    html = re.sub(r'(\d+\.\s.*(?:\n\d+\.\s.*)*)', lambda m: '<ol>\n' + '\n'.join(f'<li>{re.sub(r"^\d+\.\s", "", line)}</li>' for line in m.group(0).split('\n') if line.strip()) + '\n</ol>', html, flags=re.MULTILINE)

    # Tables (basic support)
    def convert_table(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)

        html_table = ['<table>']
        is_header = True

        for line in lines:
            if '|' in line and not line.startswith('|'):
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                tag = 'th' if is_header else 'td'
                html_table.append(f'<tr>{"".join(f"<{tag}>{cell}</{tag}>" for cell in cells)}</tr>')
                is_header = False

        html_table.append('</table>')
        return '\n'.join(html_table)

    html = re.sub(r'(\|.*\|(?:\n\|.*\|)+)', convert_table, html, flags=re.MULTILINE)

    # Paragraphs and line breaks
    lines = html.split('\n')
    formatted_lines = []
    current_paragraph = []

    for line in lines:
        line = line.strip()
        if line and not re.match(r'^<(h[1-6]|ul|ol|li|blockquote|p|table|tr|th|td|hr|img|a|code|strong|em)', line):
            current_paragraph.append(line)
        else:
            if current_paragraph:
                formatted_lines.append(f"<p>{' '.join(current_paragraph)}</p>")
                current_paragraph = []
            if line:
                formatted_lines.append(line)

    if current_paragraph:
        formatted_lines.append(f"<p>{' '.join(current_paragraph)}</p>")

    return '\n'.join(formatted_lines)


def create_blog_post_structure(title: str, content: str, summary: str) -> FormattedBlogPost:
    """Create a complete formatted blog post structure.

    Args:
        title: Blog post title
        content: Raw blog content
        summary: Content summary

    Returns:
        FormattedBlogPost: Complete formatted blog post
    """
    # Generate all the derived fields
    slug = generate_slug(title)
    meta_description = generate_meta_description(summary)
    reading_time = calculate_reading_time(content)
    tags = extract_tags_from_content(content)
    featured_image_alt = create_featured_image_alt(title, tags)
    formatted_content = format_blog_html(content)

    return FormattedBlogPost(
        title=title,
        meta_description=meta_description,
        slug=slug,
        content=formatted_content,
        reading_time=reading_time,
        tags=tags,
        featured_image_alt=featured_image_alt
    )
