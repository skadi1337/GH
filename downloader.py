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
    #file_path = os.path.join("/data", "downloads", file_name)

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
                
                url = pattern.replace('{x}', str(xi)).replace('{y}', str(yi)).replace('{z}', str(z))
                await queue.put(url)

                
                url2 = pattern.replace('{x}', str(xi)).replace('{y}', str(yi-1)).replace('{z}', str(z))
                await queue.put(url2)

                
                url3 = pattern.replace('{x}', str(xi)).replace('{y}', str(yi-2)).replace('{z}', str(z))
                await queue.put(url3)

                
                url4 = pattern.replace('{x}', str(xi)).replace('{y}', str(yi-3)).replace('{z}', str(z))
                await queue.put(url4)


                url5 = pattern.replace('{x}', str(xi)).replace('{y}', str(yi-4)).replace('{z}', str(z))
                await queue.put(url5)

                url6 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi)).replace('{z}', str(z))
                await queue.put(url6)

                
                url7 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi-1)).replace('{z}', str(z))
                await queue.put(url7)

                
                url8 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi-2)).replace('{z}', str(z))
                await queue.put(url8)

                
                url9 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi-3)).replace('{z}', str(z))
                await queue.put(url9)


                url10 = pattern.replace('{x}', str(xi+1)).replace('{y}', str(yi-4)).replace('{z}', str(z))
                await queue.put(url10)

                url11 = pattern.replace('{x}', str(xi+2)).replace('{y}', str(yi)).replace('{z}', str(z))
                await queue.put(url11)

                
                url12 = pattern.replace('{x}', str(xi+2)).replace('{y}', str(yi-1)).replace('{z}', str(z))
                await queue.put(url12)

                
                url13 = pattern.replace('{x}', str(xi+2)).replace('{y}', str(yi-2)).replace('{z}', str(z))
                await queue.put(url13)

                
                url14 = pattern.replace('{x}', str(xi+2)).replace('{y}', str(yi-3)).replace('{z}', str(z))
                await queue.put(url14)


                url15 = pattern.replace('{x}', str(xi+2)).replace('{y}', str(yi-4)).replace('{z}', str(z))
                await queue.put(url15)

                url16 = pattern.replace('{x}', str(xi+3)).replace('{y}', str(yi)).replace('{z}', str(z))
                await queue.put(url16)

                
                url17 = pattern.replace('{x}', str(xi+3)).replace('{y}', str(yi-1)).replace('{z}', str(z))
                await queue.put(url17)

                
                url18 = pattern.replace('{x}', str(xi+3)).replace('{y}', str(yi-2)).replace('{z}', str(z))
                await queue.put(url18)

                
                url19 = pattern.replace('{x}', str(xi+3)).replace('{y}', str(yi-3)).replace('{z}', str(z))
                await queue.put(url19)


                url20 = pattern.replace('{x}', str(xi+3)).replace('{y}', str(yi-4)).replace('{z}', str(z))
                await queue.put(url20)

                url21 = pattern.replace('{x}', str(xi+4)).replace('{y}', str(yi)).replace('{z}', str(z))
                await queue.put(url21)

                
                url22 = pattern.replace('{x}', str(xi+4)).replace('{y}', str(yi-1)).replace('{z}', str(z))
                await queue.put(url22)

                
                url23 = pattern.replace('{x}', str(xi+4)).replace('{y}', str(yi-2)).replace('{z}', str(z))
                await queue.put(url23)

                
                url24 = pattern.replace('{x}', str(xi+4)).replace('{y}', str(yi-3)).replace('{z}', str(z))
                await queue.put(url24)


                url25 = pattern.replace('{x}', str(xi+4)).replace('{y}', str(yi-4)).replace('{z}', str(z))
                await queue.put(url25)




                
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