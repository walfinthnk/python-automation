import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from datetime import date
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/"
USER_AGENT = "Mozilla/5.0 (compatible; PythonScraper/1.0)"


def load_robots_txt(base_url):
    rp = RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    try:
        rp.read()
        logger.info("robots.txt を読み込みました")
    except Exception as e:
        logger.warning(f"robots.txt の読み込みに失敗しました（アクセス許可として続行）: {e}")
    return rp


def fetch_page(url, session):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.ConnectionError as e:
        logger.error(f"接続エラーが発生しました: {e}")
        raise SystemExit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"リクエストエラーが発生しました: {e}")
        raise SystemExit(1)


def parse_books(html):
    soup = BeautifulSoup(html, "lxml")
    books = []
    for article in soup.select("article.product_pod"):
        title = article.select_one("h3 a")["title"]
        price = article.select_one("p.price_color").text.strip()
        availability = article.select_one("p.availability").text.strip()
        books.append({"title": title, "price": price, "availability": availability})
    return books


def get_next_page_url(html, current_url):
    soup = BeautifulSoup(html, "lxml")
    next_btn = soup.select_one("li.next a")
    if next_btn:
        return urljoin(current_url, next_btn["href"])
    return None


def save_to_markdown(books, filename):
    today = date.today().strftime("%Y-%m-%d")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Books Scraping Results\n\n")
        f.write(f"収集日: {today}  \n")
        f.write(f"合計: {len(books)} 冊\n\n")
        f.write("| タイトル | 価格 | 在庫状況 |\n")
        f.write("|---------|------|----------|\n")
        for book in books:
            title = book["title"].replace("|", "｜")
            f.write(f"| {title} | {book['price']} | {book['availability']} |\n")
    logger.info(f"{filename} に保存しました（{len(books)} 冊）")


def main():
    output_file = f"books_{date.today().strftime('%Y%m%d')}.md"

    rp = load_robots_txt(BASE_URL)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    all_books = []
    current_url = BASE_URL
    page_num = 1

    while current_url:
        if not rp.can_fetch(USER_AGENT, current_url):
            logger.warning(f"robots.txt によりアクセス禁止: {current_url} — スキップして終了します")
            break

        logger.info(f"ページ {page_num} 取得中: {current_url}")
        html = fetch_page(current_url, session)
        books = parse_books(html)
        all_books.extend(books)
        logger.info(f"  → {len(books)} 冊取得（累計: {len(all_books)} 冊）")

        current_url = get_next_page_url(html, current_url)
        page_num += 1

        if current_url:
            wait = random.uniform(1, 3)
            logger.info(f"  {wait:.1f} 秒待機...")
            time.sleep(wait)

    save_to_markdown(all_books, output_file)
    logger.info(f"完了: 合計 {len(all_books)} 冊を {output_file} に保存しました")


if __name__ == "__main__":
    main()
