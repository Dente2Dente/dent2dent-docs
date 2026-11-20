#!/usr/bin/env python3
"""Copia spec e protótipo para site/<projeto>/<slug>/ e registra no site/manifest.js.

Uso:
    python3 scripts/publicar.py --projeto app --projeto-nome "App" \
        --slug agenda --titulo "Agenda do consultório" \
        --spec ~/caminho/design.html --prototipo ~/caminho/prototipo.html \
        --issue https://github.com/<org>/<repo>/issues/30 --nota "Uma linha"

O link do spec para o protótipo datado (AAAA-MM-DD-<slug>-prototipo.html) vira ./prototipo.html.
Idempotente por projeto e slug: rodar de novo só com --spec preenche o slot e mantém o protótipo.
Todo HTML publicado sai com <meta name="robots" content="noindex">.
Não faz commit nem push; o push na main é o que publica.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "site"
MANIFEST = SITE / "manifest.js"
URL_BASE = "https://dente2dente.github.io/dent2dent-docs"
CABECALHO = "// Fonte única do que a home lista. Quem escreve é o scripts/publicar.py.\n"
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_PROTOTIPO = re.compile(r'(href=")(?:\./)?\d{4}-\d{2}-\d{2}-[a-z0-9-]+-prototipo\.html')
META_ROBOTS = re.compile(r'<meta\s+name=["\']robots["\']', re.IGNORECASE)
ABRE_HEAD = re.compile(r"<head[^>]*>", re.IGNORECASE)
ABRE_HTML = re.compile(r"<html[^>]*>", re.IGNORECASE)
NOINDEX = '<meta name="robots" content="noindex">'


def falha(msg):
    print(f"erro: {msg}", file=sys.stderr)
    sys.exit(1)


def ler_manifest():
    txt = MANIFEST.read_text(encoding="utf-8")
    return json.loads(txt[txt.index("{"): txt.rindex("}") + 1])


def gravar_manifest(dados):
    corpo = json.dumps(dados, ensure_ascii=False, indent=2)
    MANIFEST.write_text(CABECALHO + "window.DOCS_MANIFEST = " + corpo + ";\n", encoding="utf-8")


def garantir_noindex(texto):
    if META_ROBOTS.search(texto):
        return texto
    for abertura in (ABRE_HEAD, ABRE_HTML):
        achado = abertura.search(texto)
        if achado:
            fim = achado.end()
            return texto[:fim] + "\n" + NOINDEX + texto[fim:]
    return NOINDEX + "\n" + texto


def copiar(origem, destino, reescrever_links=False):
    origem = Path(origem).expanduser()
    if not origem.is_file() or origem.suffix != ".html" or origem.stat().st_size == 0:
        falha(f"{origem} não existe, está vazio ou não é .html")
    try:
        texto = origem.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        falha(f"{origem} não está em UTF-8")
    if "\u2014" in texto or "\u2013" in texto:
        print(f"aviso: {origem.name} tem travessão ou traço", file=sys.stderr)
    if reescrever_links:
        texto = LINK_PROTOTIPO.sub(r"\1./prototipo.html", texto)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(garantir_noindex(texto), encoding="utf-8")
    return destino.name


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--projeto", required=True)
    p.add_argument("--projeto-nome")
    p.add_argument("--slug", required=True)
    p.add_argument("--titulo")
    p.add_argument("--spec")
    p.add_argument("--prototipo")
    p.add_argument("--issue")
    p.add_argument("--nota")
    p.add_argument("--data", default=date.today().isoformat())
    a = p.parse_args()

    for nome, valor in (("projeto", a.projeto), ("slug", a.slug)):
        if not SLUG.match(valor):
            falha(f"--{nome} '{valor}' precisa ser kebab-case sem acento")

    dados = ler_manifest()
    docs = dados.setdefault("docs", [])
    atual = next((d for d in docs if d["projeto"] == a.projeto and d["slug"] == a.slug), None)
    if atual is None:
        if not a.titulo:
            falha("documento novo precisa de --titulo")
        atual = {"projeto": a.projeto, "projetoNome": a.projeto, "slug": a.slug, "titulo": a.titulo,
                 "data": a.data, "nota": "", "issue": None, "spec": None, "prototipo": None}
        docs.append(atual)

    pasta = SITE / a.projeto / a.slug
    if a.spec:
        atual["spec"] = copiar(a.spec, pasta / "design.html", reescrever_links=True)
    if a.prototipo:
        atual["prototipo"] = copiar(a.prototipo, pasta / "prototipo.html")
    if a.projeto_nome:
        atual["projetoNome"] = a.projeto_nome
    if a.titulo:
        atual["titulo"] = a.titulo
    if a.nota is not None:
        atual["nota"] = a.nota
    if a.issue:
        m = re.search(r"/issues/(\d+)", a.issue)
        if not m:
            falha("--issue precisa ser a URL de uma issue do GitHub")
        atual["issue"] = {"numero": int(m.group(1)), "url": a.issue}
    atual["data"] = a.data

    dados["generated"] = date.today().isoformat()
    gravar_manifest(dados)
    for chave in ("spec", "prototipo"):
        if atual[chave]:
            print(f"{chave}: {URL_BASE}/{a.projeto}/{a.slug}/{atual[chave]}")


if __name__ == "__main__":
    main()
