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
            if href.startswith("../"):
                continue
            self.assertTrue((BRANDBOOK / href).exists(), href)


class EsqueletosTest(unittest.TestCase):
    def ler(self, nome):
        return (BRANDBOOK / "esqueletos" / nome).read_text(encoding="utf-8")

    def test_os_dois_esqueletos_existem(self):
        for nome in ("spec-esqueleto.html", "roteiro-esqueleto.html"):
            self.assertTrue((BRANDBOOK / "esqueletos" / nome).is_file(), nome)

    def test_campos_de_conteudo_preservados(self):
        spec = self.ler("spec-esqueleto.html")
        for campo in ("TITULO", "EPIC_OU_FEATURE", "NUMERO", "LEAD", "REPO", "N_FEATURES",
                      "N_PBIS", "N_TASKS", "HORAS", "DATA", "VEREDITO", "SECAO", "CONTEUDO"):
            self.assertIn("{{" + campo + "}}", spec, campo)
        roteiro = self.ler("roteiro-esqueleto.html")
        for campo in ("TITULO", "PRODUTO", "O_QUE_ESTA_SENDO_HOMOLOGADO", "ONDE_ACESSAR_E_COM_QUAL_USUARIO",
                      "FEATURE", "OBJETIVO_EM_LINGUAGEM_DE_NEGOCIO", "NOME_DO_CASO", "PASSO",
                      "CRITERIO_OBSERVAVEL", "NUMERO", "DATA"):
            self.assertIn("{{" + campo + "}}", roteiro, campo)

    def test_rodape_com_logo_d2d(self):
        for nome in ("spec-esqueleto.html", "roteiro-esqueleto.html"):
            self.assertIn('<div class="marca">D<b>2</b>D</div>', self.ler(nome), nome)

    def test_faixa_do_topo_e_azul_liso(self):
        for nome in ("spec-esqueleto.html", "roteiro-esqueleto.html"):
            self.assertIn(".faixa{height:5px;background:var(--azul)}", self.ler(nome), nome)
            self.assertNotIn("gradient", self.ler(nome), nome)


if __name__ == "__main__":
    unittest.main()
