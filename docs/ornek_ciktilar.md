# Örnek Program Çıktıları

Bu dosyadaki çıktılar, program güncellendikten sonra yeniden üretilmiştir.

## Örnek 1: Ödevde Verilen Girdi

Komut:

```powershell
python binary_multiplier_tm.py 11 10 --trace-limit 35
```

Çıktı özeti:

```text
Girdi bandi: 11*10=
Operand ayrimi: 11 * 10

Adim adim simulasyon:
Adim 0001 | durum=q_start                  oku=1  yaz=1  hareket=S sonraki=q_find_star              | Baslangic durumundan * arama durumuna gecildi.
           bant: 11*10=
                 ^
Adim 0004 | durum=q_find_star              oku=*  yaz=*  hareket=L sonraki=q_return_left            | * bulundu; operand ayrimi baslatildi.
           bant: 11*10=
                  ^
Adim 0018 | durum=q_read_multiplier_bit    oku=0  yaz=x  hareket=S sonraki=q_skip_zero              | Bit 0 okundu; 0 basamak kaydirma icin toplama yok.
           bant: 11*1x=0
                     ^
Adim 0020 | durum=q_read_multiplier_bit    oku=1  yaz=y  hareket=S sonraki=q_copy_multiplicand      | Bit 1 okundu; 1 basamak kaydirilmis parcali carpim eklenecek.
           bant: 11*yx=0
                    ^
Adim 0025 | durum=q_copy_multiplicand      oku=_  yaz=#  hareket=R sonraki=q_copy_multiplicand      | Multiplicand 11, 1 basamak sola kaydirilarak gecici alana yaziliyor.
           bant: 11*yx=0#_
                         ^
Adim 0029 | durum=q_add_partial            oku=_  yaz=_  hareket=S sonraki=q_add_partial            | Toplama kolonu: 0 + 0 + elde 0 -> bit 0, yeni elde 0
           bant: 11*yx=0#110_
                            ^
... 21 adim daha var.

Sonuc:
Binary : 110
Decimal: 6
Final bant: 11*10=110
```

## Örnek 2: `101 x 11`

Komut:

```powershell
python binary_multiplier_tm.py 101 11 --no-trace
```

Çıktı:

```text
Girdi bandi: 101*11=
Operand ayrimi: 101 * 11

Sonuc:
Binary : 1111
Decimal: 15
Final bant: 101*11=1111
```

## Örnek 3: `1001 x 101`

Komut:

```powershell
python binary_multiplier_tm.py 1001 101 --no-trace
```

Çıktı:

```text
Girdi bandi: 1001*101=
Operand ayrimi: 1001 * 101

Sonuc:
Binary : 101101
Decimal: 45
Final bant: 1001*101=101101
```

## Test Çıktısı

Komut:

```powershell
python -m unittest -v
```

Çıktı:

```text
test_assignment_example (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_assignment_example) ... ok
test_binary_addition_helper (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_binary_addition_helper) ... ok
test_invalid_input_is_rejected (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_invalid_input_is_rejected) ... ok
test_large_sample (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_large_sample) ... ok
test_multi_bit_operands (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_multi_bit_operands) ... ok
test_one_times_number (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_one_times_number) ... ok
test_operand_delimiters_are_preserved (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_operand_delimiters_are_preserved) ... ok
test_zero_times_nonzero (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_zero_times_nonzero) ... ok
test_zero_times_zero (tests.test_binary_multiplier_tm.BinaryMultiplicationTMTests.test_zero_times_zero) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.003s

OK
```
