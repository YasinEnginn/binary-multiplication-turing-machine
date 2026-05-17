# Binary Multiplication Turing Machine

Tek bantlı Turing Makinesi mantığıyla iki binary sayıyı çarpan Python
simülatörü.

**Ders:** Özdevinirler Kuramı

**Öğrenci:** Yasin Engin

**Öğrenci No:** 23060510

**GitHub:** https://github.com/YasinEnginn/binary-multiplication-turing-machine

**YouTube Video:** https://youtu.be/dtmzvePSpGo

## Çalıştırma

```powershell
python binary_multiplier_tm.py 11 10
```

Kısa sonuç için:

```powershell
python binary_multiplier_tm.py 101 11 --no-trace
```

Geçiş tablosu:

```powershell
python binary_multiplier_tm.py --table
```

Testler:

```powershell
python -m unittest -v
```

## Teslim Dosyaları

- [binary_multiplier_tm.py](binary_multiplier_tm.py): Python kaynak kodu
- [RAPOR.md](RAPOR.md): Proje raporu
- [23060510_proje1_rapor.pdf](23060510_proje1_rapor.pdf): Teslim için PDF rapor
- [docs/gecis_tablosu.md](docs/gecis_tablosu.md): Geçiş tablosu
- [docs/ornek_ciktilar.md](docs/ornek_ciktilar.md): Yeniden üretilmiş örnek program ve test çıktıları
- [docs/durum_diyagrami.png](docs/durum_diyagrami.png): Görsel durum geçiş diyagramı
- [docs/durum_diyagrami.svg](docs/durum_diyagrami.svg): SVG durum geçiş diyagramı
- [docs/durum_diyagrami.mmd](docs/durum_diyagrami.mmd): Mermaid durum geçiş diyagramı
- [tests/test_binary_multiplier_tm.py](tests/test_binary_multiplier_tm.py): Test örnekleri
