import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "5f75b25fbfa47eba01d79fbe5323882e9852ce22"


def original(file):
    return subprocess.check_output(["git", "show", f"{BASE}:{file}"], cwd=ROOT)


class ReadingContract(unittest.TestCase):
    def test_all_seven_font_sizes_follow_the_users_default(self):
        css = (ROOT / "assets/legal.css").read_text()
        sizes = re.findall(r"font-size:\s*([^;\n}]+)", css)
        self.assertEqual(len(sizes), 7)
        for size in sizes:
            self.assertRegex(size.strip(), r"^\d+(?:\.\d+)?rem$")

    def test_default_font_sizes_and_other_css_remain_equivalent(self):
        before = original("assets/legal.css").decode()
        after = (ROOT / "assets/legal.css").read_text()
        pattern = r"font-size:\s*([\d.]+)(px|rem)"
        old = re.findall(pattern, before)
        new = re.findall(pattern, after)
        self.assertEqual(len(old), len(new))
        for (old_value, old_unit), (new_value, new_unit) in zip(old, new):
            self.assertEqual(old_unit, "px")
            self.assertEqual(new_unit, "rem")
            self.assertEqual(float(old_value), float(new_value) * 16)
        self.assertEqual(re.sub(pattern, "font-size: REVIEWED", before),
                         re.sub(pattern, "font-size: REVIEWED", after))

    def test_documents_icons_and_manifest_are_byte_identical(self):
        files = ["assets/skireview.png", "assets/social.png", "manifest.json",
                 "index.html", "support/index.html", "privacy/index.html", "terms/index.html"]
        for file in files:
            with self.subTest(file=file):
                self.assertFalse((ROOT / file).is_symlink())
                self.assertEqual((ROOT / file).read_bytes(), original(file))


if __name__ == "__main__":
    unittest.main()
