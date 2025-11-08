import csv
import json
import os
import re
import tempfile
import requests
import sys
from playwright.sync_api import sync_playwright

def _sanitize_filename(name: str) -> str:
    # Remove or replace characters not safe for filenames
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name


def save_results_to_json(results, out_path):
    """Write results to JSON using atomic write (write to tmp then replace).

    Args:
        results: Python object serializable to JSON (usually list/dict).
        out_path: destination file path.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(out_path), prefix=".tmp-", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            json.dump(results, tmpf, ensure_ascii=False, indent=2)
        os.replace(tmp_path, out_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def run(urls):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Read Properties in Coinmaster Website
        for url in urls:
            page.goto(url)
            page.wait_for_selector("h1")
            
            #scrape property name
            prop_name = page.locator("h1.ant-typography.acss-1qzactf.css-d3drge").text_content()

            #scrape token price
            price = page.locator("span.ant-typography.acss-pq30w2.css-d3drge").text_content()

            #scrape info: APR, Matures In, Total Tokens
            span_loc = page.locator("span.ant-typography.undefined.acss-1vc8mhv.css-d3drge")
            div_loc = page.locator("div.undefined.acss-pq30w2")
            div_count = div_loc.count()
            details = {}
            for i in range(div_count):
                span = span_loc.nth(i)
                div = div_loc.nth(i)
                span_text = span.text_content()
                div_text = div.text_content()
                details[span_text] = div_text

            # scrape property description
            proj_desc = page.locator('div.wmde-markdown.wmde-markdown-color')
            content = proj_desc.locator('p')
            paragraphs = [content.nth(j).text_content() for j in range(content.count())]

            # scrape PDF link of property
            pdf_link_locator = page.locator('a.acss-4h88t2')
            href = pdf_link_locator.get_attribute('href')
            absolute_pdf_url = f"https://coinlander.com{href}" if href else None

            pdf_filename = None
            if absolute_pdf_url:
                # download PDF
                try:
                    response = requests.get(absolute_pdf_url)
                    response.raise_for_status()
                    safe_name = _sanitize_filename(prop_name)
                    pdf_filename = f"{safe_name}.pdf"
                    with open(pdf_filename, "wb") as f:
                        f.write(response.content)
                except Exception as e:
                    # log an error in the result but don't crash
                    pdf_filename = None

            item = {
                "url": url,
                "property_name": prop_name,
                "price": price,
                "details": details,
                "description": paragraphs,
                "pdf_url": absolute_pdf_url,
                "pdf_file": pdf_filename,
            }
            results.append(item)

        browser.close()
    return results

def __read_urls_from_csv(file_path):
    urls = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            urls.append(row["URL"])
    return urls

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python coinlander_scraper.py <csv_file>")
        sys.exit(1)
    csv_file = sys.argv[1]
    urls = __read_urls_from_csv(csv_file)
    results = run(urls)
    json_file = "coinlander_properties.json"
    save_results_to_json(results, json_file)
    print(f"Saved {len(results)} items to {json_file}")