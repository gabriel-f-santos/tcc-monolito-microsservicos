# Relatorio de Metricas de Qualidade e Acoplamento

Gerado por `scripts/measure_quality.py`. Ferramentas: `radon` (raw/cc/mi/hal), `xenon`, `cohesion`, `grimp`.

## 1. Tamanho e complexidade

| Codebase | Arq | LOC | SLOC | Blocos | CC medio | MI medio | Xenon |
|----------|-----|-----|------|--------|----------|----------|-------|
| Monolito DDD | DDD | 2316 | 1821 | 228 | 1.84 | 90.28 | PASS |
| Monolito MVC | MVC | 622 | 466 | 43 | 1.86 | 75.04 | PASS |
| Microsservico Auth (DDD) | DDD | 465 | 344 | 62 | 1.73 | 93.25 | PASS |
| Microsservico Catalogo (DDD) | DDD | 839 | 676 | 94 | 2.31 | 81.89 | FAIL |
| Microsservico Estoque (DDD) | DDD | 847 | 685 | 83 | 2.22 | 87.28 | PASS |
| Microsservico Auth (MVC) | MVC | 135 | 103 | 10 | 2.50 | 88.66 | PASS |
| Microsservico Catalogo (MVC) | MVC | 322 | 240 | 20 | 3.90 | 83.13 | PASS |
| Microsservico Estoque (MVC) | MVC | 331 | 257 | 22 | 2.82 | 80.54 | PASS |

- **LOC/SLOC**: lines of code / source lines (sem comentarios/brancos)
- **Blocos**: classes + funcoes + metodos analisados
- **CC medio**: A=1-5 (simples), B=6-10, C=11-20, D=21-30, E=31-40, F>40
- **MI medio**: 100=max; >85 bom, 65-85 medio, <65 ruim
- **Xenon**: PASS = CC max C + modulos max B + media A

## 2. Coesao de classes (cohesion / LCOM invertido)

| Codebase | Arq | Classes | Coesao media (%) |
|----------|-----|---------|------------------|
| Monolito DDD | DDD | 87 | 32.29 |
| Monolito MVC | MVC | 0 | 0.00 |
| Microsservico Auth (DDD) | DDD | 18 | 28.24 |
| Microsservico Catalogo (DDD) | DDD | 28 | 48.87 |
| Microsservico Estoque (DDD) | DDD | 21 | 39.15 |
| Microsservico Auth (MVC) | MVC | 0 | 0.00 |
| Microsservico Catalogo (MVC) | MVC | 0 | 0.00 |
| Microsservico Estoque (MVC) | MVC | 0 | 0.00 |

Valores mais altos = classes com responsabilidade unica. MVC tende a ter 0 classes pois handlers sao funcoes.

## 3. Acoplamento entre pacotes (grimp)

| Codebase | Arq | Pacotes | Modulos | Instabilidade media |
|----------|-----|---------|---------|---------------------|
| Monolito DDD | DDD | 6 | 117 | 0.417 |
| Monolito MVC | MVC | 4 | 5 | 0.000 |
| Microsservico Auth (DDD) | DDD | 6 | 34 | 0.458 |
| Microsservico Catalogo (DDD) | DDD | 5 | 21 | 0.450 |
| Microsservico Estoque (DDD) | DDD | 5 | 35 | 0.450 |
| Microsservico Auth (MVC) | MVC | 1 | 5 | 0.000 |
| Microsservico Catalogo (MVC) | MVC | 1 | 4 | 0.000 |
| Microsservico Estoque (MVC) | MVC | 1 | 5 | 0.000 |

- **Pacotes** agrupados em 2 niveis (ex: `src.auth`, `src.catalogo`) — representam Bounded Contexts no DDD.
- **Ca** (afferent): quantos pacotes dependem desse. **Ce** (efferent): de quantos pacotes esse depende. **I = Ce/(Ca+Ce)**: 0=estavel, 1=instavel. Detalhes em `metrics/raw/<codebase>/coupling.json`.

### Detalhamento por pacote

