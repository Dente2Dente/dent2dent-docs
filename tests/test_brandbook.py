import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRANDBOOK = RAIZ / "site" / "brandbook"

HEX_D6 = {
    "#1d1d1f", "#424245", "#2563eb", "#1d4ed8", "#f5f5f7", "#6e6e73",
    "#1f8a5b", "#b45309", "#b91c1c",
}
HEX_NEUTROS = {"#fff", "#ffffff", "#000", "#000000"}
LINHA = "#e5e5ea"
PROIBIDOS = ("montserrat", "hyperiontech", "hyperion")


def paginas():
    return sorted(BRANDBOOK.rglob("*.html"))


class BrandbookTest(unittest.TestCase):
    def test_brandbook_existe(self):
        self.assertTrue((BRANDBOOK / "index.html").is_file())

    def test_sem_travessao_nem_traco_longo(self):
        for p in paginas():
            txt = p.read_text(encoding="utf-8")
            self.assertNotIn("—", txt, p.name)
            self.assertNotIn("–", txt, p.name)

    def test_so_hex_da_marca(self):
        permitidos = HEX_D6 | HEX_NEUTROS | {LINHA}
        for p in paginas():
            txt = p.read_text(encoding="utf-8")
            achados = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", txt)}
            self.assertEqual(achados - permitidos, set(), p.name)

    def test_tokens_da_marca_presentes_no_brandbook(self):
        txt = (BRANDBOOK / "index.html").read_text(encoding="utf-8").lower()
        for h in HEX_D6 | {LINHA}:
            self.assertIn(h, txt)

    def test_sem_fonte_nem_nome_de_outra_marca(self):
        for p in paginas():
            txt = p.read_text(encoding="utf-8").lower()
            for palavra in PROIBIDOS:
                self.assertNotIn(palavra, txt, f"{p.name}: {palavra}")

    def test_noindex_em_todas_as_paginas(self):
        for p in paginas():
            self.assertIn('<meta name="robots" content="noindex">', p.read_text(encoding="utf-8"), p.name)

    def test_inter_e_a_fonte(self):
        for p in paginas():
            self.assertIn("family=Inter:", p.read_text(encoding="utf-8"), p.name)

    def test_links_relativos(self):
        for p in paginas():
            txt = p.read_text(encoding="utf-8")
            self.assertEqual(re.findall(r'(?:href|src)="/[^/"]', txt), [], p.name)

    def test_links_internos_do_brandbook_resolvem(self):
        txt = (BRANDBOOK / "index.html").read_text(encoding="utf-8")
        for href in re.findall(r'href="([^":#]+)"', txt):
            if href.startswith(("../", "esqueletos/")):
                continue
            self.assertTrue((BRANDBOOK / href).exists(), href)


if __name__ == "__main__":
    unittest.main()
