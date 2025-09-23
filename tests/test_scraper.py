from __future__ import annotations

from scrape import parse_books, parse_quotes


def test_parse_books_minimal():
	html = """
	<html>
	<body>
		<ul class="breadcrumb"><li></li><li></li><li class="active">Travel</li></ul>
		<ol class="row">
			<li>
				<h3><a title="Book One" href="/book1.html">Book One</a></h3>
				<p class="price_color">£51.77</p>
			</li>
		</ol>
	</body>
	</html>
	"""
	items = parse_books(html)
	assert len(items) == 1
	item = items[0]
	assert item.source == "books"
	assert item.title == "Book One"
	assert item.category_or_author == "Travel"
	assert item.price == "£51.77"


def test_parse_quotes_minimal():
	html = """
	<html>
	<body>
		<div class="quote">
			<span class="text">“Be yourself; everyone else is already taken.”</span>
			<small class="author">Oscar Wilde</small>
			<span><a href="/author/oscar-wilde">About</a></span>
		</div>
	</body>
	</html>
	"""
	items = parse_quotes(html)
	assert len(items) == 1
	item = items[0]
	assert item.source == "quotes"
	assert item.title.startswith("Be yourself")
	assert item.category_or_author == "Oscar Wilde"