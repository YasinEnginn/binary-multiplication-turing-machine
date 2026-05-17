# Geçiş Tablosu

Bu tablo, `binary_multiplier_tm.py` dosyasındaki durum temelli Turing Makinesi
modelinin ana geçiş fonksiyonunu özetler. Program her geçişte mevcut durum,
okunan sembol, yazılan sembol, kafa hareketi, sonraki durum ve bant içeriğini
ayrıca günlük olarak üretir.

| Durum | Okunan sembol | Yazılan sembol | Hareket | Sonraki durum | Açıklama |
|---|---|---|---|---|---|
| `q_start` | `0/1` | aynı | `S` | `q_find_star` | Makine başlangıç durumundan `*` arama durumuna geçer. |
| `q_find_star` | `0/1` | aynı | `R` | `q_find_star` | `*` görülene kadar sol operand üzerinde sağa ilerler. |
| `q_find_star` | `*` | `*` | `L` | `q_return_left` | Operand ayracı bulunur; birinci operandın başına dönülür. |
| `q_return_left` | `0/1` | aynı | `L` | `q_return_left` | Sol sınır bulunana kadar geriye gidilir. |
| `q_return_left` | `_` | `_` | `R` | `q_read_multiplicand` | Sol sınırdan sonra birinci operand okunmaya başlanır. |
| `q_read_multiplicand` | `0/1` | aynı | `R` | `q_read_multiplicand` | `*` sembolüne kadar multiplicand bitleri okunur. |
| `q_read_multiplicand` | `*` | `*` | `R` | `q_read_multiplier` | `*` sembolünden sonra ikinci operand alanına geçilir. |
| `q_read_multiplier` | `0/1` | aynı | `R` | `q_read_multiplier` | `=` sembolüne kadar multiplier bitleri okunur. |
| `q_read_multiplier` | `=` | `=` | `R` | `q_init_result` | `=` sembolünden sonraki sonuç alanına geçilir. |
| `q_init_result` | `_` | `0` | `L` | `q_seek_multiplier_bit` | Sonuç alanı başlangıçta `0` olarak yazılır. |
| `q_seek_multiplier_bit` | `0/1/x/y` | aynı | `L/R/S` | `q_read_multiplier_bit` | Multiplier bitleri sağdan sola taranır ve sıradaki bit seçilir. |
| `q_read_multiplier_bit` | `0` | `x` | `S` | `q_skip_zero` | Seçilen multiplier biti `0` ise bit işaretlenir, toplama yapılmaz. |
| `q_skip_zero` | `x` | `x` | `L` | `q_seek_multiplier_bit` | Shift sayacı ilerletilir ve bir sonraki multiplier bitine geçilir. |
| `q_read_multiplier_bit` | `1` | `y` | `S` | `q_copy_multiplicand` | Seçilen multiplier biti `1` ise parçalı çarpım üretimi başlar. |
| `q_copy_multiplicand` | `0/1/_/#` | `0/1/_/#` | `R` | `q_add_partial` | Multiplicand, geçerli shift değeri kadar sola kaydırılarak geçici alana yazılır. |
| `q_add_partial` | `0/1/#/_` | aynı | `L/R/S` | `q_write_result` | Geçici parçalı çarpım mevcut sonuçla binary toplama mantığıyla toplanır. |
| `q_write_result` | `0/1/_` | `0/1/_` | `R` | `q_clear_work` | Güncellenmiş sonuç `=` sembolünden sonraki sonuç alanına yazılır. |
| `q_clear_work` | `#/0/1` | `_` | `R` | `q_seek_multiplier_bit` | Geçici parçalı çarpım alanı temizlenir. |
| `q_seek_multiplier_bit` | `*` | `*` | `R` | `q_restore_multiplier` | İşlenmemiş multiplier biti kalmadığında işaretler geri yüklenir. |
| `q_restore_multiplier` | `x` | `0` | `R` | `q_restore_multiplier` | İşaretlenmiş `0` biti eski haline getirilir. |
| `q_restore_multiplier` | `y` | `1` | `R` | `q_restore_multiplier` | İşaretlenmiş `1` biti eski haline getirilir. |
| `q_restore_multiplier` | `=` | `=` | `S` | `q_accept` | Tüm multiplier bitleri işlendiği için makine kabul durumuna geçer. |

## Alfabeler ve Özel Semboller

| Küme / sembol | Anlam |
|---|---|
| Giriş alfabesi | `{0, 1}` |
| Bant alfabesi | `{0, 1, *, =, #, x, y, _}` |
| `*` | Birinci ve ikinci operandı ayırır. |
| `=` | Sonuç alanının başlangıcını belirtir. |
| `#` | Geçici parçalı çarpım alanının başlangıç işaretidir. |
| `x` | İşlenmiş `0` multiplier bitidir. |
| `y` | İşlenmiş `1` multiplier bitidir. |
| `_` | Boş bant hücresidir. |
