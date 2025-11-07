import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time

async def fetch(session, url):
    try:
        async with session.get(url, timeout=12) as resp:
            text = await resp.text()
            return text, str(resp.url)
    except:
        return None, None

async def check_blog(session, blog_id):
    url = f"https://kovaze.com/blog/{blog_id}"
    html, final_url = await fetch(session, url)
    if not html:
        return None
    if 'kovaze.com/blogs' in final_url or 'LATEST BLOGS' in html.upper():
        return None

    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href='/events/mushrooms'):
        if a.get_text(strip=True) == '🍄':
            if a.find_parent(string=lambda t: t and 'Games' in t):
                continue
            return url
    return None

async def hunt():
    print("🍄 RUNNING ON PHONE - UPDATING links.txt")
    seen = set()
    all_links = []

    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Scanning...")
        start = time.time()
        new_found = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(1, 25001):
                tasks.append(check_blog(session, i))
                if len(tasks) >= 600:
                    results = await asyncio.gather(*tasks)
                    for url in results:
                        if url and url not in seen:
                            seen.add(url)
                            new_found.append(url)
                    tasks = []
            if tasks:
                results = await asyncio.gather(*tasks)
                for url in results:
                    if url and url not in seen:
                        seen.add(url)
                        new_found.append(url)

        if new_found:
            all_links = new_found + all_links
            all_links = all_links[:200]
            with open("links.txt", "w") as f:
                f.write("\n".join(all_links))
            print(f"🍄 {len(new_found)} NEW! Total: {len(all_links)}")
        print(f"Done in {time.time()-start:.1f}s\n")
        await asyncio.sleep(45)

if __name__ == "__main__":
    asyncio.run(hunt())
