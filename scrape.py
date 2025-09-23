from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.schemas import ScrapedResourceCreate

BOOKS_BASE = "https://books.toscrape.com/"
QUOTES_BASE = "https://quotes.toscrape.com/"


def can_fetch(base_url: str, user_agent: str, path: str) -> bool:
	rp = RobotFileParser()
	rp.set_url(urljoin(base_url, "robots.txt"))
	try:
		rp.read()
		return rp.can_fetch(user_agent, urljoin(base_url, path))
	except Exception:
		return True


def fetch_page(url: str, user_agent: str) -> str:
	headers = {"User-Agent": user_agent}
	response = requests.get(url, headers=headers, timeout=20)
	response.raise_for_status()
	return response.text


def parse_books(html: str) -> list[ScrapedResourceCreate]:
	soup = BeautifulSoup(html, "html.parser")
	items: list[ScrapedResourceCreate] = []
	for li in soup.select("ol.row li"):  # product list
		title_el = li.select_one("h3 a")
		price_el = li.select_one(".price_color")
		category = soup.select_one(".breadcrumb li.active")
		if not title_el:
			continue
		title = title_el.get("title") or title_el.text.strip()
		url = title_el.get("href", "").strip()
		price = price_el.text.strip() if price_el else None
		cat = category.text.strip() if category else ""
		items.append(
			ScrapedResourceCreate(
				source="books",
				title=title,
				url=url,
				category_or_author=cat,
				price=price,
			)
		)
	return items


def parse_quotes(html: str) -> list[ScrapedResourceCreate]:
	soup = BeautifulSoup(html, "html.parser")
	items: list[ScrapedResourceCreate] = []
	for div in soup.select("div.quote"):
		text_el = div.select_one("span.text")
		author_el = div.select_one("small.author")
		if not text_el or not author_el:
			continue
		# Normalize curly quotes and surrounding punctuation to plain text
		raw = text_el.text.strip()
		# Replace common curly quotes with straight quotes
		normalized = (
			raw.replace("“", "\"")
			.replace("”", "\"")
			.replace("‘", "'")
			.replace("’", "'")
		)
		# Trim surrounding quotes if present
		if normalized.startswith('"') and normalized.endswith('"'):
			normalized = normalized[1:-1]
		title = normalized
		author = author_el.text.strip()
		link_el = div.select_one("span a")
		url = link_el.get("href", "").strip() if link_el else ""
		items.append(
			ScrapedResourceCreate(
				source="quotes",
				title=title,
				url=url,
				category_or_author=author,
				price=None,
			)
		)
	return items


def scrape_site(site: str, pages: int, user_agent: str) -> list[ScrapedResourceCreate]:
	items: list[ScrapedResourceCreate] = []
	if site == "books":
		base = BOOKS_BASE
		if not can_fetch(base, user_agent, "/"):
			print("robots.txt disallows fetching", file=sys.stderr)
			return items
		url = base
		for page in range(1, pages + 1):
			page_url = urljoin(base, f"catalogue/page-{page}.html") if page > 1 else base
			html = fetch_page(page_url, user_agent)
			items.extend(parse_books(html))
	elif site == "quotes":
		base = QUOTES_BASE
		if not can_fetch(base, user_agent, "/"):
			print("robots.txt disallows fetching", file=sys.stderr)
			return items
		for page in range(1, pages + 1):
			page_url = urljoin(base, f"page/{page}/")
			html = fetch_page(page_url, user_agent)
			items.extend(parse_quotes(html))
	else:
		raise ValueError("Unsupported site. Use 'books' or 'quotes'.")
	return items


def save_json(items: list[ScrapedResourceCreate], path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as f:
		json.dump([i.model_dump() for i in items], f, ensure_ascii=False, indent=2)


def insert_db(items: list[ScrapedResourceCreate]) -> int:
	init_db()
	with SessionLocal() as db:  # type: Session
		from app.crud import insert_scraped_resources
		return insert_scraped_resources(db, items)


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description="Scrape books or quotes and insert into DB")
	parser.add_argument("--pages", type=int, default=1)
	parser.add_argument("--site", choices=["books", "quotes"], default="books")
	parser.add_argument("--db", default=".", help="Database URL or '.' to use env DATABASE_URL")
	parser.add_argument("--json", default="samples/scraped.json")
	args = parser.parse_args(argv)

	settings = get_settings()
	user_agent = settings.SCRAPER_USER_AGENT

	if args.db != ".":
		# Override DATABASE_URL dynamically
		settings.DATABASE_URL = args.db  # type: ignore[attr-defined]

	items = scrape_site(args.site, args.pages, user_agent)
	save_json(items, Path(args.json))
	inserted = insert_db(items)
	print(f"Scraped: {len(items)}, Inserted: {inserted}, JSON: {args.json}")
	return 0


if __name__ == "__main__":
	sys.exit(main())