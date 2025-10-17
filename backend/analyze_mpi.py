from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
import os
import argparse
import time
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from collections import Counter
from modules.io_loader import read_file
from modules.analyzer import analyze_text, detailed_analyze_text
from modules.utils import params_from_nim


def list_text_files(folder='data'):
    return sorted([os.path.join(folder, n) for n in os.listdir(folder) if n.lower().endswith('.txt')])


def local_analyze(files, io_workers=2, cpu_workers=2, detailed=False, top_k=20):
    """Hybrid local analysis using threads + processes"""
    results = {}
    word_counter = Counter()

    with ThreadPoolExecutor(max_workers=io_workers) as tpool, ProcessPoolExecutor(max_workers=cpu_workers) as ppool:
        read_futures = {tpool.submit(read_file, f): f for f in files}
        analyze_futures = {}

        for rf in as_completed(read_futures):
            f = read_futures[rf]
            try:
                text = rf.result()
            except Exception as e:
                results[os.path.basename(f)] = {"error": str(e)}
                continue

            if detailed:
                fut = ppool.submit(detailed_analyze_text, text, top_k)
            else:
                fut = ppool.submit(analyze_text, text)
            analyze_futures[fut] = f

        for af in as_completed(analyze_futures):
            f = analyze_futures[af]
            try:
                r = af.result()
                results[os.path.basename(f)] = r
                if detailed:
                    for w, c in r.get("top_words", []):
                        word_counter[w] += c
            except Exception as e:
                results[os.path.basename(f)] = {"error": str(e)}

    return results, word_counter


def main():
    parser = argparse.ArgumentParser(
        description="Hybrid MPI + Threads + Processes Analyzer")
    parser.add_argument('--folder', default='data',
                        help='Folder containing .txt files')
    parser.add_argument('--io-workers', type=int, default=2,
                        help='Number of I/O threads per rank')
    parser.add_argument('--cpu-workers', type=int, default=2,
                        help='Number of CPU process workers per rank')
    parser.add_argument('--limit-data', type=int, default=None,
                        help='Limit number of files to process')
    parser.add_argument('--nim', type=str, default=None,
                        help='NIM to derive parameters automatically')
    parser.add_argument('--detailed', action='store_true',
                        help='Enable detailed analysis (top words)')
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if args.nim:
        try:
            threads, processes, data_count = params_from_nim(args.nim)
            if args.io_workers is None:
                args.io_workers = threads
            if args.cpu_workers is None:
                args.cpu_workers = processes
            if args.limit_data is None:
                args.limit_data = data_count
            if rank == 0:
                print(
                    f"Derived from NIM {args.nim}: io={threads}, cpu={processes}, files={data_count}")
        except Exception as e:
            if rank == 0:
                print(f"Failed to derive NIM parameters: {e}")

    if rank == 0:
        files = list_text_files(args.folder)
        if args.limit_data:
            files = files[:args.limit_data]
        chunks = [files[i::size] for i in range(size)]
    else:
        chunks = None

    my_files = comm.scatter(chunks, root=0)

    start = time.perf_counter()
    local_results, local_words = local_analyze(
        my_files,
        io_workers=args.io_workers,
        cpu_workers=args.cpu_workers,
        detailed=args.detailed
    )
    elapsed = time.perf_counter() - start

    all_results = comm.gather(local_results, root=0)
    all_words = comm.gather(local_words, root=0)
    total_time = comm.reduce(elapsed, op=MPI.MAX, root=0)

    if rank == 0:
        merged = {}
        global_words = Counter()
        for part, words in zip(all_results, all_words):
            merged.update(part)
            global_words.update(words)

        total_files = len(merged)
        overall_top = global_words.most_common(1)
        top_str = f"'{overall_top[0][0]}' (count: {overall_top[0][1]})" if overall_top else "n/a"

        # Run sequential baseline for speedup calculation
        print("\nRunning sequential baseline for speedup calculation...")
        if args.limit_data:
            all_files = list_text_files(args.folder)[:args.limit_data]
        else:
            all_files = list_text_files(args.folder)
        
        seq_start = time.perf_counter()
        if args.detailed:
            analyzer = detailed_analyze_text
        else:
            analyzer = analyze_text
        
        for f in all_files:
            try:
                text = read_file(f)
                analyzer(text)
            except:
                pass
        seq_time = time.perf_counter() - seq_start

        throughput = total_files / total_time if total_time > 0 else 0
        speedup = seq_time / total_time if total_time > 0 else 0
        total_workers = size * args.cpu_workers
        efficiency = speedup / total_workers if total_workers > 0 else 0

        print("\n=== MPI Hybrid Analysis Results ===")
        print(f"Ranks: {size}")
        print(f"I/O Threads per Rank: {args.io_workers}")
        print(f"CPU Processes per Rank: {args.cpu_workers}")
        print(f"Total files processed: {total_files}")
        print(f"Top word: {top_str}")
        print(f"Sequential time: {seq_time:.3f}s")
        print(f"Parallel wall time: {total_time:.3f}s")
        print(f"Speedup: {speedup:.2f}x")
        print(f"Throughput: {throughput:.2f} files/s")
        print(f"Efficiency: {efficiency:.3f}")
        print("===============================")


if __name__ == '__main__':
    main()
