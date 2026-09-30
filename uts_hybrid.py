"""Nama: Siti Qori'ah Muhafidloh | NIM : 247006111141"""
import os, re, sys, time, random, argparse, statistics
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

NAMA = "Siti Qori'ah Muhafidloh"
NIM = "247006111141"

SEED = int(NIM)                             
N_THREAD = int(NIM[-2:]) % 4 + 2             # 41 mod 4 + 2 = 3
N_PROSES = int(NIM[5:7]) % 3 + 2             # 61 mod 3 + 2 = 3  (dua digit tengah = digit ke-6 dan ke-7)
N_DATA = int(NIM[-3:]) * 10                  # 141 x 10 = 1410

FOLDER = "dataset_uts"
BATCH = 10                                 

RE_VOKAL = re.compile(r"[aeiouAEIOU]")
RE_KATA = re.compile(r"[A-Za-z]+")
RE_ANGKA = re.compile(r"\d")
RE_SIMBOL = re.compile(r"[^\w\s]")

def baca_batch(paths):
    """Tugas I/O-bound: membaca sekelompok file."""
    hasil = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            hasil.append(f.read())
    return hasil

def analisis_teks(teks):
    """Tugas CPU-bound: statistik satu teks."""
    kata = [k.lower() for k in RE_KATA.findall(teks)]
    return {
        "vokal": len(RE_VOKAL.findall(teks)),
        "kata": len(kata),
        "angka": len(RE_ANGKA.findall(teks)),
        "simbol": len(RE_SIMBOL.findall(teks)),
        "frek": Counter(kata),
    }

def analisis_batch(teks_list):
    total = {"vokal": 0, "kata": 0, "angka": 0, "simbol": 0, "file": 0, "frek": Counter()}
    for t in teks_list:
        r = analisis_teks(t)
        for k in ("vokal", "kata", "angka", "simbol"):
            total[k] += r[k]
        total["frek"].update(r["frek"])
        total["file"] += 1
    return total

def _dummy(x):
    return x

def gabung(daftar):
    total = {"vokal": 0, "kata": 0, "angka": 0, "simbol": 0, "file": 0, "frek": Counter()}
    for d in daftar:
        for k in ("vokal", "kata", "angka", "simbol", "file"):
            total[k] += d[k]
        total["frek"].update(d["frek"])
    return total

def daftar_file(n_data):
    """Ambil n_data file secara acak-tetap (random.seed(NIM)) supaya semua konfigurasi memakai data yang sama."""
    semua = sorted(os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.endswith(".txt"))
    if n_data > len(semua):
        raise SystemExit(f"Data diminta {n_data}, hanya ada {len(semua)} file. Jalankan make_dataset.py dulu.")
    rng = random.Random(SEED)
    rng.shuffle(semua)
    return semua[:n_data]

def pecah(paths, ukuran=BATCH):
    return [paths[i:i + ukuran] for i in range(0, len(paths), ukuran)]

def jalankan_sekuensial(paths, profil=False):
    """Baseline T1: satu alur, tanpa thread dan tanpa process."""
    t_baca = t_hitung = 0.0
    hasil = []
    for grup in pecah(paths):
        a = time.perf_counter(); teks = baca_batch(grup); b = time.perf_counter()
        hasil.append(analisis_batch(teks)); c = time.perf_counter()
        t_baca += b - a; t_hitung += c - b
    total = gabung(hasil)
    return (total, t_baca, t_hitung) if profil else total

def jalankan_hybrid(paths, n_thread, n_proses):
    """Thread membaca file -> begitu satu batch selesai dibaca, langsung dikirim ke ProcessPool."""
    with ThreadPoolExecutor(max_workers=n_thread) as tp, ProcessPoolExecutor(max_workers=n_proses) as pp:
        list(pp.map(_dummy, range(n_proses * 2)))          # warm-up pool (start proses tidak ikut diukur)
        mulai = time.perf_counter()
        f_baca = [tp.submit(baca_batch, g) for g in pecah(paths)]
        f_hitung = []
        for fb in as_completed(f_baca):
            f_hitung.append(pp.submit(analisis_batch, fb.result()))
        hasil = [fh.result() for fh in f_hitung]
        selesai = time.perf_counter()
    return gabung(hasil), selesai - mulai

def median_waktu(fungsi, ulang=3):
    waktu, hasil = [], None
    for _ in range(ulang):
        a = time.perf_counter()
        hasil = fungsi()
        waktu.append(time.perf_counter() - a)
    return statistics.median(waktu), hasil

def ukur_konfigurasi(n_thread, n_proses, n_data, t1=None, ulang=3):
    """Kembalikan dict hasil: waktu hybrid (median), speedup, efisiensi, throughput."""
    paths = daftar_file(n_data)
    if t1 is None:
        t1, ref = median_waktu(lambda: jalankan_sekuensial(paths), ulang)
    else:
        ref = jalankan_sekuensial(paths)
    ws, hasil = [], None
    for _ in range(ulang):
        hasil, w = jalankan_hybrid(paths, n_thread, n_proses)
        ws.append(w)
    th = statistics.median(ws)
    sama = all(hasil[k] == ref[k] for k in ("vokal", "kata", "angka", "simbol", "file")) and hasil["frek"] == ref["frek"]
    speedup = t1 / th
    return {"thread": n_thread, "proses": n_proses, "data": n_data, "t1": t1, "waktu": th,
            "speedup": speedup, "efisiensi": speedup / n_proses * 100,
            "throughput": n_data / th, "valid": sama, "hasil": hasil}

def cetak_hasil(r):
    h = r["hasil"]
    print("=" * 62)
    print(f"Hybrid Project by: {NAMA} ({NIM})")
    print(f"Threads: {r['thread']} | Processes: {r['proses']} | Data: {r['data']}")
    print(f"Total Time: {r['waktu']:.2f} s | Speedup: {r['speedup']:.2f} | Efficiency: {r['efisiensi']:.1f}%")
    print(f"Throughput: {r['throughput']:.1f} file/s | Waktu sekuensial (T1): {r['t1']:.2f} s")
    print("-" * 62)
    print(f"Jumlah file : {h['file']}")
    print(f"Total kata  : {h['kata']:,}")
    print(f"Total vokal : {h['vokal']:,}")
    print(f"Total angka : {h['angka']:,}")
    print(f"Total simbol: {h['simbol']:,}")
    print("5 kata teratas:", ", ".join(f"{k}({v:,})" for k, v in h["frek"].most_common(5)))
    print(f"Verifikasi hasil hybrid == sekuensial: {'SAMA' if r['valid'] else 'BEDA (ada bug!)'}")
    print("=" * 62)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=N_THREAD)
    ap.add_argument("--procs", type=int, default=N_PROSES)
    ap.add_argument("--data", type=int, default=N_DATA)
    ap.add_argument("--ulang", type=int, default=3)
    a = ap.parse_args()
    random.seed(SEED)
    cetak_hasil(ukur_konfigurasi(a.threads, a.procs, a.data, ulang=a.ulang))

if __name__ == "__main__":
    main()
