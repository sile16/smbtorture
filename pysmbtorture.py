
import time
from multiprocessing.pool import ThreadPool
import subprocess


def test1(args, number):

    start = time.time()

    cmd = f"smbclient \\\\{args.server}\\{args.share} -k -m SMB2"
    
    p = subprocess.Popen(cmd.split(" "), stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, 
                                         universal_newlines=True)
    #p = subprocess.Popen(cmd.split(" "), stdin=subprocess.PIPE,
    #                                     universal_newlines=True)


    p.stdin.write(f'mkdir python_t3_{number}\n')
    p.stdin.flush()

    for x in range(20):
        p.stdin.write(f'l python_t3_{number}\\r.bin \n')
        p.stdin.flush()
        time.sleep(1)

        p.stdin.write(f'put random.bin python_t3_{number}\\r.bin\n')
        p.stdin.flush()
        time.sleep(1)

        p.stdin.write(f'get python_t3_{number}\\r.bin  r-{number}.bin\n')
        p.stdin.flush()
        time.sleep(1)

        p.stdin.write(f'l python_t3_{number}\\r.bin \n')
        p.stdin.flush()
        time.sleep(1)

        p.stdin.write(f'mkdir python_t3_{number}\\1 \n')
        p.stdin.flush()
        time.sleep(1)

        p.stdin.write(f'mkdir python_t3_{number}\\2 \n')
        p.stdin.flush()
        time.sleep(1)

        p.stdin.write(f'rmdir python_t3_{number}\\1 \n')
        p.stdin.flush()
        time.sleep(1)

        p.stdin.write(f'rmdir python_t3_{number}\\2 \n')
        p.stdin.flush()
        time.sleep(1)
    
    if args.cleanup:
        p.stdin.write(f'del python_t3_{number}\\r.bin \n')
        p.stdin.flush()

        p.stdin.write(f'rmdir python_t3_{number}\n')
        p.stdin.flush()

    
    p.stdin.write(f'quit\n')
    p.stdin.flush()


def main(args):

    # Create amultiprocessing pool
    pool = ThreadPool(processes=args.t)
    futures = []

    for i in range(args.t):
        futures.append(pool.apply_async(test1, args=(args, i, )))
        time.sleep(0.001)

    pool.close()
    pool.join()

    for f in futures:
        result = f.get()
        #print(result)
    


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
    parser.add_argument('--delay', type=int, default=10,
                        help="clean up files and folders after the run")            
    parser.add_argument('-t', type=int, help="number of threads", default=1000)
    main(parser.parse_args())
