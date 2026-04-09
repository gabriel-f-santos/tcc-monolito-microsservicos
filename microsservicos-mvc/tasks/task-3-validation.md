# Task 3: Validacao Final e Comparacao

## Objetivo

Apos os 3 servicos implementados, validar que tudo funciona e coletar metricas de comparacao.

## Validacao

```bash
# Rodar testes de cada servico
cd microsservicos-mvc/auth-service && pytest -v
cd ../catalogo-service && pytest -v
cd ../estoque-service && pytest -v
```

## Metricas a coletar

### Comparacao MVC vs DDD na migracao

```bash
# Linhas por servico
for svc in auth-service catalogo-service estoque-service; do
  echo "=== $svc ==="
  echo "MVC:"
  find microsservicos-mvc/$svc/src -name "*.py" ! -name "__init__.py" -exec cat {} + | wc -l
  echo "DDD:"
  find microsservicos/$svc/src -name "*.py" ! -name "__init__.py" -exec cat {} + | wc -l
done
```

### Reuso: quanto do monolito-mvc foi reutilizado?

Como o MVC nao tem domain/application separados, o reuso deve ser ~0%.
Documentar:
- Quantas linhas foram copiadas sem alteracao
- Quantas linhas foram reescritas
- Comparar com DDD (95% reuso por linhas)

### Tabela final para o artigo

| Metrica | DDD → Microsservicos | MVC → Microsservicos |
|---------|---------------------|---------------------|
| Tempo migracao | 18min 08s | ? |
| Arquivos reutilizados | 34/58 (58%) | ?/? |
| Linhas reutilizadas | ~95% | ? |
| Testes passando | 34/34 | ?/? |
| CC media | A | ? |
