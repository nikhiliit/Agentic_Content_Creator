"""Output guardrails for content safety in the blog writing engine."""

from agents import GuardrailFunctionOutput
from ..core.schemas import ContentSafetyCheck, MediumStructureValidation, MediumBlogContent


async def content_safety_guardrail(ctx, agent, message):
    """Guardrail to prevent generation of content on sensitive political topics.

    This guardrail checks if the content involves politically sensitive topics
    that could lead to legal issues or platform violations.
    """
    # More specific sensitive topics - focus on clearly political content
    sensitive_phrases = [
        "political party", "political leader", "political campaign",
        "government policy", "government regulation", "government law",
        "election results", "election fraud", "voting rights",
        "political scandal", "political corruption", "political controversy",
        "political protest", "political revolution", "political uprising",
        "parliament debate", "congress vote", "presidential election",
        "political candidate", "political ideology", "political system",
        "politics", "election", "government", "policy", "regulation",
        "legislation", "candidate", "voting", "democracy"
    ]

    # Check the message content for sensitive topics
    message_lower = message.lower()
    found_topics = []

    # Check for sensitive political phrases
    for phrase in sensitive_phrases:
        if phrase in message_lower:
            # Special handling for "regulation" - allow in tech contexts
            if phrase == "regulation":
                # Allow regulation in technological contexts
                tech_keywords = [
                    "ai", "data", "privacy", "gdpr", "machine learning",
                    "algorithm", "tech", "digital", "software", "cybersecurity",
                    "artificial intelligence", "ml", "deep learning", "neural network",
                    "computer vision", "nlp", "natural language processing",
                    "machine unlearning", "unlearning", "federated learning"
                ]
                in_tech_context = False
                for keyword in tech_keywords:
                    if keyword in message_lower:
                        in_tech_context = True
                        break

                # Only flag regulation if not in tech context
                if not in_tech_context:
                    found_topics.append(phrase)
                # If in tech context, don't add to found_topics (allow it)
            else:
                found_topics.append(phrase)

    # Note: "revolution" is now allowed in all contexts (technological, scientific, etc.)
    # No special filtering needed for revolution-related terms

    # If sensitive topics found, trigger guardrail
    if found_topics:
        safety_check = ContentSafetyCheck(
            is_safe=False,
            issues_found=[f"Contains sensitive topic: {topic}" for topic in found_topics],
            recommendations=[
                "Avoid political topics to prevent legal issues",
                "Focus on technology, business, or educational content",
                "Consider neutral, informative topics instead"
            ]
        )

        return GuardrailFunctionOutput(
            output_info={"safety_check": safety_check.model_dump()},
            tripwire_triggered=True
        )

    # Content is safe
    safety_check = ContentSafetyCheck(
        is_safe=True,
        issues_found=[],
        recommendations=[]
    )

    return GuardrailFunctionOutput(
        output_info={"safety_check": safety_check.model_dump()},
        tripwire_triggered=False
    )


def is_content_safe(content: str) -> ContentSafetyCheck:
    """Utility function to check if content contains sensitive topics.

    Args:
        content: The text content to check

    Returns:
        ContentSafetyCheck: Results of the safety evaluation
    """
    # More specific sensitive topics - focus on clearly political content
    sensitive_phrases = [
        "political party", "political leader", "political campaign",
        "government policy", "government regulation", "government law",
        "election results", "election fraud", "voting rights",
        "political scandal", "political corruption", "political controversy",
        "political protest", "political revolution", "political uprising",
        "parliament debate", "congress vote", "presidential election",
        "political candidate", "political ideology", "political system",
        "politics", "election", "government", "policy", "regulation",
        "legislation", "candidate", "voting", "democracy"
    ]

    content_lower = content.lower()
    found_topics = []

    # Check for sensitive political phrases
    for phrase in sensitive_phrases:
        if phrase in content_lower:
            # Special handling for "regulation" - allow in tech contexts
            if phrase == "regulation":
                # Allow regulation in technological contexts
                tech_keywords = [
                    "ai", "data", "privacy", "gdpr", "machine learning",
                    "algorithm", "tech", "digital", "software", "cybersecurity",
                    "artificial intelligence", "ml", "deep learning", "neural network",
                    "computer vision", "nlp", "natural language processing",
                    "machine unlearning", "unlearning", "federated learning"
                ]
                in_tech_context = False
                for keyword in tech_keywords:
                    if keyword in content_lower:
                        in_tech_context = True
                        break

                # Only flag regulation if not in tech context
                if not in_tech_context:
                    found_topics.append(phrase)
                # If in tech context, don't add to found_topics (allow it)
            else:
                found_topics.append(phrase)

    # Note: "revolution" is now allowed in all contexts (technological, scientific, etc.)
    # No special filtering needed for revolution-related terms

    if found_topics:
        return ContentSafetyCheck(
            is_safe=False,
            issues_found=[f"Contains sensitive topic: {topic}" for topic in found_topics],
            recommendations=[
                "Avoid political topics to prevent legal issues",
                "Focus on technology, business, or educational content",
                "Consider neutral, informative topics instead"
            ]
        )

    return ContentSafetyCheck(
        is_safe=True,
        issues_found=[],
        recommendations=[]
    )


