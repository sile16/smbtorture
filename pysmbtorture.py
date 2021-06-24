
import time
import asyncio
import os
from random import randint


# Send a command to smbclient, with an optional wait
async def cmd(p, c, sleep=0):
    # if there is a return code it means the processes exited and something went wrong
    if p.returncode:
        out = await p.stdout.read()
        out = out.decode('utf-8')
        print(out)
    p.stdin.write(c.encode('utf-8'))
    await asyncio.sleep(sleep)
    


async def test1(args, number, counter, semaphore):

    # the command is evaluated twice,  so we have to escape our back slashes twice..
    smb_cmd = f"smbclient \\\\\\\\{args.server}\\\\{args.share} -k -m SMB2"

    # the semaphore prevents us from spawning too many processes too quickly which causes os issues.
    await semaphore.acquire()
    p = await asyncio.create_subprocess_shell(smb_cmd, 
                                stdin=asyncio.subprocess.PIPE,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE)
    semaphore.release()
    
    folder = f"{args.folder_prefix}_{number}"
    
    await asyncio.sleep(1)
    await cmd(p, f'mkdir {folder}\n')

    # counter is an object passed by reference
    counter[0] += 1
    if counter[0] == args.t:
        print(f"Connection Count: {counter[0]}")
        print(f"Starting {args.duration}s test.")
    elif counter[0] % 100 == 0:
        print(f"Connection Count: {counter[0]}")
    
    # We are going to wait here until all threads get to this point.
    while counter[0] < args.t:
        await asyncio.sleep(0.5)

    t_end = time.time() + args.duration

    # Random sleep, so threads are working on different things at different times
    await asyncio.sleep(randint(0, 10))

    while time.time() < t_end:
        
        await cmd(p, f'put random.bin {folder}\\r.bin\n', 0.5)
        
        await cmd(p, f'get {folder}\\r.bin  r-{number}.bin\n', 0.5)
        await cmd(p, f'l {folder}\\r.bin \n', 0.5)
        await cmd(p, f'mkdir {folder}\\1 \n', 0.5)
        await cmd(p, f'mkdir {folder}\\2 \n', 0.5)
        await cmd(p, f'rmdir {folder}\\1 \n', 0.5)
        await cmd(p, f'rmdir {folder}\\2 \n', 0.5)
    
    if number == 0:
        # so only 1 test instance prints
        print("Test finished ")
    
    if args.cleanup:
        if number == 0:
            # so only 1 test instance prints
            print("Cleaning up files")
        
        await cmd(p, f'del {folder}\\r.bin \n')
        await cmd(p, f'rmdir {folder}\n')
        os.remove(f'r-{number}.bin')
    
    await cmd(p, f'quit\n')
     


async def main(args):

    # counter is an object so it can be passed by reference.
    # this is asyncio so no races conditions to worry about.
    counter = [0]
    

    # only start so many processes at a time because of OS issues
    semaphore = asyncio.Semaphore(80)
    
    tasks = []
    for i in range(args.t):
        tasks.append(test1(args, i, counter, semaphore))

    results = await asyncio.gather(*tasks)
    
    # Todo return some stats and aggregate them.
    # print(results)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=int, default=60,
                        help="duration in seconds")
    parser.add_argument('--server', type=str, required=True,
                        help="server")
    parser.add_argument('--share', type=str, required=True,
                        help="share")
    parser.add_argument('--cleanup', action="store_true",
                        help="clean up files and folders after the run")          
    parser.add_argument('-t', type=int, help="number of threads", default=5)
    parser.add_argument('--folder-prefix', type=str, default="pysmbtorture",
                        help="Folder prefix name to be used on shared folder for test.")

    # start our async loop and run the main function.
    # This is Python 3.6 so can't use asyncio.run
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(parser.parse_args()))
