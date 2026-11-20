import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import publicar  # noqa: E402

SPEC = (
    '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Spec</title></head>'
    '<body><a href="2026-11-20-agenda-prototipo.html">protótipo</a></body></html>'
)
PROTO_COM_ROBOTS = '<html><head><meta name="robots" content="index"></head><body>p</body></html>'


class PublicarTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.site = base / "site"
        self.site.mkdir()
        (self.site / "manifest.js").write_text(
            'window.DOCS_MANIFEST = {"generated": "2026-11-20", "docs": []};\n', encoding="utf-8")
        self.spec = base / "spec.html"
        self.spec.write_text(SPEC, encoding="utf-8")
        self.proto = base / "proto.html"
        self.proto.write_text(PROTO_COM_ROBOTS, encoding="utf-8")
        self.antigo = (publicar.SITE, publicar.MANIFEST)
        publicar.SITE, publicar.MANIFEST = self.site, self.site / "manifest.js"
        self.addCleanup(self.restaurar)

    def restaurar(self):
        publicar.SITE, publicar.MANIFEST = self.antigo

    def rodar(self, *args):
        argv = sys.argv
        sys.argv = ["publicar.py", *args]
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                publicar.main()
        finally:
            sys.argv = argv

    def manifest(self):
        return publicar.ler_manifest()

    def test_manifest_do_repo_e_json_valido(self):
        real = (RAIZ / "site" / "manifest.js").read_text(encoding="utf-8")
        txt = real[real.index("{"): real.rindex("}") + 1]
        self.assertIsInstance(json.loads(txt)["docs"], list)

    def test_grava_design_e_entrada_no_manifest(self):
        self.rodar("--projeto", "app", "--projeto-nome", "App", "--slug", "agenda",
                   "--titulo", "Agenda", "--spec", str(self.spec),
                   "--issue", "https://github.com/org/repo/issues/12", "--nota", "Uma linha")
        self.assertTrue((self.site / "app" / "agenda" / "design.html").is_file())
        doc = self.manifest()["docs"][0]
        self.assertEqual(doc["projeto"], "app")
        self.assertEqual(doc["projetoNome"], "App")
        self.assertEqual(doc["spec"], "design.html")
        self.assertIsNone(doc["prototipo"])
        self.assertEqual(doc["issue"]["numero"], 12)

    def test_injeta_noindex_quando_falta(self):
        self.rodar("--projeto", "app", "--slug", "agenda", "--titulo", "Agenda", "--spec", str(self.spec))
        html = (self.site / "app" / "agenda" / "design.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('name="robots"'), 1)
        self.assertLess(html.index('name="robots"'), html.index("</head>"))

    def test_nao_duplica_robots_existente(self):
        self.rodar("--projeto", "app", "--slug", "agenda", "--titulo", "Agenda", "--prototipo", str(self.proto))
        html = (self.site / "app" / "agenda" / "prototipo.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('name="robots"'), 1)

    def publicar_proto(self, html):
        self.proto.write_text(html, encoding="utf-8")
        self.rodar("--projeto", "app", "--slug", "agenda", "--titulo", "Agenda", "--prototipo", str(self.proto))
        return (self.site / "app" / "agenda" / "prototipo.html").read_text(encoding="utf-8")

    def test_robots_index_existente_vira_noindex(self):
        html = self.publicar_proto(PROTO_COM_ROBOTS)
        self.assertEqual(re.findall(r"<meta[^>]*name=.robots.[^>]*>", html), ['<meta name="robots" content="noindex">'])

    def test_robots_sem_valor_noindex_ganha_noindex_e_preserva_nofollow(self):
        html = self.publicar_proto('<html><head><meta content="index, nofollow" name="robots"></head></html>')
        self.assertEqual(re.findall(r"<meta[^>]*name=.robots.[^>]*>", html), ['<meta content="noindex, nofollow" name="robots">'])

    def test_robots_sem_content_ganha_noindex(self):
        html = self.publicar_proto('<html><head><meta name="robots"></head></html>')
        self.assertEqual(re.findall(r"<meta[^>]*name=.robots.[^>]*>", html), ['<meta name="robots" content="noindex">'])

    def test_robots_ja_noindex_fica_igual(self):
        html = self.publicar_proto('<html><head><meta name="robots" content="noindex, nofollow"></head></html>')
        self.assertIn('content="noindex, nofollow"', html)

    def test_reescreve_link_do_prototipo_datado(self):
        self.rodar("--projeto", "app", "--slug", "agenda", "--titulo", "Agenda", "--spec", str(self.spec))
        html = (self.site / "app" / "agenda" / "design.html").read_text(encoding="utf-8")
        self.assertIn('href="./prototipo.html"', html)

    def test_rodar_de_novo_so_com_spec_mantem_prototipo(self):
        self.rodar("--projeto", "app", "--slug", "agenda", "--titulo", "Agenda",
                   "--spec", str(self.spec), "--prototipo", str(self.proto))
        self.rodar("--projeto", "app", "--slug", "agenda", "--spec", str(self.spec))
        docs = self.manifest()["docs"]
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["prototipo"], "prototipo.html")

    def test_slug_com_acento_e_recusado(self):
        with self.assertRaises(SystemExit):
            self.rodar("--projeto", "app", "--slug", "Agenda Nova", "--titulo", "x", "--spec", str(self.spec))

    def test_documento_novo_sem_titulo_e_recusado(self):
        with self.assertRaises(SystemExit):
            self.rodar("--projeto", "app", "--slug", "agenda", "--spec", str(self.spec))

    def test_nao_deixa_projeto_de_exemplo_no_site_real(self):
        self.rodar("--projeto", "app", "--slug", "agenda", "--titulo", "Agenda", "--spec", str(self.spec))
        self.assertFalse((RAIZ / "site" / "app").exists())
        self.assertNotIn('"projeto": "app"', (RAIZ / "site" / "manifest.js").read_text(encoding="utf-8"))

    def test_script_roda_pela_linha_de_comando(self):
        r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "publicar.py"), "--help"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
