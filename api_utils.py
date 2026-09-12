import time
from google.genai import errors

def safe_generate(client, **kwargs):
    """Wraps generate_content with retry-on-429 using progressive backoff."""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(**kwargs)
        except errors.ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 20 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s before retry ({attempt+1}/{max_retries})...")
                time.sleep(wait)
                continue
            raise