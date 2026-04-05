---
name: metrics-collection
description: Use when collecting, recording, or analyzing project metrics — radon output, k6 results, AI development time, or cost data. Standardizes how measurements are captured and stored.
---

# Metrics Collection Standard

## Overview

Standardized process for collecting and recording metrics across four dimensions: code quality, performance, cost, and AI productivity.

## Code Quality (radon)

**Run after every feature implementation:**

```bash
# Cyclomatic complexity per function (grade A-F)
radon cc src/ -s -a -j > metrics/cc-{feature}-{arch}-{timestamp}.json

# Maintainability index per file (0-100)
radon mi src/ -s -j > metrics/mi-{feature}-{arch}-{timestamp}.json

# Xenon threshold check (fail if above B)
xenon src/ -b B -m A -a A
```

**Record in planilha:**
- CC average before/after feature
- MI average before/after feature
- Any function with grade C or worse (flag for discussion)

## Performance (k6)

**Three standard scenarios:**

```bash
# Constant load
k6 run --out json=metrics/k6-constant-{arch}.json scenarios/constant.js

# Burst
k6 run --out json=metrics/k6-burst-{arch}.json scenarios/burst.js

# Ramp
k6 run --out json=metrics/k6-ramp-{arch}.json scenarios/ramp.js
```

**Extract from results:** p50, p95, p99, throughput (req/s), error rate

**Cold start measurement:** First request after 15min idle, repeat 5 times, report median.

## AI Productivity

**For each feature x architecture x AI tool:**

1. Start timer when prompt is sent
2. Stop timer when all tests pass
3. Record:
   - Time (minutes)
   - Number of iterations (re-prompts until tests pass)
   - `git diff --stat` (lines added/removed)
   - CC before and after (radon)
   - MI before and after (radon)

**Naming convention:** `metrics/ai-{feature}-{arch}-{tool}-{timestamp}.md`

## Cost (AWS)

**After test execution:**
- Export billing from AWS Cost Explorer (filter by service)
- Record: Lambda invocations, DynamoDB R/W units, API Gateway requests, data transfer
- Project for 3 scenarios: low (100 req/day), medium (1000 req/day), high (10000 req/day)

## File Structure

```
metrics/
  cc-crud-produto-monolito-20260403.json
  mi-crud-produto-monolito-20260403.json
  k6-constant-monolito.json
  ai-crud-produto-monolito-claude-20260403.md
  aws-costs-20260410.csv
```
