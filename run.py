from main import run_server
import multiprocessing

def main():
    cpu_count = multiprocessing.cpu_count()
    ports = range(8080, 8080 + cpu_count)
    processes = []
    for port in ports:
        p = multiprocessing.Process(target=run_server, args=(port,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
