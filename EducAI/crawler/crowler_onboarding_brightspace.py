import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import argparse
from urllib.parse import urlparse, urljoin
from datetime import datetime
import validators

def is_valid_url(url):
    return validators.url(url)

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
    except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError, ValueError) as e:
        log_message(f"Erro ao acessar {url}: {e}")
        return None

def parse_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    return soup

def get_all_links(soup, base_url):
    links = set()
    base_domain = urlparse(base_url).netloc
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == base_domain and is_valid_url(full_url):
            links.add(full_url)
    return links

async def crawl_website(base_url):
    visited = set()
    to_visit = [base_url]

    async with aiohttp.ClientSession() as session:
        while to_visit:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue

            log_message(f'Crawling: {current_url}')
            content = await fetch(session, current_url)
            if content is None:
                continue

            soup = parse_html(content)
            links = get_all_links(soup, base_url)

            to_visit.extend(links - visited)
            visited.add(current_url)

            # Save visited links and content to a file immediately
            text_content = soup.get_text(separator='\n', strip=True)
            save_content_to_file(current_url, text_content, 'output.txt')

    return visited

def interact_with_submenus(base_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(base_url)
    time.sleep(3)  # Wait for the page to load

    # Interact with submenus (example)
    submenus = driver.find_elements_by_css_selector('.submenu-class')
    for submenu in submenus:
        submenu.click()
        time.sleep(1)  # Wait for submenu to load

    page_source = driver.page_source
    driver.quit()
    return page_source

def save_content_to_file(url, content, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"URL: {url}\n")
        file.write(f"Content:\n{content}\n")
        file.write("="*80 + "\n")

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}"
    print(log_entry)
    with open('crawler.log', 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry + '\n')

async def main(base_url):
    if not is_valid_url(base_url):
        print(f"URL inválida: {base_url}")
        return

    all_links = await crawl_website(base_url)

    # Optionally, interact with submenus
    submenu_content = interact_with_submenus(base_url)
    soup = parse_html(submenu_content)

    # Add submenu links to the set of all links
    all_links.update(get_all_links(soup, base_url))

    # Save all links to a file
    async with aiohttp.ClientSession() as session:
        tasks = []
        for link in all_links:
            tasks.append(fetch_and_save_content(session, link))
        await asyncio.gather(*tasks)

    print(f"Total links found: {len(all_links)}")
    print("Links and content saved to output.txt")

async def fetch_and_save_content(session, url):
    content = await fetch(session, url)
    if content:
        soup = parse_html(content)
        text_content = soup.get_text(separator='\n', strip=True)
        save_content_to_file(url, text_content, 'output.txt')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler para coletar links de um site.')
    parser.add_argument('url', help='URL do site para rastrear')
    args = parser.parse_args()

    asyncio.run(main(args.url))
