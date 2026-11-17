import importlib.util
import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = importlib.util.spec_from_file_location("work_order_gate", os.path.join(ROOT, "tools", "gate.py"))
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


class FunctionDeclarationCountTests(unittest.TestCase):
    def test_counts_one_declaration(self):
        source = "function bimCurvePoint(c, u) {\n  return u;\n}\n"
        self.assertEqual(GATE.function_declaration_count(source, "bimCurvePoint"), 1)

    def test_detects_duplicate_declarations(self):
        source = "function bimCurvePoint(c, u) {}\nfunction bimCurvePoint(c, u) {}\n"
        self.assertEqual(GATE.function_declaration_count(source, "bimCurvePoint"), 2)

    def test_ignores_mentions_that_are_not_declarations(self):
        source = "// function bimCurvePoint(c, u)\nvar value = bimCurvePoint(c, u);\n"
        self.assertEqual(GATE.function_declaration_count(source, "bimCurvePoint"), 0)


if __name__ == "__main__":
    unittest.main()
