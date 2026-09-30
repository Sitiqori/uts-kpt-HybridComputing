"""Nama : Siti Qori'ah Muhafidloh | NIM: 247006111141"""
import csv, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import uts_hybrid as U

KONFIG = [
    (1, 1, 1410),   # 1  hybrid minimum
    (3, 3, 1410),   # 2  parameter NIM
    (3, 2, 1410),   # 3  variasi proses
    (3, 4, 1410),   # 4  variasi proses
    (3, 8, 1410),   # 5  variasi proses (= jumlah thread logis)
    (1, 3, 1410),   # 6  variasi thread
    (5, 3, 1410),   # 7  variasi thread
    (3, 3, 141),    # 8  variasi data
    (3, 3, 705),    # 9  variasi data
    (3, 3, 2820),   # 10 variasi data
]

def main():
    t1_cache, baris = {}, []
    # profil I/O vs CPU pada baseline 1410 file
    paths = U.daftar_file(1410)
    _, tb, th = U.jalankan_sekuensial(paths, profil=True)
    profil = {"t_baca": tb, "t_hitung": th, "persen_cpu": th / (tb + th) * 100}
    json.dump(profil, open("profil_io_cpu.json", "w"))
    print(f"Profil sekuensial 1410 file: baca={tb:.2f}s hitung={th:.2f}s (CPU {profil['persen_cpu']:.1f}%)")

    for no, (t, p, d) in enumerate(KONFIG, 1):
        if d not in t1_cache:
            t1_cache[d], _ = U.median_waktu(lambda d=d: U.jalankan_sekuensial(U.daftar_file(d)), 3)
        r = U.ukur_konfigurasi(t, p, d, t1=t1_cache[d])
        r["no"] = no
        baris.append(r)
        print(f"[{no:2d}] thread={t} proses={p} data={d:4d} | T1={r['t1']:.2f}s waktu={r['waktu']:.2f}s "
              f"speedup={r['speedup']:.2f} efisiensi={r['efisiensi']:.1f}% valid={r['valid']}")

    with open("hasil_uts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["no", "thread", "proses", "data", "t1", "waktu", "speedup", "efisiensi", "throughput", "valid"])
        for r in baris:
            w.writerow([r["no"], r["thread"], r["proses"], r["data"], f"{r['t1']:.4f}", f"{r['waktu']:.4f}",
                        f"{r['speedup']:.4f}", f"{r['efisiensi']:.2f}", f"{r['throughput']:.2f}", r["valid"]])

    g = sorted([r for r in baris if r["proses"] == 3 and r["data"] == 1410], key=lambda r: r["thread"])
    plt.figure(figsize=(5.5, 3.6)); plt.plot([r["thread"] for r in g], [r["waktu"] for r in g], "o-")
    plt.xlabel("Jumlah thread"); plt.ylabel("Waktu (s)"); plt.title("Waktu vs Jumlah Thread (proses=3, data=1410)")
    plt.xticks([r["thread"] for r in g]); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig("grafik_waktu_thread.png", dpi=150); plt.close()

    g = sorted([r for r in baris if r["thread"] == 3 and r["data"] == 1410], key=lambda r: r["proses"])
    plt.figure(figsize=(5.5, 3.6)); plt.plot([r["proses"] for r in g], [r["waktu"] for r in g], "o-", color="tab:orange")
    plt.xlabel("Jumlah process"); plt.ylabel("Waktu (s)"); plt.title("Waktu vs Jumlah Process (thread=3, data=1410)")
    plt.xticks([r["proses"] for r in g]); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig("grafik_waktu_proses.png", dpi=150); plt.close()

    plt.figure(figsize=(7, 3.8))
    plt.bar([str(r["no"]) for r in baris], [r["speedup"] for r in baris], color="tab:green")
    for r in baris:
        plt.text(str(r["no"]), r["speedup"] + .03, f"{r['speedup']:.2f}", ha="center", fontsize=8)
    plt.axhline(1, color="gray", ls="--", lw=.8); plt.xlabel("Nomor konfigurasi"); plt.ylabel("Speedup")
    plt.title("Speedup vs Konfigurasi"); plt.tight_layout(); plt.savefig("grafik_speedup.png", dpi=150); plt.close()

    g = sorted([r for r in baris if r["thread"] == 3 and r["proses"] == 3], key=lambda r: r["data"])
    plt.figure(figsize=(5.5, 3.6))
    plt.plot([r["data"] for r in g], [r["waktu"] for r in g], "o-", label="Hybrid")
    plt.plot([r["data"] for r in g], [r["t1"] for r in g], "s--", label="Sekuensial")
    plt.xlabel("Jumlah data (file)"); plt.ylabel("Waktu (s)"); plt.title("Waktu vs Jumlah Data (thread=3, proses=3)")
    plt.legend(); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig("grafik_waktu_data.png", dpi=150); plt.close()
    print("Selesai: hasil_uts.csv, profil_io_cpu.json, grafik_*.png")

if __name__ == "__main__":
    main()
