
import time
import asyncio
import os
from random import randint


# Send a command to smbclient, with an optional wait
async def cmd(p, c, sleep=0):
    if p.returncode:
        out = await p.stdout.read()
        out = out.decode('utf-8')
        print(out)
    p.stdin.write(c.encode('utf-8'))
    await asyncio.sleep(sleep)
    


async def test1(args, number, counter, semaphore):

    start = time.time()

    smb_cmd = f"smbclient \\\\\\\\{args.server}\\\\{args.share} -k -m SMB2"

    await semaphore.acquire()
    p = await asyncio.create_subprocess_shell(smb_cmd, 
                                stdin=asyncio.subprocess.PIPE,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE)
    semaphore.release()
    
    await asyncio.sleep(1)

    await cmd(p, f'mkdir python_t3_{number}\n')

    counter[0] += 1
    if counter[0] % 100 == 0:
        print(f"Connection Count: {counter[0]}")
    
    # We are going to wait here until all threads get to this point.
    while counter[0] < args.t:
        await asyncio.sleep(0.5)

    # Random sleep, so threads are working on different things at different times
    await asyncio.sleep(randint(0, 10))

    for x in range(20):
        
        await cmd(p, f'put random.bin python_t3_{number}\\r.bin\n', 0.5)
        
        await cmd(p, f'get python_t3_{number}\\r.bin  r-{number}.bin\n', 0.5)
        await cmd(p, f'l python_t3_{number}\\r.bin \n', 0.5)
        await cmd(p, f'mkdir python_t3_{number}\\1 \n', 0.5)
        await cmd(p, f'mkdir python_t3_{number}\\2 \n', 0.5)
        await cmd(p, f'rmdir python_t3_{number}\\1 \n', 0.5)
        await cmd(p, f'rmdir python_t3_{number}\\2 \n', 0.5)
    
    if args.cleanup:
        await cmd(p, f'del python_t3_{number}\\r.bin \n')
        await cmd(p, f'rmdir python_t3_{number}\n')
        os.remove(f'r-{number}.bin')


async def main(args):

    # Create amultiprocessing pool
    counter = [0]
    tasks = []

    # only start so many processes at a time because of OS issues
    semaphore = asyncio.Semaphore(80)

    for i in range(args.t):
        tasks.append(test1(args, i, counter, semaphore))

    results = await asyncio.gather(*tasks)
    print(results)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=int, default=1,
                        help="duration in seconds")
    parser.add_argument('--server', type=str, required=True,
                        help="server")
    parser.add_argument('--share', type=str, required=True,
                        help="share")
    parser.add_argument('--cleanup', action="store_true",
                        help="clean up files and folders after the run")          
    parser.add_argument('-t', type=int, help="number of threads", default=5)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(parser.parse_args()))
