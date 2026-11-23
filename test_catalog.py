import unittest

from catalog_check import compare


class CatalogTests(unittest.TestCase):
    def test_reordering_and_escaped_braces(self):
        self.assertEqual(compare(
            {"msg": "{name}: {count} items {{total}}"},
            {"msg": "{count} عناصر للمستخدم {name}"},
        ), [])

    def test_changed_count_and_missing_key(self):
        findings = compare(
            {"msg": "{name} {name}", "other": "Hello"},
            {"msg": "{name} {user}"},
        )
        self.assertEqual([entry["kind"] for entry in findings], ["placeholders", "missing"])
        self.assertEqual(findings[0]["missing"], ["name"])
        self.assertEqual(findings[0]["extra"], ["user"])

    def test_nested_spec_and_bad_format(self):
        self.assertEqual(compare({"p": "{total:{width}.2f}"}, {"p": "{total:.2f}"})[0]["missing"], ["width"])
        self.assertEqual(compare({"p": "{name}"}, {"p": "Hi {name"})[0]["kind"], "invalid-format")
