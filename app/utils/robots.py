import os
from app.config import OUTPUT_DIR

def generate_robots(base_url):

    robots = f"""User-agent: *
Allow: /

Disallow: /admin/
Disallow: /login/
Disallow: /cart/

Sitemap: {base_url}/sitemap.xml
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    path = f"{OUTPUT_DIR}/robots.txt"

    with open(path, "w", encoding="utf-8") as f:
        f.write(robots)

    return robots