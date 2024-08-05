import asyncio
import aiohttp
import aiofiles
import argparse
import os


async def fetch(session, url, timeout):
    try:
        async with session.get(url, timeout=timeout) as response:
            content = await response.text()
            return url, content
    except asyncio.TimeoutError:
        print(f"Timeout error for URL: {url}")
        return url, None
    except aiohttp.ClientError as e:
        print(f"Error for URL: {url}, {e}")
        return url, None


async def fetch_all(urls, timeout):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, timeout) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


async def save_content(url, content):
    if content is None:
        return
    filename = url.replace("://", "_").replace("/", "_").replace("?", "_").replace("&", "_")
    async with aiofiles.open(f"output/{filename}.txt", "w", encoding='utf-8') as file:
        await file.write(content)


async def process_results(results):
    tasks = [save_content(url, content) for url, content in results]
    await asyncio.gather(*tasks)


async def main(input_file, timeout):
    if not os.path.exists('output'):
        os.makedirs('output')

    async with aiofiles.open(input_file, mode='r') as file:
        urls = [line.strip() for line in await file.readlines()]

    results = await fetch_all(urls, timeout)
    await process_results(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Asynchronous URL Fetcher')
    parser.add_argument('input_file', type=str, help='Input file with URLs')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout for requests in seconds')
    args = parser.parse_args()

    asyncio.run(main(args.input_file, args.timeout))
