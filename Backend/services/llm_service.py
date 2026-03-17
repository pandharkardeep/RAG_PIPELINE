"""
LLM Service — NVIDIA DeepSeek V3.2
Uses deepseek-ai/deepseek-v3.2 via NVIDIA NIM (OpenAI-compatible API).
Replaces the local llama-cpp model with a cloud-hosted, much more capable model.
"""

from openai import OpenAI
from config import NVIDIA_DEEPSEEK_API_KEY
import json
import re


class LLMService:
    """
    Service for generating elite-quality tweets using a 2-stage LLM pipeline:
    1. Extract key insights from context
    2. Generate diverse tweet styles with tone control
    """

    # NVIDIA NIM endpoint
    _BASE_URL = "https://integrate.api.nvidia.com/v1"
    _MODEL_ID = "deepseek-ai/deepseek-v3.2"

    # ─── Banned Phrases ──────────────────────────────────────────────
    BANNED_PHRASES = [
        "In today's world", "It is important to note", "This highlights",
        "In conclusion", "The future of X is bright", "This shows that",
        "It's worth noting", "As we can see", "Moving forward",
        "At the end of the day", "It goes without saying",
        "In the ever-evolving", "In this day and age",
        "game-changer", "redefining", "proving that", "isn't just",
        "has already", "is a major", "marking a major",
    ]

    # ─── Tone Definitions ────────────────────────────────────────────
    TONE_INSTRUCTIONS = {
        "sharp": "Be direct, punchy, and thought-provoking. Cut through the noise with razor-sharp clarity.",
        "analytical": "Break down complex ideas with precision. Use data-driven framing and logical structure.",
        "contrarian": "Challenge conventional wisdom. Take the opposite stance and back it up with insight.",
        "optimistic": "Highlight opportunities and breakthroughs. Be genuinely excited, not fake-positive.",
        "cautionary": "Warn about hidden risks and overlooked dangers. Be the voice of reason.",
        "visionary": "Paint a picture of the future. Connect dots others don't see. Be bold in predictions.",
    }

    # ─── Few-Shot Thread Example ─────────────────────────────────────
    FEW_SHOT_EXAMPLE = """
Here is an example of the EXACT format and quality I want. Study it carefully:

---
Topic: AI coding tools

The "AI-assisted coding" hype is misleading.
Most devs aren't using AI to write code.
They're using it to avoid reading documentation.
The Productivity Illusion: A Thread

1/
The Promise vs. Reality
AI code completion saves ~30% of keystrokes.
But studies show developers spend 60% of time READING code, not writing it.
Keystroke savings on 40% of the job is not the revolution we were sold.

2/
The Copy-Paste Trap
GitHub data shows AI-generated PRs have 2x the revert rate.
Why? Devs accept suggestions without understanding them.
Speed up input. Slow down comprehension.
Net effect? Often negative.

3/
Where AI Actually Wins
Boilerplate. Tests. Regex. Config files.
The boring stuff nobody wants to write.
Here, AI saves real hours.
But nobody makes headlines saying "AI writes great YAML."

4/
The Hidden Cost
Junior devs who learn with AI never build mental models.
They can ship code. They can't debug code.
We are training a generation of assemblers, not engineers.

5/
The Bottom Line
AI coding tools are a power tool, not autopilot.
Power tools in skilled hands: transformative.
Power tools in untrained hands: dangerous.
Which one is your team building toward?
---

Match this style EXACTLY: numbered parts, subtitle per tweet, short punchy lines, specific data, narrative arc.
"""

    def __init__(self):
        """
        Initialize the LLM service with NVIDIA DeepSeek V3.2.
        No local model download needed — runs via cloud API.
        """
        if not NVIDIA_DEEPSEEK_API_KEY:
            raise RuntimeError("NVIDIA_DEEPSEEK_API_KEY is not set in environment variables.")

        self.client = OpenAI(
            api_key=NVIDIA_DEEPSEEK_API_KEY,
            base_url=self._BASE_URL,
        )
        print(f"✓ LLM Service initialized (model={self._MODEL_ID})")

    # ─── Generic Chat Completion ─────────────────────────────────────

    def chat_completion(self, messages: list, max_tokens: int = 4096,
                        temperature: float = 0.7, top_p: float = 0.95,
                        thinking: bool = False) -> str:
        """
        Generic chat completion method.
        Used by tweet generation AND data extraction service.

        Args:
            messages: OpenAI-format message list
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling
            thinking: Enable deepseek thinking mode (chain-of-thought)

        Returns:
            str: The generated text content
        """
        extra_body = {}
        if thinking:
            extra_body["chat_template_kwargs"] = {"thinking": True}

        # Use streaming to collect the full response
        completion = self.client.chat.completions.create(
            model=self._MODEL_ID,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            extra_body=extra_body if extra_body else None,
            stream=True,
        )

        content_parts = []
        reasoning_parts = []
        for chunk in completion:
            if not getattr(chunk, "choices", None):
                continue
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # Collect reasoning tokens (thinking mode)
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                reasoning_parts.append(reasoning)

            # Collect actual content tokens
            content = getattr(delta, "content", None)
            if content:
                content_parts.append(content)

        if reasoning_parts:
            print(f"  🧠 DeepSeek reasoning: {len(reasoning_parts)} tokens")

        result = "".join(content_parts).strip()

        # Fallback: if content is empty but we got reasoning, the model
        # may have put the answer inside the reasoning block (NVIDIA quirk)
        if not result and reasoning_parts:
            print("  ⚠ No content tokens found, extracting from reasoning output")
            result = "".join(reasoning_parts).strip()

        return result

    # ─── Context Formatting ──────────────────────────────────────────

    def _format_context(self, context_articles: list, max_articles: int = 5,
                        max_chars: int = 500) -> str:
        """
        Format context articles concisely for LLM consumption.
        Keeps it tight to avoid context degradation.
        """
        if not context_articles:
            return ""

        formatted = ""
        for i, article in enumerate(context_articles[:max_articles], 1):
            text = article.get('text', '')[:max_chars]
            source = article.get('filename', 'Unknown')
            formatted += f"Source {i} ({source}):\n{text}\n\n"

        return formatted.strip()

    # ─── Stage 1: Extract Insights ───────────────────────────────────

    def _extract_insights(self, query: str, formatted_context: str) -> list:
        """
        Stage 1: Extract key insights from context before writing tweets.
        Forces the LLM to think before writing.
        """
        if not formatted_context:
            return [f"Key developments in {query}"]

        messages = [
            {
                "role": "system",
                "content": "You are a research analyst. Extract key insights from articles. Return a JSON array of 5 insight strings. Only return the JSON array, nothing else."
            },
            {
                "role": "user",
                "content": f"""Topic: {query}

Articles:
{formatted_context}

Extract exactly 5 key insights that would make compelling tweet content.
Focus on: surprising facts, counterintuitive findings, concrete data points, emerging trends, hidden risks.

Return as JSON array: ["insight 1", "insight 2", ...]"""
            }
        ]

        try:
            content = self.chat_completion(
                messages=messages,
                max_tokens=512,
                temperature=0.3,
            )
            # Parse JSON array
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                if isinstance(insights, list) and len(insights) > 0:
                    print(f"✓ Stage 1: Extracted {len(insights)} insights")
                    return insights

            print("⚠ Stage 1: Could not parse insights, using fallback")
            return [f"Key developments in {query}"]

        except Exception as e:
            print(f"⚠ Stage 1 error: {e}")
            return [f"Key developments in {query}"]

    # ─── Stage 2: Generate Tweets ────────────────────────────────────

    def _generate_tweets_from_insights(
        self, query: str, insights: list, count: int,
        max_length: int, tone: str, formatted_context: str
    ) -> list:
        """
        Stage 2: Generate diverse, high-quality tweets from extracted insights.
        Uses style variety and tone control with DeepSeek V3.2.
        """
        tone_instruction = self.TONE_INSTRUCTIONS.get(tone, self.TONE_INSTRUCTIONS["sharp"])
        banned_list = "\n".join(f'- "{phrase}"' for phrase in self.BANNED_PHRASES)

        system_prompt = f"""You are an elite Twitter thread writer. You write deep-dive analytical threads that go viral.

THREAD FORMAT (follow EXACTLY):
- Start with a HOOK tweet: a provocative claim (3-4 short lines) + a subtitle like "A Deep Dive" or "A Thread"
- The hook tweet MUST have substance, not just a title. Include 3-4 punchy lines before the subtitle.
- Then numbered tweets: 1/, 2/, 3/ etc.
- Each numbered tweet has a SHORT SUBTITLE on its own line (e.g. "The Promise vs. Reality")
- MAXIMUM 5-6 lines per tweet. Keep them tight.
- One sentence per line. Line breaks between sentences.
- Use specific data: numbers, percentages, currency, comparisons.
- Build a NARRATIVE ARC: hook → setup → evidence → tension → resolution → conclusion
- End with a strong closing tweet that reframes the topic + optional call to action

STRICT FORMATTING RULES:
- NO markdown formatting. No **, no __, no #. Write plain text ONLY.
- NO direct quotes from people. Paraphrase instead.
- NO long paragraphs. Every sentence gets its own line.
- Sound like a smart analyst, NOT an AI summarizer.
- Be opinionated. Take a stance.
- Use contrast: "X is not Y. It's Z."
- Name specific companies, products, numbers.
- No hashtags. Minimal emojis (only flags or data-relevant ones).

BANNED PHRASES (never use):
{banned_list}

Tone: {tone_instruction}

{self.FEW_SHOT_EXAMPLE}

OUTPUT FORMAT:
Return the thread as plain text. Start with the hook tweet, then numbered tweets (1/, 2/, ...).
Do NOT use markdown. Do NOT add metadata. Just write the thread."""

        insights_text = "\n".join(f"- {ins}" for ins in insights)

        user_prompt = f"""Topic: {query}

Key Insights:
{insights_text}

Context:
{formatted_context[:2000] if formatted_context else 'No additional context.'}

Write a Twitter thread with exactly {count} tweets (hook + {count - 1} numbered parts).
Each tweet should have a subtitle, short lines, and specific data where possible.
Build a narrative arc from hook to conclusion.

Write the thread now:"""

        try:
            content = self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4096,  # deepseek can handle much more
                temperature=0.75,
                top_p=0.9,
            )
            print(f"Stage 2 raw output:\n{content}")

            # Parse thread output
            tweets = self._parse_thread(content, count)

            # Strip any markdown the LLM might have added despite instructions
            tweets = [self._clean_markdown(t) for t in tweets]

            if tweets:
                print(f"✓ Stage 2: Generated {len(tweets)} thread tweets")
                return tweets

            # Fallback: try paragraph splitting
            print("⚠ Stage 2: Thread parse failed, falling back to text split")
            return self._fallback_parse(content, count)

        except Exception as e:
            print(f"❌ Stage 2 error: {e}")
            return []

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Strip markdown formatting from tweet text."""
        text = text.replace('**', '')
        text = text.replace('__', '')
        # Remove leading # headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        return text.strip()

    def _parse_thread(self, content: str, count: int) -> list:
        """Parse thread-style output into individual tweets."""
        tweets = []

        # Find all numbered markers: 1/, 2/, 3/ etc
        markers = list(re.finditer(r'(?:^|\n)\s*(\d+)/', content))

        if markers:
            # Everything before the first marker is the hook
            hook = content[:markers[0].start()].strip()
            if hook and len(hook) > 20:
                tweets.append(hook)

            # Extract each numbered tweet
            for idx, m in enumerate(markers):
                num = m.group(1)
                start = m.end()
                end = markers[idx + 1].start() if idx + 1 < len(markers) else len(content)
                tweet_content = content[start:end].strip()
                if tweet_content and len(tweet_content) > 20:
                    tweets.append(f"{num}/\n{tweet_content}")

        # If regex didn't find numbered markers, try double-newline split
        if len(tweets) < 2:
            tweets = []
            for block in content.split('\n\n'):
                block = block.strip()
                if block and len(block) > 20:
                    tweets.append(block)

        return tweets if tweets else []

    def _fallback_parse(self, content: str, count: int) -> list:
        """Fallback parsing when thread format fails."""
        tweets = []

        # Try JSON first
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                raw = json.loads(json_match.group())
                for item in raw:
                    if isinstance(item, str) and len(item.strip()) > 20:
                        tweets.append(item.strip())
                    elif isinstance(item, dict):
                        t = item.get('tweet', '').strip()
                        if t and len(t) > 20:
                            tweets.append(t)
                    elif isinstance(item, list) and len(item) > 0:
                        t = str(item[0]).strip()
                        if t and len(t) > 20:
                            tweets.append(t)
                if tweets:
                    return tweets[:count]
        except Exception:
            pass

        # Double newline split
        for para in content.split('\n\n'):
            para = para.strip()
            if not para or len(para) < 20:
                continue
            lower = para.lower()
            if any(skip in lower for skip in [
                'here are', 'here is', 'based on', 'output', 'tweet must'
            ]):
                continue
            tweets.append(para)

        return tweets[:count]

    # ─── Main Entry Point ────────────────────────────────────────────

    def generate_tweets(
        self, query: str, count: int = 8, max_length: int = 280,
        context_articles: list = None, tone: str = "sharp"
    ) -> list:
        """
        Generate elite-quality tweet threads using a 2-stage pipeline:
        1. Extract insights from context (think before writing)
        2. Generate narrative thread with style variety

        Args:
            query: Topic to generate tweets about
            count: Number of tweets to generate
            max_length: Maximum characters per tweet
            context_articles: RAG context articles
            tone: Writing tone (sharp/analytical/contrarian/optimistic/cautionary/visionary)

        Returns:
            List of high-quality tweet strings
        """
        # Validate tone
        if tone not in self.TONE_INSTRUCTIONS:
            tone = "sharp"

        print(f"🚀 Starting 2-stage tweet pipeline | topic: {query} | tone: {tone} | count: {count}")

        # Format context
        formatted_context = self._format_context(context_articles)

        # Stage 1: Extract insights
        print("── Stage 1: Extracting insights ──")
        insights = self._extract_insights(query, formatted_context)

        # Stage 2: Generate exactly count tweets
        print(f"── Stage 2: Generating {count} thread tweets ──")
        tweets = self._generate_tweets_from_insights(
            query, insights, count, max_length, tone, formatted_context
        )

        if not tweets:
            print("⚠ Stage 2 produced no tweets, using fallback")
            return [
                f"The {query} landscape is shifting fast.\n"
                f"Most people aren't paying attention.\n"
                f"Here's what the data actually shows:"
                for _ in range(count)
            ]

        # Pad if we got fewer than requested
        while len(tweets) < count:
            tweets.append(
                f"The conversation around {query} is evolving.\n"
                f"The real question isn't what's next.\n"
                f"It's who adapts first."
            )

        print(f"✓ Pipeline complete: {len(tweets[:count])} thread tweets")
        return tweets[:count]
