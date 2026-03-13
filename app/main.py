from fastapi import FastAPI
from app.models.request import AuditRequest
from app.crawler.fast_crawler import FastCrawler

app = FastAPI(title="Fast SEO Auditor")

@app.post("/audit")
async def audit(req: AuditRequest):

    crawler = FastCrawler(req.url, req.depth)

    await crawler.crawl()

    return crawler.report()