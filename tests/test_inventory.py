import io
import os
import tempfile
import unittest

from inventory.cli import main
from inventory.db import Inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()

    def test_add_and_list(self):
        self.inv.add("Widget", 10, 2.5)
        self.inv.add("Gadget", 3, 10)
        self.assertEqual([i.name for i in self.inv.list()], ["Gadget", "Widget"])
        self.assertEqual([i.name for i in self.inv.list("wid")], ["Widget"])

    def test_duplicate_is_case_insensitive(self):
        self.inv.add("Widget", 1, 1)
        with self.assertRaises(ValueError):
            self.inv.add("widget", 1, 1)

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.inv.add("  ", 1, 1)
        with self.assertRaises(ValueError):
            self.inv.add("Bad", -1, 1)

    def test_adjust_and_no_negative_stock(self):
        self.inv.add("Widget", 2, 1)
        self.assertEqual(self.inv.adjust("Widget", 3), 5)
        with self.assertRaises(ValueError):
            self.inv.adjust("Widget", -6)
        with self.assertRaises(KeyError):
            self.inv.adjust("Nope", 1)

    def test_total_value_and_low_stock(self):
        self.inv.add("A", 2, 5)
        self.inv.add("B", 10, 1)
        self.assertEqual(self.inv.total_value(), 20)
        self.assertEqual([i.name for i in self.inv.low_stock(2)], ["A"])

    def test_remove(self):
        self.inv.add("A", 1, 1)
        self.inv.remove("A")
        self.assertEqual(self.inv.list(), [])
        with self.assertRaises(KeyError):
            self.inv.remove("A")


class CliTests(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            db = os.path.join(d, "t.db")
            out = io.StringIO()
            self.assertEqual(main(["--db", db, "add", "Widget", "4", "2.50"], out), 0)
            self.assertEqual(main(["--db", db, "value"], out), 0)
            self.assertIn("Total value: $10.00", out.getvalue())
            self.assertEqual(main(["--db", db, "stock", "Widget", "-9"], out), 1)


if __name__ == "__main__":
    unittest.main()
