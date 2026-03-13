import os
from urllib.parse import urlparse
from app.config import OUTPUT_DIR

def generate_llms(pages):

    sections = set()

    for url in pages:

        path = urlparse(url).path.split("/")

        if len(path) > 1 and path[1]:
            sections.add(path[1])

    content = "\n".join(f"- /{s}" for s in sections)

    text = f"""# LLMs.txt

Main sections:

{content}
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    path = f"{OUTPUT_DIR}/llms.txt"

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return text