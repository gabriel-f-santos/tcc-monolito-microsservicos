#!/usr/bin/env python3
"""Medicao de qualidade e acoplamento para os 8 codebases do TCC.

Roda:
  - radon raw|cc|mi|hal  -> LOC, CC, MI, Halstead
  - xenon                -> gate de qualidade (informativo)
  - cohesion             -> LCOM por classe
  - grimp                -> Ca/Ce/I por pacote

Saidas:
  - metrics/raw/<codebase>/*.txt + coupling.json
  - docs/metrics-report.md
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_BIN = ROOT / ".venv-metrics" / "bin"
RAW_DIR = ROOT / "metrics" / "raw"
REPORT = ROOT / "docs" / "metrics-report.md"


@dataclass
class Codebase:
    name: str           # nome curto (monolito-ddd, auth-ms-ddd, ...)
    label: str          # label legivel
    arch: str           # DDD | MVC
    kind: str           # monolito | microsservico
    root: Path          # diretorio que contem o codigo (cwd pra grimp)
    src_paths: list[str]  # paths relativos dentro de root pra radon/cohesion
    grimp_package: str | None  # nome do pacote pra grimp (ou None se nao da)


CODEBASES: list[Codebase] = [
    Codebase("monolito-ddd", "Monolito DDD", "DDD", "monolito",
             ROOT / "monolito", ["src"], "src"),
    Codebase("monolito-mvc", "Monolito MVC", "MVC", "monolito",
             ROOT / "monolito-mvc",
             ["routes", "models.py", "app.py", "database.py", "schemas.py"],
             "routes"),
    Codebase("auth-ms-ddd", "Microsservico Auth (DDD)", "DDD", "microsservico",
             ROOT / "microsservicos" / "auth-service", ["src"], "src"),
    Codebase("catalogo-ms-ddd", "Microsservico Catalogo (DDD)", "DDD", "microsservico",
             ROOT / "microsservicos" / "catalogo-service", ["src"], "src"),
    Codebase("estoque-ms-ddd", "Microsservico Estoque (DDD)", "DDD", "microsservico",
             ROOT / "microsservicos" / "estoque-service", ["src"], "src"),
    Codebase("auth-ms-mvc", "Microsservico Auth (MVC)", "MVC", "microsservico",
             ROOT / "microsservicos" / "auth-service-mvc", ["src"], "src"),
    Codebase("catalogo-ms-mvc", "Microsservico Catalogo (MVC)", "MVC", "microsservico",
             ROOT / "microsservicos" / "catalogo-service-mvc", ["src"], "src"),
    Codebase("estoque-ms-mvc", "Microsservico Estoque (MVC)", "MVC", "microsservico",
             ROOT / "microsservicos" / "estoque-service-mvc", ["src"], "src"),
]


def sh(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Roda comando, retorna (returncode, stdout+stderr)."""
    try:
        r = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=120
        )
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 1, "TIMEOUT"
    except FileNotFoundError as e:
        return 1, f"NOT FOUND: {e}"


# ------------ parsers -------------


def parse_radon_raw(text: str) -> dict:
    """Extrai totais do 'radon raw -s'."""
    out = {}
    in_total = False
    for line in text.splitlines():
        if "** Total **" in line:
            in_total = True
            continue
        if in_total:
            m = re.match(r"\s*(LOC|LLOC|SLOC|Comments|Single comments|Multi|Blank):\s*(\d+)", line)
            if m:
                out[m.group(1).lower().replace(" ", "_")] = int(m.group(2))
    return out


def parse_radon_cc(text: str) -> dict:
    """Extrai blocos totais e complexidade media."""
    out = {"blocks": 0, "avg_cc": 0.0}
    m = re.search(r"(\d+)\s+blocks\s+\(.*\)\s+analyzed\.", text)
    if m:
        out["blocks"] = int(m.group(1))
    m = re.search(r"Average complexity:\s+[A-F]\s+\(([\d.]+)\)", text)
    if m:
        out["avg_cc"] = float(m.group(1))
    return out


