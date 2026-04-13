import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// --- Config ---
const AUTH_URL = __ENV.AUTH_URL || 'https://pqq4enk0xd.execute-api.us-east-1.amazonaws.com/Prod';
const CAT_URL  = __ENV.CAT_URL  || 'https://aoglrk7gth.execute-api.us-east-1.amazonaws.com/Prod';
const EST_URL  = __ENV.EST_URL  || 'https://o337i2maha.execute-api.us-east-1.amazonaws.com/Prod';

export const options = {
  stages: [
    { duration: '15s', target: 5 },
    { duration: '1m', target: 10 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<3000'],
  },
};

// Custom trends per endpoint
const loginLatency = new Trend('latency_login');
const registrarLatency = new Trend('latency_registrar');
const criarCategoriaLatency = new Trend('latency_criar_categoria');
const criarProdutoLatency = new Trend('latency_criar_produto');
const listarProdutosLatency = new Trend('latency_listar_produtos');
const entradaLatency = new Trend('latency_entrada');
const saidaLatency = new Trend('latency_saida');
const buscarEstoqueLatency = new Trend('latency_buscar_estoque');
const healthLatency = new Trend('latency_health');

const headers = { 'Content-Type': 'application/json' };

export default function () {
  const uid = `${__VU}-${__ITER}-${Date.now()}`;

  // Health (auth)
  let r = http.get(`${AUTH_URL}/health`);
  healthLatency.add(r.timings.duration);

  // Registrar
  r = http.post(`${AUTH_URL}/api/v1/auth/registrar`, JSON.stringify({
    nome: 'Load', email: `load-${uid}@test.com`, senha: 'senha12345',
  }), { headers });
  registrarLatency.add(r.timings.duration);
  check(r, { 'registrar 201': (r) => r.status === 201 });

  // Login
  r = http.post(`${AUTH_URL}/api/v1/auth/login`, JSON.stringify({
    email: `load-${uid}@test.com`, senha: 'senha12345',
  }), { headers });
  loginLatency.add(r.timings.duration);
  check(r, { 'login 200': (r) => r.status === 200 });

  const token = JSON.parse(r.body).access_token;
  const auth = { headers: { ...headers, Authorization: `Bearer ${token}` } };

  // Criar categoria
  r = http.post(`${CAT_URL}/api/v1/categorias`, JSON.stringify({
    nome: `Cat-${uid}`, descricao: 'loadtest',
  }), auth);
  criarCategoriaLatency.add(r.timings.duration);
  check(r, { 'categoria 201': (r) => r.status === 201 });
  const catId = JSON.parse(r.body).id;

  // Criar produto
  r = http.post(`${CAT_URL}/api/v1/produtos`, JSON.stringify({
    sku: `LT-${uid}`, nome: 'ProdLoad', preco: 10, categoria_id: catId,
  }), auth);
  criarProdutoLatency.add(r.timings.duration);
  check(r, { 'produto 201': (r) => r.status === 201 });
  const prodId = JSON.parse(r.body).id;

  // Listar produtos
  r = http.get(`${CAT_URL}/api/v1/produtos`, auth);
  listarProdutosLatency.add(r.timings.duration);

  // Buscar item estoque por produto
  r = http.get(`${EST_URL}/api/v1/estoque/produto/${prodId}`, auth);
  buscarEstoqueLatency.add(r.timings.duration);
  if (r.status !== 200) { sleep(0.5); return; }
  const itemId = JSON.parse(r.body).id;

  // Entrada
  r = http.post(`${EST_URL}/api/v1/estoque/${itemId}/entrada`, JSON.stringify({
    quantidade: 50,
  }), auth);
  entradaLatency.add(r.timings.duration);
  check(r, { 'entrada 201': (r) => r.status === 201 });

  // Saida
  r = http.post(`${EST_URL}/api/v1/estoque/${itemId}/saida`, JSON.stringify({
    quantidade: 20,
  }), auth);
  saidaLatency.add(r.timings.duration);
  check(r, { 'saida 201': (r) => r.status === 201 });

  sleep(0.5);
}
