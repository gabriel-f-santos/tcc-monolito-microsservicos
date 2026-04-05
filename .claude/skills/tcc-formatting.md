---
name: tcc-formatting
description: Use when writing or editing TCC article sections in docs/tcc.md. Contains MBA USP/ESALQ formatting rules for sections, figures, tables, citations, and general structure. Max 30 pages.
---

# TCC Formatting Rules — MBA USP/ESALQ

## Overview

Rules for the TCC article in `docs/tcc.md`. Written in Markdown now, formatted in Word later. Embed formatting hints as HTML comments where relevant.

## Required Sections (in order, no numbering)

1. **Resumo** — single paragraph, covers all sections
2. **Palavras-chave** — up to 5, different from title words, separated by semicolons
3. *Abstract + Keywords (optional, English/Spanish)*
4. **Introducao** — MAX 2 PAGES, no subtopics, no figures, no tables. Literature review goes here.
5. **Material e Metodos** — subtopics allowed (bold, 1.25cm indent in Word)
6. **Resultados e Discussao** — subtopics allowed
7. **Conclusao** — concise, no figures, no tables
8. *Agradecimento (optional, max 3 lines)*
9. **Referencias** — alphabetical, only cited works

## Citation Rules

- **Indirect only** (paraphrase, never copy directly)
- **No apud** — always cite original source
- Up to 2 authors: "Sobrenome1 e Sobrenome2 (ano)"
- 3+ authors: "Sobrenome1 et al. (ano)"
- Capital letter only on first letter of surnames
- Acronyms: first occurrence "por extenso [SIGLA]", then just SIGLA
- Foreign expressions in "quotes" (Latin in *italics*)

## Figure Format (in Markdown)

```markdown
<!-- Ao passar para Word: titulo ABAIXO da figura, sem ponto final -->
![Descricao](path/to/image.png)
Figura X. Descricao sem ponto final
Fonte: Dados originais da pesquisa
```

## Table Format (in Markdown)

```markdown
<!-- Ao passar para Word: titulo ACIMA da tabela, sem ponto final -->
Tabela X. Descricao sem ponto final

| Col1 | Col2 | Col3 |
|------|------|------|
| dado | dado | dado |

Fonte: Resultados originais da pesquisa
```

## Reference Format

- Periodical: `Autor(es). Ano. Titulo. Nome da revista volume(edicao): paginas.`
- Book: `Autor(es). Ano. Titulo. Edicao. Editora, Cidade, Estado, Pais.`

## Word Formatting Hints (leave as comments)

- Font: Arial 11 (body), Arial 9 (footnotes, author addresses)
- Margins: 2.5cm all sides
- Line spacing: 1.5 (body), single (resumo, tables, figure captions)
- Section titles: bold, left-aligned, no indent, no numbering
- Subtitles: bold, 1.25cm first-line indent
- Max 30 pages including appendices
