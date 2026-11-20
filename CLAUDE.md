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

- **O push na `main` publica.** O workflow `pages.yml` confere travessão em todo `site/**/*.html` e no manifest, roda a suíte
  (`unittest discover`) e sobe `site/` pelo `actions/deploy-pages`, sem segredo. Acompanhe com `gh run watch`.
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

**O site no ar, dent2dent.com.br, vence qualquer documento.** A fonte dos tokens é
`site/brandbook/index.html`, e o `tests/test_brandbook.py` trava o que ele afirma. Mudou o site,
muda o brandbook e o teste no mesmo commit; os esqueletos de `site/brandbook/esqueletos/` e a
home herdam os mesmos tokens.

- **Cores:** ink `#1d1d1f`, azul `#2563eb` e `#1d4ed8`, surface `#f5f5f7`, mais os estados verde,
  âmbar e perigo. Linha é `--hair` (preto a 8%) e `--hair-strong` (14%); tinta de estado a 8%.
- **Raios:** `--r-xs` 6, `--r-sm` 10, `--r-md` 14, `--r-lg` 20, `--r-xl` 28 e a pílula `999px`
  para botão e chip. Raio literal fora disso reprova no teste.
- **Logo:** o PNG do site, por URL (`https://dent2dent.com.br/logo.png`), nunca copiado para cá.
  Em texto, `Dent2Dent` em Inter 500, 22px, com o "2" em azul. Os esqueletos usam a forma em texto.
- **Texto sobre tinta verde** vai em `--ink-2` e o verde só na borda: verde sobre a tinta dá 3,9
  de contraste.
- **Cópia fora daqui:** os dois esqueletos são recopiados para `plugins/dent2dent/shared/marca/`
  do repositório de skills. Mudou um, recopie.

## Nunca travessão

Travessão (U+2014) e traço (U+2013) são proibidos em qualquer texto daqui. O workflow reprova
todo `site/**/*.html` e o manifest que os tiverem.
