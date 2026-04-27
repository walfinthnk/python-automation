import time
import random
import logging
from datetime import date
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://quotes.toscrape.com"
START_PATH = "/js"
USER_AGENT = "Mozilla/5.0 (compatible; PythonScraper/1.0)"


def load_robots_txt(base_url):
    rp = RobotFileParser()
    try:
        response = requests.get(urljoin(base_url, "/robots.txt"), timeout=10)
        rp.parse(response.text.splitlines())
        logger.info("robots.txt を読み込みました")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"接続エラーが発生しました: {e}")
        raise SystemExit(1)
    except Exception as e:
        logger.warning(f"robots.txt の読み込みに失敗しました（アクセス許可として続行）: {e}")
    return rp


def save_to_markdown(quotes, filename):
    today = date.today().strftime("%Y-%m-%d")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Quotes Scraping Results\n\n")
        f.write(f"収集日: {today}  \n")
        f.write(f"合計: {len(quotes)} 件\n\n")
        f.write("---\n\n")
        for i, q in enumerate(quotes, 1):
            text = q["text"].strip("“”\"")
            f.write(f"### {i}. {q['author']}\n\n")
            f.write(f"> {text}\n\n")
    logger.info(f"{filename} に保存しました（{len(quotes)} 件）")


def scrape_quotes():
    today = date.today().strftime("%Y%m%d")
    output_md = f"quotes_{today}.md"
    output_png = f"quotes_{today}.png"

    rp = load_robots_txt(BASE_URL)

    all_quotes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        current_path = START_PATH
        page_num = 1
        screenshot_taken = False

        while current_path:
            current_url = BASE_URL + current_path

            if not rp.can_fetch(USER_AGENT, current_url):
                logger.warning(f"robots.txt によりアクセス禁止: {current_url} — スキップして終了します")
                break

            logger.info(f"ページ {page_num} 取得中: {current_url}")

            try:
                page.goto(current_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_selector(".quote", timeout=15000)
            except PlaywrightTimeoutError as e:
                logger.error(f"タイムアウトエラー: {e}")
                break
            except Exception as e:
                logger.error(f"接続エラーが発生しました: {e}")
                raise SystemExit(1)

            if not screenshot_taken:
                page.screenshot(path=output_png, full_page=True)
                logger.info(f"スクリーンショットを保存しました: {output_png}")
                screenshot_taken = True

            quote_elements = page.query_selector_all(".quote")
            page_quotes = []
            for el in quote_elements:
                text_el = el.query_selector(".text")
                author_el = el.query_selector(".author")
                if text_el and author_el:
                    page_quotes.append({
                        "text": text_el.inner_text().strip(),
                        "author": author_el.inner_text().strip(),
                    })

            all_quotes.extend(page_quotes)
            logger.info(f"  → {len(page_quotes)} 件取得（累計: {len(all_quotes)} 件）")

            next_btn = page.query_selector("li.next a")
            if next_btn:
                current_path = next_btn.get_attribute("href")
                page_num += 1
                wait = random.uniform(1, 3)
                logger.info(f"  {wait:.1f} 秒待機...")
                time.sleep(wait)
            else:
                current_path = None

        browser.close()

    save_to_markdown(all_quotes, output_md)
    logger.info(f"完了: 合計 {len(all_quotes)} 件を {output_md} に保存しました")


if __name__ == "__main__":
    scrape_quotes()
