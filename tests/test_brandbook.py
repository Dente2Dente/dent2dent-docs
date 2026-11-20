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
PROIBIDOS = ("montserrat", "hyperiontech", "hyperion")

HOME = RAIZ / "site" / "index.html"
ESQUELETOS = BRANDBOOK / "esqueletos"
RAIOS_DO_SITE = ("--r-xs:6px", "--r-sm:10px", "--r-md:14px", "--r-lg:20px", "--r-xl:28px")
RAIOS_PERMITIDOS = {
    "var(--r-xs)", "var(--r-sm)", "var(--r-md)", "var(--r-lg)", "var(--r-xl)",
    "999px", "0", "50%",
}
RAIOS_DIREITA_ARREDONDADA = {"0 var(--r-md) var(--r-md) 0"}
RGBA_DE_PRETO = {".08", ".14"}
TINTA_DE_ESTADO = {"31,138,91": "verde", "37,99,235": "azul", "180,83,9": "ambar", "185,28,28": "perigo"}
LOGO_REAL = '<img src="https://dent2dent.com.br/logo.png" alt="Dent2Dent">'


def paginas():
    return sorted(BRANDBOOK.rglob("*.html"))


def hexes(txt):
    return {h.lower() for h in re.findall(r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", txt)}


def raios(txt):
    return {r.strip() for r in re.findall(r"border-radius:([^;}\"]+)", txt)}


def rgbas(txt):
    return re.findall(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\.?\d*\.?\d+)\s*\)", txt)


def regra(txt, seletor):
    m = re.search(re.escape(seletor) + r"\{([^}]*)\}", txt)
    assert m, seletor
    return m.group(1)


def paginas_e_home():
    return paginas() + [HOME]


class TokensDoSiteTest(unittest.TestCase):
    def test_raios_do_site_nas_tres_superficies(self):
        for p in paginas_e_home():
            txt = p.read_text(encoding="utf-8").replace(" ", "")
            for r in RAIOS_DO_SITE:
                self.assertTrue(r in txt, f"{p.name}: falta {r}")
            self.assertFalse("--r-lg:16px" in txt, p.name)

    def test_nenhum_raio_literal_fora_dos_tokens_do_site(self):
        for p in paginas_e_home():
            usados = raios(p.read_text(encoding="utf-8")) - RAIOS_DIREITA_ARREDONDADA
            self.assertEqual(usados - RAIOS_PERMITIDOS, set(), p.name)

    def test_linha_e_a_do_site(self):
        for p in paginas_e_home():
            txt = p.read_text(encoding="utf-8").replace(" ", "")
            self.assertFalse("#e5e5ea" in txt.lower(), p.name)
            self.assertFalse("--linha" in txt, p.name)
            self.assertTrue("--hair:rgba(0,0,0,.08)" in txt, f"{p.name}: falta --hair")
            self.assertTrue("--hair-strong:rgba(0,0,0,.14)" in txt, f"{p.name}: falta --hair-strong")

    def test_rgba_de_preto_so_a_8_e_14_por_cento(self):
        for p in paginas_e_home():
            for r, g, b, a in rgbas(p.read_text(encoding="utf-8")):
                if (r, g, b) == ("0", "0", "0"):
                    self.assertIn(a, RGBA_DE_PRETO, p.name)

    def test_tinta_de_estado_a_8_por_cento(self):
        for p in paginas_e_home():
            for r, g, b, a in rgbas(p.read_text(encoding="utf-8")):
                if f"{r},{g},{b}" in TINTA_DE_ESTADO:
                    self.assertEqual(a, ".08", f"{p.name}: {r},{g},{b}")

    def test_marca_em_texto_e_a_do_rodape_do_site(self):
        for p in paginas_e_home():
            txt = p.read_text(encoding="utf-8")
            self.assertFalse("D<b>2</b>D" in txt, p.name)
            self.assertTrue("Dent<b>2</b>Dent" in txt, p.name)
            for seletor in (".rodape .marca", ".m-rodape .marca", ".logo", ".marca-g"):
                if seletor + "{" in txt:
                    css = regra(txt, seletor)
                    self.assertIn("font-weight:500", css, f"{p.name} {seletor}")
                    self.assertNotIn("font-weight:800", css, f"{p.name} {seletor}")
                    self.assertIn("letter-spacing:-.025em", css, f"{p.name} {seletor}")

    def test_texto_sobre_tinta_verde_e_ink_2_e_o_verde_so_na_borda(self):
        roteiro = (ESQUELETOS / "roteiro-esqueleto.html").read_text(encoding="utf-8")
        self.assertNotIn("color:var(--verde)", regra(roteiro, ".certo b"))
        self.assertIn("color:var(--ink-2)", regra(roteiro, ".certo b"))
        self.assertIn("border-left:3px solid var(--verde)", regra(roteiro, ".certo"))
        home = HOME.read_text(encoding="utf-8")
        novo = regra(home, ".novo")
        self.assertNotIn("color:var(--verde)", novo)
        self.assertIn("color:var(--ink-2)", novo)
        self.assertIn("border:1px solid var(--verde)", novo)


# A bolinha da legenda do guia tem de ser a mesma cor da marcação que o prints.mjs desenha no print.
HEX_FUNCIONAIS = {"#f28c18"}


class BrandbookTest(unittest.TestCase):
    def test_brandbook_existe(self):
        self.assertTrue((BRANDBOOK / "index.html").is_file())

    def test_sem_travessao_nem_traco_longo(self):
        for p in paginas():
            txt = p.read_text(encoding="utf-8")
            self.assertNotIn("—", txt, p.name)
            self.assertNotIn("–", txt, p.name)

    def test_so_hex_da_marca(self):
        permitidos = HEX_D6 | HEX_NEUTROS | HEX_FUNCIONAIS
        for p in paginas():
            txt = p.read_text(encoding="utf-8")
            achados = {h.lower() for h in re.findall(r'(?<!href=")(?:#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b)', txt)}
            self.assertEqual(achados - permitidos, set(), p.name)

    def test_tokens_da_marca_presentes_no_brandbook(self):
        txt = (BRANDBOOK / "index.html").read_text(encoding="utf-8").lower()
        for h in HEX_D6:
            self.assertIn(h, txt)

    def test_logo_real_por_url_absoluta_e_sem_a_frase_antiga(self):
        txt = (BRANDBOOK / "index.html").read_text(encoding="utf-8")
        self.assertTrue(LOGO_REAL in txt, "falta o logo real por URL absoluta")
        for frase in ("Não existe arquivo de imagem", "nada foi acrescentado", "passos de 4px"):
            self.assertFalse(frase in txt, frase)
        self.assertFalse(list(BRANDBOOK.rglob("*.png")))

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


class HomeTest(unittest.TestCase):
    def test_so_hex_da_marca(self):
        permitidos = HEX_D6 | HEX_NEUTROS
        self.assertEqual(hexes(HOME.read_text(encoding="utf-8")) - permitidos, set())

    def test_chips_da_home_sao_pilula_como_no_site(self):
        self.assertIn("border-radius:999px", regra(HOME.read_text(encoding="utf-8"), ".contagem span"))

    def test_link_do_brandbook_resolve(self):
        txt = HOME.read_text(encoding="utf-8")
        hrefs = set(re.findall(r'href="(brandbook/[^"]*)"', txt))
        self.assertTrue(hrefs)
        for href in hrefs:
            alvo = HOME.parent / href
            self.assertTrue((alvo / "index.html" if href.endswith("/") else alvo).is_file(), href)


ESQUELETOS_DA_MARCA = ("spec-esqueleto.html", "roteiro-esqueleto.html", "guia-esqueleto.html")


class EsqueletosTest(unittest.TestCase):
    def ler(self, nome):
        return (BRANDBOOK / "esqueletos" / nome).read_text(encoding="utf-8")

    def test_os_tres_esqueletos_existem(self):
        for nome in ESQUELETOS_DA_MARCA:
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

    def test_rodape_com_a_marca_em_texto_do_site(self):
        for nome in ESQUELETOS_DA_MARCA:
            self.assertTrue('<div class="marca">Dent<b>2</b>Dent</div>' in self.ler(nome), nome)

    def test_faixa_do_topo_e_azul_liso(self):
        for nome in ESQUELETOS_DA_MARCA:
            self.assertIn(".faixa{height:5px;background:var(--azul)}", self.ler(nome), nome)
            self.assertNotIn("gradient", self.ler(nome), nome)


if __name__ == "__main__":
    unittest.main()
