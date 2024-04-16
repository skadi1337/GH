import sys
import os
import asyncio
import aiohttp
from PIL import Image
from urllib.parse import unquote

xMin = int(sys.argv[1])
yMin = int(sys.argv[2])
xMax = int(sys.argv[3])
yMax = int(sys.argv[4])
z = int(sys.argv[5])
pattern = sys.argv[6]
max_concurrent_tasks = 100  # Maximum number of concurrent tasks

async def download_file(session, url):
    file_url = url
    file_name = os.path.basename(file_url) + ".png"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads", file_name)

    if os.path.exists(file_path):
        return

    try:
        async with session.get(file_url) as response:
            if response.status == 200:
                file_data = await response.read()

                if len(file_data) < 10:
                    image = Image.new("RGB", (512, 512), color="black")
                    image.save(file_path, "PNG") 
                
                else:
                    with open(file_path, "wb") as file:
                        file.write(file_data)

            elif response.status == 404:
                image = Image.new("RGB", (512, 512), color="black")
                image.save(file_path, "PNG")           
    except Exception as e:
        # sys.stderr.write("Error downloading file:", str(e))
        # sys.stderr.flush()
        return


async def worker(session, queue):
    while True:
        url = await queue.get()
        await download_file(session, url)
        print(1)
        sys.stdout.flush()
        queue.task_done()


async def main():
    queue = asyncio.Queue(maxsize=max_concurrent_tasks)

    async with aiohttp.ClientSession() as session:
        # Start the worker tasks
        workers = []
        for _ in range(max_concurrent_tasks):
            worker_task = asyncio.create_task(worker(session, queue))
            workers.append(worker_task)

        # Enqueue the tasks
        for yi in range(int(yMin), int(yMax) - 1, -5):
            for xi in range(int(xMin), int(xMax) + 1, 5):
                # Top-left tile of the 2x2 square
                url = pattern.replace('{x}', str(xi)).replace('{y}', str(yi)).replace('{z}', str(z))
                await queue.put(url)

                # Tile above the top-left tile
                url2 = pattern.replace('{x}', str(xi)).replace('{y}', str(yi-1)).replace('{z}', str(z))
                await queue.put(url2)

                # Diagonal tile of the top-left tile
                url3 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi-1)).replace('{z}', str(z))
                await queue.put(url3)

                # Tile to the right of the top-left tile
                url4 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi)).replace('{z}', str(z))
                await queue.put(url4)

                
        await queue.join()

        # Cancel the worker tasks
        for worker_task in workers:
            worker_task.cancel()

        # Wait until all worker tasks are cancelled
        await asyncio.gather(*workers, return_exceptions=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    exit(0)