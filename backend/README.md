
Nama: Farid Firdaus
NPM: 237006081
Kelas: C

# Parallel File Analyzer 

File penting:
- `main.py` — buat sample files (default 810) di folder `data/`.
- `analyze_files.py` — runner: threads untuk I/O + process pool untuk analisis CPU-bound.
- `analyze_mpi.py` — contoh distribusi pekerjaan dengan MPI (`mpi4py`).
- `modules/` — helper: `analyzer.py`, `io_loader.py`, `utils.py`.

Cara run Thread + ProcessPool:
{
1) `Baseline (NIM-derived):`
python .\analyze_files.py --nim 237006081 --detailed


2) `Eksplisit (equivalent baseline):`
python .\analyze_files.py --io-workers 3 --cpu-workers 2 --limit-data 810 --detailed


3) `Lebih banyak thread:`
python .\analyze_files.py --io-workers 6 --cpu-workers 2 --limit-data 810 --detailed


4) `Lebih banyak process:`
python .\analyze_files.py --io-workers 3 --cpu-workers 4 --limit-data 810 --detailed


5) `Kurangi data (uji skala kecil):`
python .\analyze_files.py --io-workers 3 --cpu-workers 2 --limit-data 100 --detailed


6) `Data sedang + thread tinggi:`
python .\analyze_files.py --io-workers 8 --cpu-workers 4 --limit-data 400 --detailed


7) `Process tinggi (stress CPU):`
python .\analyze_files.py --io-workers 4 --cpu-workers 8 --limit-data 810 --detailed


8) `Minimal resources (lihat overhead):`
python .\analyze_files.py --io-workers 2 --cpu-workers 1 --limit-data 200 --detailed


9) `Contoh kecil (limit 81 files):`
python .\analyze_files.py --io-workers 2 --cpu-workers 1 --limit-data 81 --detailed


10) `Campuran (random test):`
python .\analyze_files.py --io-workers 5 --cpu-workers 3 --limit-data 300 --detailed
}

Cara run ProcessPool + MPI).:
{
1) Baseline (NIM-derived):
mpiexec -n 4 python .\analyze_mpi.py --nim 237006081 --detailed


2) Eksplisit (equivalent baseline):
mpiexec -n 4 python .\analyze_mpi.py --io-workers 3 --cpu-workers 2 --limit-data 810 --detailed


3) Lebih banyak thread per rank:
mpiexec -n 4 python .\analyze_mpi.py --io-workers 6 --cpu-workers 2 --limit-data 810 --detailed

4) Lebih banyak process per rank:
mpiexec -n 4 python .\analyze_mpi.py --io-workers 3 --cpu-workers 4 --limit-data 810 --detailed

5) Kurangi data (uji skala kecil):
mpiexec -n 4 python .\analyze_mpi.py --io-workers 3 --cpu-workers 2 --limit-data 100 --detailed

6) Data sedang + thread tinggi:
mpiexec -n 4 python .\analyze_mpi.py --io-workers 8 --cpu-workers 4 --limit-data 400 --detailed

7) Process tinggi (stress CPU):
mpiexec -n 4 python .\analyze_mpi.py --io-workers 4 --cpu-workers 8 --limit-data 810 --detailed

8) Minimal resources (lihat overhead):
mpiexec -n 4 python .\analyze_mpi.py --io-workers 2 --cpu-workers 1 --limit-data 200 --detailed

9) Contoh kecil (limit 81 files):
mpiexec -n 4 python .\analyze_mpi.py --io-workers 2 --cpu-workers 1 --limit-data 81 --detailed

10) Campuran (random test):
mpiexec -n 4 python .\analyze_mpi.py --io-workers 5 --cpu-workers 3 --limit-data 300 --detailed
}