**Monolito DDD**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `src.auth` | 1 | 1 | 0.5 | 26 |
| `src.catalogo` | 1 | 1 | 0.5 | 35 |
| `src.estoque` | 1 | 1 | 0.5 | 32 |
| `src.infrastructure` | 0 | 0 | 0.0 | 1 |
| `src.presentation` | 0 | 4 | 1.0 | 5 |
| `src.shared` | 4 | 0 | 0.0 | 17 |

**Monolito MVC**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `routes.auth` | 0 | 0 | 0.0 | 1 |
| `routes.categorias` | 0 | 0 | 0.0 | 1 |
| `routes.estoque` | 0 | 0 | 0.0 | 1 |
| `routes.produtos` | 0 | 0 | 0.0 | 1 |

**Microsservico Auth (DDD)**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `src.application` | 2 | 1 | 0.333 | 4 |
| `src.container` | 1 | 2 | 0.667 | 1 |
| `src.domain` | 3 | 1 | 0.25 | 10 |
| `src.handlers` | 0 | 3 | 1.0 | 4 |
| `src.infrastructure` | 1 | 1 | 0.5 | 6 |
| `src.shared` | 1 | 0 | 0.0 | 8 |

**Microsservico Catalogo (DDD)**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `src.application` | 1 | 1 | 0.5 | 3 |
| `src.domain` | 3 | 1 | 0.25 | 6 |
| `src.handlers` | 0 | 4 | 1.0 | 3 |
| `src.infrastructure` | 1 | 1 | 0.5 | 4 |
| `src.shared` | 2 | 0 | 0.0 | 4 |

**Microsservico Estoque (DDD)**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `src.application` | 1 | 1 | 0.5 | 7 |
| `src.domain` | 3 | 1 | 0.25 | 11 |
| `src.handlers` | 0 | 4 | 1.0 | 4 |
| `src.infrastructure` | 1 | 1 | 0.5 | 4 |
| `src.shared` | 2 | 0 | 0.0 | 8 |

**Microsservico Auth (MVC)**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `src.handlers` | 0 | 0 | 0.0 | 4 |

**Microsservico Catalogo (MVC)**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `src.handlers` | 0 | 0 | 0.0 | 3 |

**Microsservico Estoque (MVC)**

| Pacote | Ca | Ce | I | modulos |
|--------|----|----|---|---------|
| `src.handlers` | 0 | 0 | 0.0 | 4 |

## 4. Comparacoes DDD vs MVC

| Unidade | Metrica | DDD | MVC | Delta |
|---------|---------|-----|-----|-------|
| Monolito | SLOC | 1821 | 466 | +1355 |
| Monolito | CC medio | 1.84 | 1.86 | -0.02 |
| Monolito | MI medio | 90.28 | 75.04 | +15.24 |
| Monolito | Instab media | 0.417 | 0.000 | +0.417 |
| Auth MS | SLOC | 344 | 103 | +241 |
| Auth MS | CC medio | 1.73 | 2.50 | -0.77 |
| Auth MS | MI medio | 93.25 | 88.66 | +4.59 |
| Auth MS | Instab media | 0.458 | 0.000 | +0.458 |
| Catalogo MS | SLOC | 676 | 240 | +436 |
| Catalogo MS | CC medio | 2.31 | 3.90 | -1.59 |
| Catalogo MS | MI medio | 81.89 | 83.13 | -1.24 |
| Catalogo MS | Instab media | 0.450 | 0.000 | +0.450 |
| Estoque MS | SLOC | 685 | 257 | +428 |
| Estoque MS | CC medio | 2.22 | 2.82 | -0.60 |
| Estoque MS | MI medio | 87.28 | 80.54 | +6.74 |
| Estoque MS | Instab media | 0.450 | 0.000 | +0.450 |

## 5. Saidas brutas

Arquivos detalhados em `metrics/raw/<codebase>/`:
- `radon-raw.txt` — LOC/SLOC/comentarios
- `radon-cc.txt` — complexidade por funcao
- `radon-mi.txt` — MI por arquivo
- `radon-hal.txt` — metricas de Halstead
- `cohesion.txt` — LCOM por classe
- `coupling.json` — Ca/Ce/I por pacote (grimp)
- `xenon.txt` — gate de qualidade
