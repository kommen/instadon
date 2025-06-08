# InstaDon

Cross-post from Instagram to Mastodon with automatic text summarization and duplicate prevention.

## Features

- Fetches latest Instagram posts using instaloader
- Downloads media via Cobalt API
- Summarizes long captions using OpenRouter/DeepSeek
- Prevents duplicate posts
- Creates Mastodon drafts

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Basic usage
instadon kulturneubau

# With custom visibility
instadon kulturneubau --visibility unlisted
```

## Configuration

Create a `.env` file:
```
MASTODON_INSTANCE=https://your-instance.social
MASTODON_ACCESS_TOKEN=your_token
OPENROUTER_API_KEY=your_key
```
