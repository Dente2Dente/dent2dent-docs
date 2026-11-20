# dent2dent-docs

Specs, protótipos e brandbook da Dent2Dent, publicados no GitHub Pages em
**https://dente2dente.github.io/dent2dent-docs/**.

## O site é público

**Não há login.** Protótipo entra só com dado fictício; spec entra sem segredo, nome de cliente,
valor real ou URL interna. A home tem `<meta name="robots" content="noindex">` e o `publicar.py`
garante a mesma meta em todo `design.html` e `prototipo.html` publicado. Isso tira o site da busca
e nada mais: quem tem o link abre. Documento que precisa de sigilo fica no repositório do projeto
e não vem para cá.

## Publicar

```bash
python3 scripts/publicar.py --projeto <kebab> --projeto-nome "<Nome>" --slug <kebab> \
  --titulo "<Título>" --spec <design.html> --prototipo <prototipo.html> --issue <url> --nota "<uma linha>"
git add site && git commit -m "Publica <slug> de <projeto>" && git push
```

- **O push na `main` publica.** O workflow `pages.yml` confere travessão na home e no manifest e
  sobe `site/` pelo `actions/deploy-pages`, sem segredo. Acompanhe com `gh run watch`.
- **`site/manifest.js` é a fonte da home.** Arquivo em `site/` sem entrada no manifest vai ao ar e
  fica invisível. Não editar `index.html` para listar documento.
- **Estrutura fixa:** `site/<projeto>/<slug>/design.html` e `prototipo.html`. Rodar de novo com só
  `--spec` preenche o slot e mantém o protótipo. `site/brandbook/` é a exceção, fixa na home.
- **Links internos são relativos:** o site vive em `/dent2dent-docs/`, então `/x` sem o prefixo
  aponta para fora dele.

## Testes

```bash
python3 -m unittest discover -s tests
```

O teste do `publicar.py` roda numa cópia temporária e não deixa projeto de exemplo em `site/`.

## Pages

- **Fonte do Pages é "GitHub Actions"** (Settings, Pages). O ambiente `github-pages` só publica
  da branch padrão: o workflow numa branch de trabalho não faz deploy.
- **Repositório público no plano Free:** é o que permite Pages sem plano pago, e é por isso que
  nada sigiloso entra aqui.

## Marca

Dent2Dent, não HyperionTech: Inter e mono do sistema, ink `#1d1d1f`, azul `#2563eb` e
`#1d4ed8`, surface `#f5f5f7`. Logotipo em texto "D2D" com o "2" em azul. Os tokens vivem no
`:root` do `site/index.html`.

## Nunca travessão

Travessão (U+2014) e traço (U+2013) são proibidos em qualquer texto daqui. O workflow reprova
a home e o manifest que os tiverem.
