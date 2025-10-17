import os
import json
import csv
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from collections import Counter
import sys

from modules.io_loader import read_file
from modules.analyzer import analyze_text, detailed_analyze_text
from modules.utils import params_from_nim


def list_text_files(folder='data'):
    for name in sorted(os.listdir(folder)):
        if name.lower().endswith('.txt'):
            yield os.path.join(folder, name)


def main(folder='data', max_workers_io=16, max_workers_cpu=None, detailed=False, top_k=20, write_files=False, limit_data=None):
    files = list(list_text_files(folder))
    # apply optional NIM limit
    data_limit = globals().get('_NIM_DATA_COUNT', None)
    if data_limit is not None:
        files = files[:data_limit]
    # apply explicit CLI limit if provided
    if limit_data is not None:
        files = files[:limit_data]
    print(f"Found {len(files)} .txt files in '{folder}'")

    # --- Sequential baseline: run single-threaded single-process pass for timing
    print('\nRunning sequential baseline (single-process, single-thread) for timing...')
    seq_start = time.perf_counter()
    seq_results = {}
    if detailed:
        analyzer_seq = detailed_analyze_text
    else:
        analyzer_seq = analyze_text

    for path in files:
        try:
            text = read_file(path)
            seq_results[path] = analyzer_seq(text)
        except Exception as e:
            seq_results[path] = {'error': str(e)}
    seq_end = time.perf_counter()
    seq_time = seq_end - seq_start
    print(f'Sequential baseline time: {seq_time:.3f}s')

    results = {}
    word_counter = Counter()
    len_hist = Counter()

    # Streaming pipeline: read -> immediately submit analysis to process pool
    par_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers_io) as tpool, ProcessPoolExecutor(max_workers=max_workers_cpu) as ppool:
        read_futures = {tpool.submit(read_file, path): path for path in files}
        analyze_futures = {}

        for read_fut in as_completed(read_futures):
            path = read_futures[read_fut]
            try:
                text = read_fut.result()
            except Exception as e:
                print(f"Failed to read {path}: {e}")
                continue

            # choose analyzer
            if detailed:
                fut = ppool.submit(detailed_analyze_text, text, top_k)
            else:
                fut = ppool.submit(analyze_text, text)

            analyze_futures[fut] = path

        # collect analysis results
        for fut in as_completed(analyze_futures):
            path = analyze_futures[fut]
            try:
                r = fut.result()
            except Exception as e:
                print(f"Analysis failed for {path}: {e}")
                continue

            results[path] = r
            if detailed:
                # aggregate top words and len hist
                for w, c in r.get('top_words', []):
                    word_counter[w] += c
                len_hist.update(r.get('len_histogram', {}))
            else:
                # no per-token info, skip
                pass

    par_end = time.perf_counter()
    par_time = par_end - par_start

    # Aggregate summary
    total_files = len(results)
    agg = {'files': total_files, 'words': 0, 'vowels': 0,
           'digits': 0, 'symbols': 0, 'avg_len': 0}
    avg_lens = []
    for r in results.values():
        agg['words'] += r.get('words', 0)
        agg['vowels'] += r.get('vowels', 0)
        agg['digits'] += r.get('digits', 0)
        agg['symbols'] += r.get('symbols', 0)
        avg_lens.append(r.get('avg_len', 0))

    agg['avg_len'] = sum(avg_lens) / len(avg_lens) if avg_lens else 0

    print('\nAggregate statistics:')
    print(json.dumps(agg, indent=2))

    # Performance metrics
    cpu_workers = max_workers_cpu if max_workers_cpu is not None else os.cpu_count()
    par_time = max(par_time, 1e-6)
    seq_time = max(seq_time, 1e-6)
    throughput = total_files / par_time
    speedup = seq_time / par_time
    efficiency = speedup / float(cpu_workers) if cpu_workers else 0.0

    print('\nPerformance:')
    print(f'  Threads (I/O workers): {max_workers_io}')
    print(f'  Processes (CPU workers): {cpu_workers}')
    print(f'  Sequential time: {seq_time:.3f}s')
    print(f'  Parallel time:   {par_time:.3f}s')
    print(f'  Throughput: {throughput:.2f} files/s')
    print(f'  Speedup: {speedup:.2f}x')
    print(f'  Efficiency: {efficiency:.3f}')

    # add overall top-K if detailed
    overall_top = word_counter.most_common(top_k) if detailed else []

    # Example output: top-1 word (if available) and brief metrics
    print('\nExample analysis result:')
    print(f"  Total files processed: {total_files}")
    print(f"  Total words: {agg['words']}")
    if overall_top:
        top_word, top_count = overall_top[0]
        print(f"  Top word: '{top_word}' (count: {top_count})")
    else:
        print('  Top word: n/a (detailed analysis not enabled)')

    # Optionally write results to files. By default we only print to terminal.
    if write_files:
        with open('results.json', 'w', encoding='utf-8') as f:
            json.dump({'aggregate': agg, 'per_file': results, 'top_words': overall_top,
                      'len_histogram': dict(len_hist)}, f, ensure_ascii=False, indent=2)

        # CSV (per-file basic metrics)
        with open('results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['file', 'words', 'vowels',
                            'digits', 'symbols', 'avg_len'])
            for path, r in results.items():
                writer.writerow([os.path.basename(path), r.get('words', 0), r.get(
                    'vowels', 0), r.get('digits', 0), r.get('symbols', 0), r.get('avg_len', 0)])

        print('\nWrote results.json and results.csv')


