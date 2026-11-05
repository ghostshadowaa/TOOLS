# Shadow Tools

**Painel web + toolkit offline para Kali NetHunter.**

Shadow Tools reúne consultas técnicas de infraestrutura pública, verificações defensivas de sites autorizados e inventário de ferramentas locais. O projeto possui dois modos independentes:

- **Online:** Flask + Gunicorn no Render, acessível pelo navegador.
- **Offline:** Python dentro do Kali NetHunter, para inventariar ferramentas instaladas no próprio ambiente.

> Render não é Kali remoto, não tem acesso ao Android/Termux e não fornece root do celular.

## Recursos disponíveis

### Painel online

- Login por token configurado no ambiente.
- Proteção CSRF, cookies HttpOnly/SameSite e cabeçalhos de segurança.
- Limites de consultas por IP.
- Consulta DNS de registros A, AAAA, MX, NS e TXT.
- Inspeção de IP: classificação técnica, DNS reverso e dados de alocação RDAP para IPs públicos.
- Verificação HTTPS/TLS e cabeçalhos de segurança em domínios públicos autorizados.
- Endpoint de saúde em /health.
- Sem histórico persistente das consultas nesta versão.

### NetHunter offline

- Inventário de Nmap, Metasploit, SQLMap, Whois, Dig, cURL, Wget, TCPDump, Traceroute, IP, SS, Git e Python.
- Informações do ambiente e UID efetivo.
- Instalação explícita de uma lista permitida de ferramentas de diagnóstico.
- Metasploit e SQLMap são detectados se já estiverem instalados; não são instalados ou iniciados automaticamente.

## Estrutura

```text
TOOLS/
├── app.py
├── core/                 # validação e verificações seguras
├── shadowtools/          # consultas técnicas e validação
├── offline.py            # menu local e instalador
├── offline/
│   ├── main.py
│   └── tool_registry.py
├── templates/
├── static/
├── tests/
├── install.sh
├── requirements.txt
├── render.yaml
├── AGENTS.md
└── README.md
```

## Instalação no Kali NetHunter

Clone o repositório dentro do Kali:

```bash
git clone https://github.com/ghostshadowaa/TOOLS.git
cd TOOLS
bash install.sh
python3 offline.py
```

O menu offline permite detectar ferramentas e instalar a lista permitida de ferramentas de diagnóstico. Se o APT informar falta de permissões, entre como usuário root do container NetHunter (por exemplo, nethunter -r no Termux host) e execute o instalador novamente. **Isso não concede root real ao Android:** root no PRoot é limitado ao container.

Menu alternativo de inventário:

```bash
python3 offline/main.py
```

## Executar o painel localmente

Requer Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export APP_SECRET_KEY="troque-por-um-segredo-longo"
export DASHBOARD_TOKEN="defina-um-token-forte"
export COOKIE_SECURE=0
python app.py
```

Abra http://127.0.0.1:5000.

## Deploy no Render

1. Crie um Blueprint no Render e conecte este repositório.
2. O render.yaml configura build, Gunicorn, variáveis secretas e /health.
3. Copie o valor de DASHBOARD_TOKEN das Environment Variables do serviço para entrar no painel.
4. Mantenha APP_SECRET_KEY e DASHBOARD_TOKEN privados. Nunca os coloque no código ou no GitHub.
5. A configuração de produção ativa cookies Secure.

O serviço gratuito pode suspender-se após inatividade. O disco padrão é efêmero; não use arquivos locais para guardar histórico ou dados importantes. Ainda não há banco de dados configurado.

## API autenticada

Todas as rotas exigem login, sessão e token CSRF:

- POST /api/dns — JSON: {"domain":"example.com"}
- POST /api/ip — JSON: {"ip":"1.1.1.1"}
- POST /api/web-check — JSON: {"domain":"example.com"}

## Privacidade e limites

- Consultas RDAP enviam o IP público consultado ao serviço rdap.org. Contatos e dados pessoais não são incluídos no resultado.
- DNS usa o resolvedor configurado no ambiente servidor.
- A verificação web conecta somente a IPs públicos validados, usa HTTPS na porta 443 e não segue redirecionamentos.
- Não há busca de pessoas por CPF, RG, telefone, endereço, nome, e-mail ou username; não há dossiês pessoais, busca de credenciais ou enumeração de contas.
- Verifique somente sistemas próprios ou com autorização explícita.
- O painel web não executa comandos de shell nem ferramentas locais do NetHunter.
- Entradas não são gravadas em histórico nesta versão.

## Testes

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Licença

MIT. Consulte LICENSE.