def parse_radon_mi(text: str) -> dict:
    """Calcula MI medio dos arquivos listados."""
    scores = []
    for line in text.splitlines():
        m = re.search(r"-\s+[A-F]\s+\(([\d.]+)\)", line)
        if m:
            scores.append(float(m.group(1)))
    return {
        "mi_avg": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "files": len(scores),
    }


def parse_cohesion(text: str) -> dict:
    """Extrai porcentagens 'Total: X%' por classe."""
    totals = [float(m.group(1)) for m in re.finditer(r"Total:\s+([\d.]+)%", text)]
    return {
        "classes": len(totals),
        "cohesion_avg": round(sum(totals) / len(totals), 2) if totals else 0.0,
    }


# ------------ grimp -------------


def compute_coupling(cb: Codebase) -> dict:
    """Ca/Ce/I por pacote de 2 niveis (ex: src.auth.domain)."""
    if cb.grimp_package is None:
        return {"error": "grimp_package nao definido"}
    sys.path.insert(0, str(cb.root))
    try:
        import importlib
        import grimp
        grimp = importlib.reload(grimp)
        graph = grimp.build_graph(cb.grimp_package, include_external_packages=False)
    except Exception as e:
        return {"error": f"build_graph falhou: {e}"}
    finally:
        if str(cb.root) in sys.path:
            sys.path.remove(str(cb.root))

    modules = [
        m for m in graph.modules
        if (m.startswith(cb.grimp_package + ".") or m == cb.grimp_package)
        and "__pycache__" not in m
    ]
    # Agrupa por 2 niveis (ex: src.auth) — nivel do bounded context
    def pkg_of(m: str) -> str:
        parts = m.split(".")
        return ".".join(parts[:2]) if len(parts) >= 2 else m

    packages = sorted({pkg_of(m) for m in modules if m != cb.grimp_package})

    rows = []
    total_ca = total_ce = 0
    for p in packages:
        p_mods = [m for m in modules if pkg_of(m) == p]
        efferent: set[str] = set()   # pacotes QUE esse pacote importa
        afferent: set[str] = set()   # pacotes QUE importam esse pacote
        for m in p_mods:
            for imported in graph.find_modules_directly_imported_by(m):
                other = pkg_of(imported)
                if other != p and other in packages:
                    efferent.add(other)
            for importer in graph.find_modules_that_directly_import(m):
                other = pkg_of(importer)
                if other != p and other in packages:
                    afferent.add(other)
        ca = len(afferent)
        ce = len(efferent)
        inst = round(ce / (ca + ce), 3) if (ca + ce) > 0 else 0.0
        rows.append({"package": p, "Ca": ca, "Ce": ce, "I": inst, "modules": len(p_mods)})
        total_ca += ca
        total_ce += ce

    return {
        "packages": rows,
        "total_modules": len(modules),
        "total_packages": len(packages),
        "avg_instability": round(
            sum(r["I"] for r in rows) / len(rows), 3) if rows else 0.0,
    }


# ------------ pipeline por codebase -------------


def measure(cb: Codebase) -> dict:
    print(f"[*] {cb.name}")
    out_dir = RAW_DIR / cb.name
    out_dir.mkdir(parents=True, exist_ok=True)
    src_paths = [str(cb.root / p) for p in cb.src_paths if (cb.root / p).exists()]
    if not src_paths:
        print(f"    SKIP: nenhum src existe em {cb.root}")
        return {"error": "src nao existe"}

    metrics: dict = {"codebase": cb.name, "label": cb.label, "arch": cb.arch, "kind": cb.kind}

    # radon raw
    rc, text = sh([str(VENV_BIN / "radon"), "raw", "-s", *src_paths])
    (out_dir / "radon-raw.txt").write_text(text)
    metrics["raw"] = parse_radon_raw(text)

    # radon cc
    rc, text = sh([str(VENV_BIN / "radon"), "cc", "-s", "-a", *src_paths])
    (out_dir / "radon-cc.txt").write_text(text)
    metrics["cc"] = parse_radon_cc(text)

    # radon mi
    rc, text = sh([str(VENV_BIN / "radon"), "mi", "-s", *src_paths])
    (out_dir / "radon-mi.txt").write_text(text)
    metrics["mi"] = parse_radon_mi(text)

    # radon hal
    rc, text = sh([str(VENV_BIN / "radon"), "hal", *src_paths])
    (out_dir / "radon-hal.txt").write_text(text)

    # xenon (informativo)
    rc, text = sh([
        str(VENV_BIN / "xenon"), "--max-absolute", "C",
        "--max-modules", "B", "--max-average", "A", *src_paths,
    ])
    (out_dir / "xenon.txt").write_text(f"exit={rc}\n{text}")
    metrics["xenon_pass"] = (rc == 0)

    # cohesion — nao aceita arquivos individuais, so diretorio
    coh_text = ""
    for p in src_paths:
        if Path(p).is_dir():
            rc, t = sh([str(VENV_BIN / "cohesion"), "-d", p])
            coh_text += t
    (out_dir / "cohesion.txt").write_text(coh_text)
    metrics["cohesion"] = parse_cohesion(coh_text)

    # grimp (acoplamento)
    coupling = compute_coupling(cb)
    (out_dir / "coupling.json").write_text(json.dumps(coupling, indent=2))
    metrics["coupling"] = coupling

    return metrics


