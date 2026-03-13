import asyncio
from urllib.parse import urljoin, urlparse, urlunparse
from collections import defaultdict
import httpx
from bs4 import BeautifulSoup
import tldextract
import networkx as nx
from app.models.page import Page
from app.config import MAX_PAGES, WORKERS, BLOCK_PATHS
from app.utils.sitemap import generate_sitemap
from app.utils.robots import generate_robots
from app.utils.llms import generate_llms

class FastCrawler:

    def __init__(self, base_url, depth):

        self.base_url = self.normalize(base_url)
        self.depth_limit = depth

        ext = tldextract.extract(base_url)
        self.domain = f"{ext.domain}.{ext.suffix}"

        self.pages = {}
        self.visited = set()

        self.queue = asyncio.Queue()

        self.errors = {"4xx": [], "5xx": []}
        self.meta = defaultdict(list)

        self.graph = nx.DiGraph()

    def normalize(self, url):

        parsed = urlparse(url)

        return urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", "")
        )

    def is_internal(self, url):

        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}"

        return domain == self.domain

    def blocked(self, url):

        path = urlparse(url).path

        return any(path.startswith(p) for p in BLOCK_PATHS)

    async def fetch(self, client, url):

        try:
            r = await client.get(url, timeout=10)
            return r.status_code, r.text
        except:
            return 500, ""

    async def worker(self, client):

        while True:

            url, depth = await self.queue.get()

            if url in self.visited or len(self.visited) >= MAX_PAGES:
                self.queue.task_done()
                continue

            self.visited.add(url)

            page = Page(url)
            self.pages[url] = page

            status, html = await self.fetch(client, url)

            page.status = status

            if 400 <= status < 500:
                self.errors["4xx"].append(url)
                self.queue.task_done()
                continue

            if status >= 500:
                self.errors["5xx"].append(url)
                self.queue.task_done()
                continue

            soup = BeautifulSoup(html, "html.parser")

            title = soup.title.get_text(strip=True) if soup.title else None

            desc_tag = soup.find("meta", attrs={"name": "description"})
            desc = desc_tag.get("content", "").strip() if desc_tag else None

            h1_tag = soup.find("h1")
            h1 = h1_tag.get_text(strip=True) if h1_tag else None

            page.title = title
            page.description = desc
            page.h1 = h1

            if depth < self.depth_limit:

                for a in soup.find_all("a", href=True):

                    link = self.normalize(urljoin(url, a["href"]))

                    if not self.is_internal(link):
                        continue

                    if self.blocked(link):
                        continue

                    page.out_links.add(link)

                    if link not in self.pages:
                        self.pages[link] = Page(link)

                    self.pages[link].in_links.add(url)

                    self.graph.add_edge(url, link)

                    await self.queue.put((link, depth + 1))

            self.queue.task_done()

    async def crawl(self):

        await self.queue.put((self.base_url, 0))

        async with httpx.AsyncClient(follow_redirects=True) as client:

            workers = [
                asyncio.create_task(self.worker(client))
                for _ in range(WORKERS)
            ]

            await self.queue.join()

            for w in workers:
                w.cancel()

    def report(self):

        sitemap = generate_sitemap(self.pages.keys())
        robots = generate_robots(self.base_url)
        llms = generate_llms(self.pages.keys())

        return {
            "pages_scanned": len(self.pages),
            "errors": self.errors,
            "meta_issues": dict(self.meta),
            "sitemap_xml": sitemap,
            "robots_txt": robots,
            "llms_txt": llms,
        }