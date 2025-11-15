"""Main entry point for the Content Generator blog writing engine."""

import asyncio
import argparse
import os
from dotenv import load_dotenv
from ..core.orchestrator import generate_complete_blog
from ..utils.guardrails import is_content_safe


def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment.")
        return False

    return True


def validate_topic_safety(topic: str) -> bool:
    """Check if the blog topic is safe to generate content for.

    Args:
        topic: The blog topic to validate

    Returns:
        bool: True if topic is safe, False otherwise
    """
    safety_check = is_content_safe(topic)

    if not safety_check.is_safe:
        print("❌ Topic safety check failed:")
        for issue in safety_check.issues_found:
            print(f"  - {issue}")
        print("\n💡 Recommendations:")
        for rec in safety_check.recommendations:
            print(f"  - {rec}")
        return False

    print("✅ Topic passed safety check")
    return True


async def generate_blog_post(topic: str, output_file: str = None, num_searches: int = 3, search_provider: str = "gemini", model_name: str = "gemini", medium_mode: bool = False):
    """Generate a complete blog post for the given topic.

    Args:
        topic: The blog topic to write about
        output_file: Optional file path to save the results
        num_searches: Number of web searches to perform
        search_provider: Search provider ("gemini" or "openai")
        model_name: AI model ("gemini" or "gpt-4o-mini")
        medium_mode: Whether to optimize for Medium articles
    """
    try:
        mode_desc = "Medium article" if medium_mode else "blog post"
        print(f"🎯 Generating {mode_desc} for topic: '{topic}'")
        print(f"🔍 Performing {num_searches} web searches")
        print("=" * 60)

        # Generate the blog post
        blog_post = await generate_complete_blog(topic, num_searches, search_provider, model_name, medium_mode)

        # Display results
        print("\n" + "=" * 60)
        print("📝 BLOG POST GENERATED SUCCESSFULLY")
        print("=" * 60)

        print(f"\n📖 Title: {blog_post.title}")
        print(f"🔗 Slug: {blog_post.slug}")
        print(f"⏱️  Reading Time: {blog_post.reading_time} minutes")
        print(f"🏷️  Tags: {', '.join(blog_post.tags)}")
        print(f"📄 Meta Description: {blog_post.meta_description}")
        print(f"🖼️  Featured Image Alt: {blog_post.featured_image_alt}")

        print(f"\n📝 Content Preview (first 500 chars):")
        print("-" * 40)
        content_preview = blog_post.content.replace('<p>', '').replace('</p>', '\n').replace('<h2>', '\n## ').replace('</h2>', '').replace('<h3>', '\n### ').replace('</h3>', '')
        print(content_preview[:500] + "..." if len(content_preview) > 500 else content_preview)

        # Save to file if requested
        if output_file:
            import json
            output_data = {
                "topic": topic,
                "blog_post": blog_post.model_dump()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Results saved to: {output_file}")

        print("\n✅ Blog generation completed!")

    except Exception as e:
        print(f"❌ Error during blog generation: {str(e)}")
        raise


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Content Generator - AI Blog Writing Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "The Future of Artificial Intelligence in 2025"
  python main.py "Machine Learning Best Practices" --output blog_post.json
  python main.py "Sustainable Technology Solutions" --output results.json
        """
    )

    parser.add_argument(
        'topic',
        help='The blog topic to write about'
    )

    parser.add_argument(
        '--output', '-o',
        help='Optional JSON file to save the generated blog post'
    )

    parser.add_argument(
        '--search-provider', '-p',
        choices=['gemini', 'openai'],
        default='gemini',
        help='Search provider: "gemini" (free) or "openai" (paid, $0.025/search)'
    )

    parser.add_argument(
        '--model', '-m',
        choices=['gemini', 'gpt-4o-mini'],
        default='gemini',
        help='AI model: "gemini" (free) or "gpt-4o-mini" (paid)'
    )

    parser.add_argument(
        '--searches', '-s',
        type=int,
        default=3,
        choices=range(1, 8),  # Allow 1-7 searches
        help='Number of web searches to perform (1-7, default: 3)'
    )

    parser.add_argument(
        '--medium', '-m',
        action='store_true',
        help='Optimize for Medium articles (engaging hooks, structure, formatting)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Validate environment
    if not validate_environment():
        return 1

    # Validate topic safety
    if not validate_topic_safety(args.topic):
        return 1

    # Generate blog post
    try:
        asyncio.run(generate_blog_post(args.topic, args.output, args.searches, args.search_provider, args.model, args.medium))
        return 0
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
        return 1
    except Exception as e:
        error_str = str(e).lower()
        print("\n❌ Error occurred:")
        if "api_key" in error_str and "invalid" in error_str:
            print("API Key Error: Invalid API key. Check your GOOGLE_API_KEY or OPENAI_API_KEY")
        elif "quota" in error_str or "rate limit" in error_str:
            print("Quota Exceeded: API quota limit reached. Try again later or use different model")
        elif "network" in error_str or "connection" in error_str:
            print("Network Error: Unable to connect to AI services. Check internet connection")
        elif "timeout" in error_str:
            print("Timeout Error: Request took too long. Try fewer searches or simpler topic")
        elif "safety" in error_str or "blocked" in error_str:
            print("Content Blocked: Topic contains sensitive content that cannot be processed")
        else:
            print(f"Unexpected Error: {str(e)[:100]}...")
        return 1


if __name__ == "__main__":
    exit(main())
