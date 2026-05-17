"""Single-tape Turing machine style simulator for binary multiplication.

The machine receives two binary operands, builds a tape in the form
``multiplicand*multiplier=``, separates the operands by locating ``*``, and
multiplies them with the shift-and-add method.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable


BLANK = "_"
LEFT = "L"
RIGHT = "R"
STAY = "S"


STATE_DESCRIPTIONS = {
    "q_start": "Baslangic durumudur; kafa bandin en solundadir.",
    "q_find_star": "* ayiracini bulmak icin saga tarar.",
    "q_return_left": "Birinci operandi okumak icin bandin sol basina doner.",
    "q_read_multiplicand": "* sembolune kadar sol operandi okur.",
    "q_read_multiplier": "= sembolune kadar sag operandi okur.",
    "q_init_result": "Sonuc alanini 0 ile baslatir.",
    "q_seek_multiplier_bit": "Multiplier bitlerini sagdan sola arar.",
    "q_read_multiplier_bit": "Siradaki multiplier bitini okur ve isaretler.",
    "q_skip_zero": "Bit 0 ise toplama yapmadan yalnizca kaydirma adimini tamamlar.",
    "q_copy_multiplicand": "Bit 1 ise multiplicand'i uygun sayida sifirla gecici alana kopyalar.",
    "q_add_partial": "Gecici parcali carpimi mevcut sonuca ikili toplama ile ekler.",
    "q_write_result": "Guncellenmis sonucu = sembolunden sonra yazar.",
    "q_clear_work": "Gecici calisma alanini temizler.",
    "q_restore_multiplier": "Isaretlenen multiplier bitlerini eski haline getirir.",
    "q_accept": "Carpma tamamlanmistir.",
    "q_reject": "Gecersiz giris veya beklenmeyen bant sembolu gorulmustur.",
}


TRANSITION_TABLE = [
    ("q_start", "0/1", "ayni", "S", "q_find_star", "Bant uzerinde * aramaya basla."),
    ("q_find_star", "0/1", "ayni", "R", "q_find_star", "* gorulene kadar saga ilerle."),
    ("q_find_star", "*", "*", "L", "q_return_left", "* bulundu; sol operanda don."),
    ("q_return_left", "0/1", "ayni", "L", "q_return_left", "Sol sinira kadar geri git."),
    ("q_return_left", "_", "_", "R", "q_read_multiplicand", "Sol operandin ilk bitine gel."),
    ("q_read_multiplicand", "0/1", "ayni", "R", "q_read_multiplicand", "Multiplicand bitlerini oku."),
    ("q_read_multiplicand", "*", "*", "R", "q_read_multiplier", "Ayirac sonrasi multiplier okunur."),
    ("q_read_multiplier", "0/1", "ayni", "R", "q_read_multiplier", "Multiplier bitlerini oku."),
    ("q_read_multiplier", "=", "=", "R", "q_init_result", "Sonuc alanina gec."),
    ("q_init_result", "_", "0", "L", "q_seek_multiplier_bit", "Sonucu 0 ile baslat."),
    ("q_seek_multiplier_bit", "0/1/x/y/*", "ayni", "L/R/S", "q_read_multiplier_bit", "Siradaki islenmemis bite konumlan."),
    ("q_read_multiplier_bit", "0", "x", "S", "q_skip_zero", "0 biti isaretlenir; toplama yapilmaz."),
    ("q_skip_zero", "x", "x", "L", "q_seek_multiplier_bit", "Toplama yapmadan sonraki multiplier bitine gecilir."),
    ("q_read_multiplier_bit", "1", "y", "S", "q_copy_multiplicand", "1 biti isaretlenir; parcali carpim hazirlanir."),
    ("q_copy_multiplicand", "0/1/_/#", "0/1/_/#", "R", "q_add_partial", "Multiplicand, shift kadar 0 eklenerek gecici alana yazilir."),
    ("q_add_partial", "0/1/#/_", "ayni", "L/R/S", "q_write_result", "Mevcut sonuc ile parcali carpim ikili toplanir."),
    ("q_write_result", "0/1/_", "0/1/_", "R", "q_clear_work", "Yeni sonuc = sonrasina yazilir."),
    ("q_clear_work", "#/0/1", "_", "R", "q_seek_multiplier_bit", "Gecici alan temizlenir; sonraki bite gecilir."),
    ("q_seek_multiplier_bit", "*", "*", "R", "q_restore_multiplier", "Islenmemis multiplier biti kalmadiginda isaretler geri yuklenir."),
    ("q_restore_multiplier", "x", "0", "R", "q_restore_multiplier", "0 olarak isaretlenen bit geri alinir."),
    ("q_restore_multiplier", "y", "1", "R", "q_restore_multiplier", "1 olarak isaretlenen bit geri alinir."),
    ("q_restore_multiplier", "=", "=", "S", "q_accept", "Tum bitler islendi; kabul."),
]


@dataclass(frozen=True)
class TransitionLog:
    """A single visible transition in the simulation trace."""

    step: int
    state: str
    read: str
    write: str
    move: str
    next_state: str
    tape: str
    head_offset: int
    note: str

    @property
    def pointer(self) -> str:
        return " " * self.head_offset + "^"


class Tape:
    """Sparse single-tape representation."""

    def __init__(self, initial: str) -> None:
        self.cells = {index: symbol for index, symbol in enumerate(initial)}
        self.head = 0

    def read(self) -> str:
        return self.cells.get(self.head, BLANK)

    def write(self, symbol: str) -> None:
        if symbol == BLANK:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = symbol

    def move(self, direction: str) -> None:
        if direction == LEFT:
            self.head -= 1
        elif direction == RIGHT:
            self.head += 1
        elif direction == STAY:
            return
        else:
            raise ValueError(f"Bilinmeyen kafa hareketi: {direction!r}")

    def view(self) -> tuple[str, int]:
        keys = list(self.cells.keys()) + [0, self.head]
        left = min(keys)
        right = max(keys)
        text = "".join(self.cells.get(index, BLANK) for index in range(left, right + 1))
        return text, self.head - left

    def content(self) -> str:
        if not self.cells:
            return ""
        left = min(self.cells)
        right = max(self.cells)
        return "".join(self.cells.get(index, BLANK) for index in range(left, right + 1)).strip(BLANK)


class BinaryMultiplicationTM:
    """Binary multiplier that exposes each operation as a TM transition trace."""

    def __init__(self, multiplicand: str, multiplier: str) -> None:
        self.multiplicand_input = validate_binary(multiplicand, "Birinci sayi")
        self.multiplier_input = validate_binary(multiplier, "Ikinci sayi")
        self.initial_tape = f"{self.multiplicand_input}*{self.multiplier_input}="
        self.tape = Tape(self.initial_tape)
        self.logs: list[TransitionLog] = []
        self.current_state = "q_start"
        self.star_index: int | None = None
        self.equal_index: int | None = None
        self.multiplicand = ""
        self.multiplier = ""
        self.result = ""
        self.accepted = False

    def run(self) -> str:
        self._record(STAY, "q_find_star", "Baslangic durumundan * arama durumuna gecildi.")
        self._find_star()
        self._read_operands()
        self._write_result("0", "q_init_result", "Sonuc alani 0 ile baslatildi.")
        self._process_multiplier_bits()
        self._restore_multiplier()
        self.current_state = "q_accept"
        self.accepted = True
        self._record(STAY, "q_accept", "Makine kabul durumuna gecti.")
        return self.result

    def decimal_result(self) -> int:
        if not self.accepted:
            raise RuntimeError("Makine henuz calistirilmadi.")
        return binary_to_decimal(self.result)

    def format_logs(self, limit: int | None = None) -> str:
        selected = self.logs if limit is None else self.logs[:limit]
        lines: list[str] = []
        for log in selected:
            lines.append(
                f"Adim {log.step:04d} | durum={log.state:<24} "
                f"oku={log.read:<2} yaz={log.write:<2} hareket={log.move:<1} "
                f"sonraki={log.next_state:<24} | {log.note}"
            )
            lines.append(f"           bant: {log.tape}")
            lines.append(f"                 {log.pointer}")
        if limit is not None and len(self.logs) > limit:
            lines.append(f"... {len(self.logs) - limit} adim daha var.")
        return "\n".join(lines)

    def _record(
        self,
        move: str,
        next_state: str,
        note: str,
        write: str | None = None,
    ) -> None:
        state = self.current_state
        read = self.tape.read()
        symbol_to_write = read if write is None else write
        self.tape.write(symbol_to_write)
        self.tape.move(move)
        tape_text, head_offset = self.tape.view()
        self.logs.append(
            TransitionLog(
                step=len(self.logs) + 1,
                state=state,
                read=read,
                write=symbol_to_write,
                move=move,
                next_state=next_state,
                tape=tape_text,
                head_offset=head_offset,
                note=note,
            )
        )
        self.current_state = next_state

    def _move_to(self, target: int, state: str, note: str) -> None:
        self.current_state = state
        while self.tape.head < target:
            self._record(RIGHT, state, note)
        while self.tape.head > target:
            self._record(LEFT, state, note)

    def _find_star(self) -> None:
        self.current_state = "q_find_star"
        while True:
            symbol = self.tape.read()
            if symbol == "*":
                self.star_index = self.tape.head
                self._record(LEFT, "q_return_left", "* bulundu; operand ayrimi baslatildi.")
                return
            if symbol in {"0", "1"}:
                self._record(RIGHT, "q_find_star", "* aranirken sol operand uzerinde ilerleniyor.")
                continue
            self.current_state = "q_reject"
            raise ValueError("Bantta * ayiraci bulunamadi.")

    def _read_operands(self) -> None:
        if self.star_index is None:
            raise RuntimeError("* konumu bilinmiyor.")

        self._move_to(-1, "q_return_left", "Sol sinir aranarak birinci operandin basina donuluyor.")
        self._record(RIGHT, "q_read_multiplicand", "Sol sinir bulundu; multiplicand okunacak.")

        bits: list[str] = []
        while True:
            symbol = self.tape.read()
            if symbol == "*":
                self.multiplicand = "".join(bits)
                self._record(RIGHT, "q_read_multiplier", "Multiplicand tamamlandi; multiplier alanina gecildi.")
                break
            if symbol in {"0", "1"}:
                bits.append(symbol)
                self._record(RIGHT, "q_read_multiplicand", f"Multiplicand biti okundu: {symbol}")
                continue
            self.current_state = "q_reject"
            raise ValueError("Multiplicand okunurken gecersiz sembol goruldu.")

        bits = []
        while True:
            symbol = self.tape.read()
            if symbol == "=":
                self.multiplier = "".join(bits)
                self.equal_index = self.tape.head
                self._record(RIGHT, "q_init_result", "Multiplier tamamlandi; sonuc alanina gecildi.")
                break
            if symbol in {"0", "1"}:
                bits.append(symbol)
                self._record(RIGHT, "q_read_multiplier", f"Multiplier biti okundu: {symbol}")
                continue
            self.current_state = "q_reject"
            raise ValueError("Multiplier okunurken gecersiz sembol goruldu.")

        if not self.multiplicand or not self.multiplier:
            self.current_state = "q_reject"
            raise ValueError("Iki operand da en az bir bitten olusmalidir.")

    def _process_multiplier_bits(self) -> None:
        if self.star_index is None or self.equal_index is None:
            raise RuntimeError("Operand sinirlari bilinmiyor.")

        shift = 0
        for bit_index in range(self.equal_index - 1, self.star_index, -1):
            self._move_to(bit_index, "q_seek_multiplier_bit", "Multiplier sagdan sola taraniyor.")
            self.current_state = "q_read_multiplier_bit"
            bit = self.tape.read()
            if bit == "0":
                self._record(STAY, "q_skip_zero", f"Bit 0 okundu; {shift} basamak kaydirma icin toplama yok.", "x")
            elif bit == "1":
                self._record(STAY, "q_copy_multiplicand", f"Bit 1 okundu; {shift} basamak kaydirilmis parcali carpim eklenecek.", "y")
                partial = shift_left(self.multiplicand, shift)
                self._write_partial(partial, shift)
                new_result, columns = add_binary_with_trace(self.result, partial)
                self._trace_addition(columns)
                self._clear_work_area()
                self._write_result(
                    new_result,
                    "q_write_result",
                    f"Yeni sonuc yazildi: {self.result} + {partial} = {new_result}",
                )
            else:
                self.current_state = "q_reject"
                raise ValueError(f"Beklenmeyen multiplier sembolu: {bit!r}")
            shift += 1

    def _write_result(self, result: str, state: str, note: str) -> None:
        if self.equal_index is None:
            raise RuntimeError("= konumu bilinmiyor.")
        normalized = normalize_binary(result)
        start = self.equal_index + 1
        old_length = len(self.result)
        span = max(old_length, len(normalized), 1)

        self._move_to(start, state, "Sonuc alaninin basina gidiliyor.")
        self.current_state = state
        for offset in range(span):
            target = start + offset
            self._move_to(target, state, "Sonuc hucresine konumlaniliyor.")
            if offset < len(normalized):
                self._record(RIGHT, state, note if offset == 0 else "Sonuc biti yaziliyor.", normalized[offset])
            else:
                self._record(RIGHT, state, "Eski sonucun fazlalik biti temizleniyor.", BLANK)
        self.result = normalized

    def _write_partial(self, partial: str, shift: int) -> None:
        if self.equal_index is None:
            raise RuntimeError("= konumu bilinmiyor.")
        start = self.equal_index + 1 + len(self.result)
        self._move_to(start, "q_copy_multiplicand", "Gecici parcali carpim alanina gidiliyor.")
        self.current_state = "q_copy_multiplicand"
        symbols = "#" + partial
        for index, symbol in enumerate(symbols):
            self._move_to(start + index, "q_copy_multiplicand", "Parcali carpim icin hucre seciliyor.")
            note = (
                f"Multiplicand {self.multiplicand}, {shift} basamak sola kaydirilarak gecici alana yaziliyor."
                if index == 0
                else "Parcali carpim biti yaziliyor."
            )
            self._record(RIGHT, "q_copy_multiplicand", note, symbol)

    def _trace_addition(self, columns: Iterable[dict[str, int | str]]) -> None:
        self.current_state = "q_add_partial"
        for column in columns:
            note = (
                "Toplama kolonu: "
                f"{column['result_bit']} + {column['partial_bit']} + elde {column['carry_in']} "
                f"-> bit {column['sum_bit']}, yeni elde {column['carry_out']}"
            )
            self._record(STAY, "q_add_partial", note)

    def _clear_work_area(self) -> None:
        if self.equal_index is None:
            raise RuntimeError("= konumu bilinmiyor.")
        start = self.equal_index + 1 + len(self.result)
        if start not in self.tape.cells:
            return
        self._move_to(start, "q_clear_work", "Gecici alana donuluyor.")
        self.current_state = "q_clear_work"
        position = start
        while position in self.tape.cells:
            self._move_to(position, "q_clear_work", "Gecici hucre temizleniyor.")
            self._record(RIGHT, "q_clear_work", "Gecici calisma sembolu silindi.", BLANK)
            position += 1

    def _restore_multiplier(self) -> None:
        if self.star_index is None or self.equal_index is None:
            raise RuntimeError("Operand sinirlari bilinmiyor.")
        self._move_to(self.star_index + 1, "q_restore_multiplier", "Multiplier isaretleri geri alinacak.")
        self.current_state = "q_restore_multiplier"
        while self.tape.head < self.equal_index:
            symbol = self.tape.read()
            if symbol == "x":
                self._record(RIGHT, "q_restore_multiplier", "Isaretli 0 biti geri yuklendi.", "0")
            elif symbol == "y":
                self._record(RIGHT, "q_restore_multiplier", "Isaretli 1 biti geri yuklendi.", "1")
            elif symbol in {"0", "1"}:
                self._record(RIGHT, "q_restore_multiplier", "Multiplier biti zaten temiz.")
            else:
                self.current_state = "q_reject"
                raise ValueError("Multiplier geri yuklenirken gecersiz sembol goruldu.")


def validate_binary(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{label} bos olamaz.")
    if any(symbol not in {"0", "1"} for symbol in cleaned):
        raise ValueError(f"{label} yalnizca 0 ve 1 karakterlerinden olusmalidir.")
    return cleaned


def normalize_binary(value: str) -> str:
    stripped = value.lstrip("0")
    return stripped or "0"


def shift_left(value: str, shift: int) -> str:
    normalized = normalize_binary(value)
    if normalized == "0":
        return "0"
    return normalized + ("0" * shift)


def add_binary_with_trace(left: str, right: str) -> tuple[str, list[dict[str, int | str]]]:
    left = normalize_binary(left)
    right = normalize_binary(right)
    i = len(left) - 1
    j = len(right) - 1
    carry = 0
    output: list[str] = []
    columns: list[dict[str, int | str]] = []

    while i >= 0 or j >= 0 or carry:
        left_bit = int(left[i]) if i >= 0 else 0
        right_bit = int(right[j]) if j >= 0 else 0
        carry_in = carry
        total = left_bit + right_bit + carry
        sum_bit = total % 2
        carry = total // 2
        output.append(str(sum_bit))
        columns.append(
            {
                "result_bit": left_bit,
                "partial_bit": right_bit,
                "carry_in": carry_in,
                "sum_bit": sum_bit,
                "carry_out": carry,
            }
        )
        i -= 1
        j -= 1

    return normalize_binary("".join(reversed(output))), columns


def binary_to_decimal(value: str) -> int:
    decimal = 0
    for bit in normalize_binary(value):
        decimal = decimal * 2 + int(bit)
    return decimal


def format_transition_table() -> str:
    headers = ("Durum", "Oku", "Yaz", "Hareket", "Sonraki", "Amac")
    widths = [22, 11, 9, 8, 22, 0]
    rows = [headers, *TRANSITION_TABLE]
    lines = []
    for row in rows:
        lines.append(
            f"{row[0]:<{widths[0]}} {row[1]:<{widths[1]}} {row[2]:<{widths[2]}} "
            f"{row[3]:<{widths[3]}} {row[4]:<{widths[4]}} {row[5]}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tek bantli Turing Makinesi ile binary carpma hesaplayici."
    )
    parser.add_argument("multiplicand", nargs="?", help="Birinci binary sayi")
    parser.add_argument("multiplier", nargs="?", help="Ikinci binary sayi")
    parser.add_argument("--no-trace", action="store_true", help="Adim adim gecisleri yazdirma.")
    parser.add_argument("--trace-limit", type=int, default=None, help="Yazdirilacak en fazla gecis sayisi.")
    parser.add_argument("--table", action="store_true", help="Gecis tablosunu yazdir.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.table:
        print(format_transition_table())
        return 0

    multiplicand = args.multiplicand or input("Birinci binary sayi: ")
    multiplier = args.multiplier or input("Ikinci binary sayi: ")

    try:
        machine = BinaryMultiplicationTM(multiplicand, multiplier)
        result = machine.run()
    except ValueError as exc:
        print(f"Hata: {exc}")
        return 1

    print(f"Girdi bandi: {machine.initial_tape}")
    print(f"Operand ayrimi: {machine.multiplicand} * {machine.multiplier}")
    if not args.no_trace:
        print("\nAdim adim simulasyon:")
        print(machine.format_logs(args.trace_limit))
    print("\nSonuc:")
    print(f"Binary : {result}")
    print(f"Decimal: {machine.decimal_result()}")
    print(f"Final bant: {machine.tape.content()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