# ------------ relatorio -------------


def fmt_int(v) -> str:
    return str(v) if v is not None else "—"


def fmt_float(v, n=2) -> str:
    try:
        return f"{float(v):.{n}f}"
    except Exception:
        return "—"


def render_report(results: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Relatorio de Metricas de Qualidade e Acoplamento\n")
    lines.append(
        "Gerado por `scripts/measure_quality.py`. Ferramentas: "
        "`radon` (raw/cc/mi/hal), `xenon`, `cohesion`, `grimp`.\n"
    )

    # Tabela 1 — Tamanho e complexidade
    lines.append("## 1. Tamanho e complexidade\n")
    lines.append("| Codebase | Arq | LOC | SLOC | Blocos | CC medio | MI medio | Xenon |")
    lines.append("|----------|-----|-----|------|--------|----------|----------|-------|")
    for r in results:
        raw = r.get("raw", {})
        cc = r.get("cc", {})
        mi = r.get("mi", {})
        lines.append(
            f"| {r['label']} | {r['arch']} "
            f"| {fmt_int(raw.get('loc'))} "
            f"| {fmt_int(raw.get('sloc'))} "
            f"| {fmt_int(cc.get('blocks'))} "
            f"| {fmt_float(cc.get('avg_cc'))} "
            f"| {fmt_float(mi.get('mi_avg'))} "
            f"| {'PASS' if r.get('xenon_pass') else 'FAIL'} |"
        )
    lines.append("")
    lines.append(
        "- **LOC/SLOC**: lines of code / source lines (sem comentarios/brancos)\n"
        "- **Blocos**: classes + funcoes + metodos analisados\n"
        "- **CC medio**: A=1-5 (simples), B=6-10, C=11-20, D=21-30, E=31-40, F>40\n"
        "- **MI medio**: 100=max; >85 bom, 65-85 medio, <65 ruim\n"
        "- **Xenon**: PASS = CC max C + modulos max B + media A\n"
    )

    # Tabela 2 — Coesao
    lines.append("## 2. Coesao de classes (cohesion / LCOM invertido)\n")
    lines.append("| Codebase | Arq | Classes | Coesao media (%) |")
    lines.append("|----------|-----|---------|------------------|")
    for r in results:
        coh = r.get("cohesion", {})
        lines.append(
            f"| {r['label']} | {r['arch']} "
            f"| {fmt_int(coh.get('classes'))} "
            f"| {fmt_float(coh.get('cohesion_avg'))} |"
        )
    lines.append("")
    lines.append("Valores mais altos = classes com responsabilidade unica. "
                 "MVC tende a ter 0 classes pois handlers sao funcoes.\n")

    # Tabela 3 — Acoplamento
    lines.append("## 3. Acoplamento entre pacotes (grimp)\n")
    lines.append("| Codebase | Arq | Pacotes | Modulos | Instabilidade media |")
    lines.append("|----------|-----|---------|---------|---------------------|")
    for r in results:
        cp = r.get("coupling", {})
        if "error" in cp:
            lines.append(f"| {r['label']} | {r['arch']} | ERRO | — | — |")
            continue
        lines.append(
            f"| {r['label']} | {r['arch']} "
            f"| {cp.get('total_packages')} "
            f"| {cp.get('total_modules')} "
            f"| {fmt_float(cp.get('avg_instability'), 3)} |"
        )
    lines.append("")
    lines.append(
        "- **Pacotes** agrupados em 2 niveis (ex: `src.auth`, `src.catalogo`) — "
        "representam Bounded Contexts no DDD.\n"
        "- **Ca** (afferent): quantos pacotes dependem desse. "
        "**Ce** (efferent): de quantos pacotes esse depende. "
        "**I = Ce/(Ca+Ce)**: 0=estavel, 1=instavel. "
        "Detalhes em `metrics/raw/<codebase>/coupling.json`.\n"
    )

    # Detalhes de acoplamento por pacote
    lines.append("### Detalhamento por pacote\n")
    for r in results:
        cp = r.get("coupling", {})
        if "error" in cp or not cp.get("packages"):
            continue
        lines.append(f"**{r['label']}**\n")
        lines.append("| Pacote | Ca | Ce | I | modulos |")
        lines.append("|--------|----|----|---|---------|")
        for p in cp["packages"]:
            lines.append(
                f"| `{p['package']}` | {p['Ca']} | {p['Ce']} "
                f"| {p['I']} | {p['modules']} |"
            )
        lines.append("")

    # Comparacoes-chave
    lines.append("## 4. Comparacoes DDD vs MVC\n")
    by_name = {r["codebase"]: r for r in results}

    def safe(d, *keys, default="—"):
        cur = d
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    pairs = [
        ("Monolito", "monolito-ddd", "monolito-mvc"),
        ("Auth MS", "auth-ms-ddd", "auth-ms-mvc"),
        ("Catalogo MS", "catalogo-ms-ddd", "catalogo-ms-mvc"),
        ("Estoque MS", "estoque-ms-ddd", "estoque-ms-mvc"),
    ]
    lines.append("| Unidade | Metrica | DDD | MVC | Delta |")
    lines.append("|---------|---------|-----|-----|-------|")
    for label, ddd_key, mvc_key in pairs:
        ddd = by_name.get(ddd_key, {})
        mvc = by_name.get(mvc_key, {})
        rows = [
            ("SLOC", safe(ddd, "raw", "sloc"), safe(mvc, "raw", "sloc"), 0),
            ("CC medio", safe(ddd, "cc", "avg_cc"), safe(mvc, "cc", "avg_cc"), 2),
            ("MI medio", safe(ddd, "mi", "mi_avg"), safe(mvc, "mi", "mi_avg"), 2),
            ("Instab media", safe(ddd, "coupling", "avg_instability"),
             safe(mvc, "coupling", "avg_instability"), 3),
        ]
        for metric, dv, mv, prec in rows:
            try:
                delta = f"{float(dv) - float(mv):+.{prec}f}"
                dv_s = f"{float(dv):.{prec}f}"
                mv_s = f"{float(mv):.{prec}f}"
            except Exception:
                delta = "—"
                dv_s, mv_s = str(dv), str(mv)
            lines.append(f"| {label} | {metric} | {dv_s} | {mv_s} | {delta} |")
    lines.append("")

    lines.append("## 5. Saidas brutas\n")
    lines.append("Arquivos detalhados em `metrics/raw/<codebase>/`:")
    lines.append("- `radon-raw.txt` — LOC/SLOC/comentarios")
    lines.append("- `radon-cc.txt` — complexidade por funcao")
    lines.append("- `radon-mi.txt` — MI por arquivo")
    lines.append("- `radon-hal.txt` — metricas de Halstead")
    lines.append("- `cohesion.txt` — LCOM por classe")
    lines.append("- `coupling.json` — Ca/Ce/I por pacote (grimp)")
    lines.append("- `xenon.txt` — gate de qualidade\n")

    return "\n".join(lines)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    results = [measure(cb) for cb in CODEBASES]

    # Salva consolidado JSON
    (RAW_DIR / "all-metrics.json").write_text(json.dumps(results, indent=2, default=str))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render_report(results))
    print(f"\n[OK] Relatorio: {REPORT}")
    print(f"[OK] Raw: {RAW_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
