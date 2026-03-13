import os
from app.config import OUTPUT_DIR

def generate_sitemap(urls):

    content = "\n".join(
        f"<url><loc>{u}</loc></url>" for u in urls
    )

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{content}
</urlset>
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    path = f"{OUTPUT_DIR}/sitemap.xml"

    with open(path, "w", encoding="utf-8") as f:
        f.write(sitemap)

    return sitemap