def validate_medium_structure(content: MediumBlogContent) -> MediumStructureValidation:
    """Validate Medium blog content structure and optimization.

    Args:
        content: MediumBlogContent to validate

    Returns:
        MediumStructureValidation: Detailed validation results
    """
    issues = []
    recommendations = []

    # Hook effectiveness (1-10)
    hook_score = 0
    if content.hook:
        hook_length = len(content.hook.split())
        if 50 <= hook_length <= 150:  # Good hook length
            hook_score += 4
        elif hook_length < 50:
            hook_score += 2
            issues.append("Hook too short - expand to 50-150 words for better engagement")
            recommendations.append("Make hook more detailed with a story, statistic, or compelling statement")

        # Check for engaging elements
        engaging_words = ["surprising", "shocking", "revealed", "discovered", "truth", "mistake", "secret", "never knew"]
        has_engaging = any(word in content.hook.lower() for word in engaging_words)
        if has_engaging:
            hook_score += 3
        else:
            hook_score += 1
            recommendations.append("Add more engaging language to hook (surprising, shocking, revealed, etc.)")
    else:
        hook_score = 0
        issues.append("Missing hook - articles need strong opening")
        recommendations.append("Add compelling hook with story, statistic, or bold statement")

    # Structure compliance (1-10)
    structure_score = 0
    if content.title and len(content.title.split()) >= 5:
        structure_score += 2
    else:
        issues.append("Title too short or missing")
        recommendations.append("Create compelling, benefit-driven title (5+ words)")

    if content.subtitle and len(content.subtitle.split()) >= 8:
        structure_score += 2
    else:
        issues.append("Subtitle too short or missing")
        recommendations.append("Add informative subtitle that intrigues without giving away too much")

    if content.preview:
        structure_score += 2
    else:
        issues.append("Missing preview/promise section")
        recommendations.append("Add clear preview of what readers will learn")

    # Check for H2 markers in sections_content
    h2_count = content.sections_content.count("**H2:**")
    if 3 <= h2_count <= 7:
        structure_score += 2
    else:
        issues.append(f"Wrong number of sections: {h2_count} (need 3-7)")
        recommendations.append("Use **H2:** markers for 3-7 section headers")

    if content.conclusion:
        structure_score += 1
    else:
        issues.append("Missing conclusion")
        recommendations.append("Add strong conclusion with key takeaways and call-to-action")

    # Engagement elements (1-10)
    engagement_score = 0

    pull_quote_count = content.sections_content.count("**PULL_QUOTE:**")
    if pull_quote_count >= 2:
        engagement_score += 3
    elif pull_quote_count >= 1:
        engagement_score += 2
    else:
        issues.append("Need more pull quotes (minimum 2)")
        recommendations.append("Add **PULL_QUOTE:** markers for key insights")

    bold_count = content.sections_content.count("**BOLD:**")
    if bold_count >= 3:
        engagement_score += 3
    elif bold_count >= 1:
        engagement_score += 2
    else:
        issues.append("Need more bold highlights (minimum 3)")
        recommendations.append("Use **BOLD:** markers to emphasize key points")

    # Check for examples and stats in content
    example_keywords = ["example", "case study", "instance", "scenario", "situation"]
    has_examples = any(keyword in content.sections_content.lower() for keyword in example_keywords)
    if has_examples:
        engagement_score += 2
    else:
        issues.append("Need real examples or case studies")
        recommendations.append("Include real examples and case studies for credibility")

    stat_keywords = ["statistic", "data", "research", "study", "survey", "percent", "number"]
    has_stats = any(keyword in content.sections_content.lower() for keyword in stat_keywords)
    if has_stats:
        engagement_score += 2
    else:
        issues.append("Need statistics or data points")
        recommendations.append("Add relevant statistics to support claims")

    # Calculate total words
    total_words = len(content.hook.split()) + len(content.preview.split()) + len(content.sections_content.split()) + len(content.conclusion.split())

    # Length optimization (1-10)
    length_score = 0
    if 1400 <= total_words <= 2000:
        length_score = 10
    elif 1200 <= total_words < 1400:
        length_score = 8
        recommendations.append("Consider expanding slightly for optimal 7-10 minute read")
    elif 2000 < total_words <= 2500:
        length_score = 7
        recommendations.append("Consider condensing slightly to maintain engagement")
    elif total_words < 1000:
        length_score = 4
        issues.append("Article significantly too short")
        recommendations.append("Expand substantially for Medium's engagement sweet spot")
    else:
        length_score = 5
        issues.append("Article length outside Medium's optimal range")
        recommendations.append("Aim for 1400-2000 words for best Medium performance")

    # Calculate overall score
    overall_score = int((hook_score + structure_score + engagement_score + length_score) / 4)

    # Determine if medium optimized
    is_medium_optimized = overall_score >= 7 and len(issues) <= 2

    return MediumStructureValidation(
        is_medium_optimized=is_medium_optimized,
        hook_score=min(10, hook_score),
        structure_score=min(10, structure_score),
        engagement_score=min(10, engagement_score),
        length_score=length_score,
        issues_found=issues,
        recommendations=recommendations,
        overall_score=overall_score
    )
