import logging
from openai import OpenAI
from typing import Optional
from .config import CONFIG

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        self.client = OpenAI(
            api_key=CONFIG["openrouter"]["api_key"],
            base_url=CONFIG["openrouter"]["base_url"]
        )
        self.model = CONFIG["openrouter"]["model"]
        self.max_chars = 500

    def summarize_if_needed(self, text: str) -> str:
        """Process text and summarize if it exceeds character limit."""
        if not text:
            return text

        if len(text) <= self.max_chars:
            logger.info(f"Text length {len(text)} chars - processing @-mentions only")
            return self._process_mentions_only(text)

        logger.info(f"Text length {len(text)} chars - summarizing with OpenRouter")
        return self._summarize_text(text)

    def _summarize_text(self, text: str) -> str:
        """Use OpenRouter to summarize the text."""
        prompt = f"""Please summarize this social media post to fit within 500 characters while preserving the key message and tone.

IMPORTANT: You must respond in the exact same language as the input text. If the input is in German, respond in German. If it's in English, respond in English. Do not translate or change the language.

Replace @-mentions with names. Only use very common abbreviations. Don't use any ascii formatting except for list items. Preserve emojis and formatting like lists done with emojis. Keep it engaging and authentic.

Only reply with the summarized text (no stats, no quotes around the summary):

{text}

Summary (max 500 chars, same language as input):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()

            # Ensure it's within limit
            if len(summary) > self.max_chars:
                summary = summary[:self.max_chars-3] + "..."

            logger.info(f"Summarized from {len(text)} to {len(summary)} chars")
            logger.info(f"Summary: {summary}")

            return summary

        except Exception as e:
            logger.error(f"Failed to summarize text: {e}")
            # Fallback: truncate with ellipsis
            fallback = text[:self.max_chars-3] + "..."
            logger.info(f"Using fallback truncation: {len(fallback)} chars")
            return fallback

    def _process_mentions_only(self, text: str) -> str:
        """Process @-mentions without summarizing."""
        prompt = f"""Please process this social media post by replacing @-mentions (usernames starting with @) with names derived from them, but do NOT summarize or shorten the text.

IMPORTANT: You must respond in the exact same language as the input text. If the input is in German, respond in German. If it's in English, respond in English. Do not translate or change the language.

Keep the original text length and content exactly the same, only replace @-mentions with readable names. Preserve all emojis, formatting, and structure.

Only reply with the processed text (no quotes around it):

{text}

Processed text (same language as input):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )

            processed_text = response.choices[0].message.content.strip()
            
            logger.info(f"Processed @-mentions: {len(text)} -> {len(processed_text)} chars")
            logger.info(f"Processed text: {processed_text}")

            return processed_text

        except Exception as e:
            logger.error(f"Failed to process @-mentions: {e}")
            # Fallback: return original text
            logger.info(f"Using original text as fallback")
            return text
