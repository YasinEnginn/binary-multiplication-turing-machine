import unittest

from binary_multiplier_tm import BinaryMultiplicationTM, add_binary_with_trace, binary_to_decimal


class BinaryMultiplicationTMTests(unittest.TestCase):
    def run_machine(self, left: str, right: str) -> BinaryMultiplicationTM:
        machine = BinaryMultiplicationTM(left, right)
        machine.run()
        return machine

    def test_assignment_example(self) -> None:
        machine = self.run_machine("11", "10")

        self.assertEqual(machine.result, "110")
        self.assertEqual(machine.decimal_result(), 6)
        self.assertEqual(machine.tape.content(), "11*10=110")

    def test_zero_times_zero(self) -> None:
        machine = self.run_machine("0", "0")

        self.assertEqual(machine.result, "0")
        self.assertEqual(machine.decimal_result(), 0)

    def test_zero_times_nonzero(self) -> None:
        machine = self.run_machine("0", "1011")

        self.assertEqual(machine.result, "0")
        self.assertEqual(machine.decimal_result(), 0)

    def test_one_times_number(self) -> None:
        machine = self.run_machine("1", "11101")

        self.assertEqual(machine.result, "11101")
        self.assertEqual(machine.decimal_result(), 29)

    def test_multi_bit_operands(self) -> None:
        machine = self.run_machine("101", "11")

        self.assertEqual(machine.result, "1111")
        self.assertEqual(machine.decimal_result(), 15)

    def test_large_sample(self) -> None:
        machine = self.run_machine("1001", "101")

        self.assertEqual(machine.result, "101101")
        self.assertEqual(machine.decimal_result(), 45)

    def test_operand_delimiters_are_preserved(self) -> None:
        machine = self.run_machine("111", "111")

        self.assertEqual(machine.initial_tape, "111*111=")
        self.assertEqual(machine.tape.content(), "111*111=110001")

    def test_invalid_input_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BinaryMultiplicationTM("102", "11")

        with self.assertRaises(ValueError):
            BinaryMultiplicationTM("", "11")

    def test_binary_addition_helper(self) -> None:
        result, trace = add_binary_with_trace("111", "101")

        self.assertEqual(result, "1100")
        self.assertGreaterEqual(len(trace), 3)
        self.assertEqual(binary_to_decimal(result), 12)


if __name__ == "__main__":
    unittest.main()
