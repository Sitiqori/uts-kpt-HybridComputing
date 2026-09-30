"""Nama : Siti Qori'ah Muhafidloh | NIM: 247006111141
Jumlah file maksimum = 2 x (tiga digit terakhir NIM x 10) = 2820 file,
supaya konfigurasi data 141 / 705 / 1410 / 2820 semuanya bisa diuji.
"""
import os, random

NIM = "247006111141"
FOLDER = "dataset_uts"
JUMLAH_FILE = int(NIM[-3:]) * 10 * 2      # 2820
KATA_PER_FILE = 6000

KATA = ("paralel terdistribusi komputasi thread proses data server request response waktu "
        "program hasil analisis kecepatan memori jaringan cluster node core kernel simulasi "
        "the of and parallel distributed computing pipeline worker queue message rank "
        "university informatics engineering student project hybrid signal energy vector matrix "
        "algorithm library python compiler network latency bandwidth throughput speedup").split()
ANGKA = ["3.14", "2026", "247", "1410", "99", "7", "100", "0.5", "42", "1e6"]
SIMBOL = ["#", "@", "!", "?", "%", "&", "*", "+", "=", "/", "-", "(", ")"]

def main():
    random.seed(int(NIM))                 
    os.makedirs(FOLDER, exist_ok=True)
    for i in range(JUMLAH_FILE):
        token = []
        for _ in range(KATA_PER_FILE):
            r = random.random()
            if r < 0.80:
                token.append(random.choice(KATA))
            elif r < 0.90:
                token.append(random.choice(ANGKA))
            else:
                token.append(random.choice(SIMBOL))
        teks = " ".join(token)
        with open(os.path.join(FOLDER, f"file_{i:04d}.txt"), "w", encoding="utf-8") as f:
            f.write(teks)
    print(f"Selesai: {JUMLAH_FILE} file dibuat di folder '{FOLDER}'")

if __name__ == "__main__":
    main()