def build_parser():
    p = argparse.ArgumentParser(
        description='Parallel File Analyzer: threads for I/O, processes for CPU-bound analysis')
    p.add_argument('--folder', default='data',
                   help='Folder containing .txt files')
    p.add_argument('--io-workers', type=int, default=16,
                   help='Number of threads for I/O')
    p.add_argument('--cpu-workers', type=int, default=None,
                   help='Number of worker processes for analysis (default: cpu_count)')
    p.add_argument('--detailed', action='store_true',
                   help='Enable detailed analysis (top-k words, length histogram)')
    p.add_argument('--top-k', type=int, default=20,
                   help='Top K words to aggregate when detailed analysis is enabled')
    p.add_argument('--nim', type=str, default=None,
                   help='NIM to derive parameters (threads/processes/data_count)')
    p.add_argument('--mpi', action='store_true',
                   help='Run the MPI-based distributed analyzer (requires mpi4py and mpiexec). When set, control is transferred to analyze_mpi.py')
    p.add_argument('--limit-data', type=int, default=None,
                   help='Process only first N files')
    p.add_argument('--write-files', action='store_true',
                   help='Write results.json and results.csv (default: print only)')
    return p


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    # If MPI mode requested, try to hand off to the MPI runner. This allows
    # users to run either `mpiexec -n <ranks> python analyze_files.py --mpi` or
    # `mpiexec -n <ranks> python analyze_mpi.py` directly.
    if args.mpi:
        try:
            # import the MPI runner and call its main()
            import backend.analyze_mpi as analyze_mpi
            analyze_mpi.main()
            sys.exit(0)
        except Exception as e:
            # Provide helpful instructions if mpi4py is not available or running
            print('Failed to start MPI mode:')
            print(f'  {e}')
            print('\nTo run MPI mode, make sure you have:')
            print('  1) mpi4py installed in the Python environment (pip install mpi4py)')
            print("  2) an MPI runtime available (mpiexec/mpirun). Example:")
            print('\n    mpiexec -n 4 python .\\analyze_mpi.py --write-files\n')
            print('Or run the same via analyze_files.py:')
            print('    mpiexec -n 4 python .\\analyze_files.py --mpi --write-files')
            sys.exit(1)
    # If NIM provided, derive parameters and trim file list accordingly
    if args.nim:
        try:
            threads, processes, data_count = params_from_nim(args.nim)
            print(
                f"Derived from NIM {args.nim}: threads={threads}, processes={processes}, data_count={data_count}")
            args.io_workers = threads
            args.cpu_workers = processes
            # Trim files inside main by passing a modified folder? We'll instead pass data_count via a small global.
            # Simpler: set an env var-like global here that main will check. We'll attach to module attribute.
            global _NIM_DATA_COUNT
            _NIM_DATA_COUNT = data_count
        except Exception as e:
            print(f"Failed to derive params from NIM: {e}")

    main(folder=args.folder, max_workers_io=args.io_workers,
         max_workers_cpu=args.cpu_workers, detailed=args.detailed, top_k=args.top_k, write_files=args.write_files, limit_data=args.limit_data)
