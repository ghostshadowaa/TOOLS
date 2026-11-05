# Shadow Tools

**Painel web + toolkit offline para Kali NetHunter.**

Shadow Tools reúne consultas técnicas de infraestrutura pública, verificações defensivas de sites autorizados e inventário de ferramentas locais. O projeto tem dois modos independentes:

- **Online:** Flask + Gunicorn no Render, acessível pelo navegador.
- **Offline:** Python dentro do Kali NetHunter, para inventariar ferramentas instaladas no próprio ambiente.

> Render não é Kali remoto, não tem acesso ao Android/Termux e não fornece root do celular.

## Recursos disponíveis

### Painel online

- Login por token configurado no ambiente.
- Proteção CSRF, cookies HttpOnly/SameSite e cabeçalhos de segurança.
- Limites de consultas por IP e limite de tentativas de login.
- DNS: registros A, AAAA, MX, NS, TXT e CAA.
- IP Inspector: classificação técnica, DNS reverso e, opcionalmente, dados de alocação RDAP.
- HTTP/TLS: certificado HTTPS e cabeçalhos de segurança em domínios públicos autorizados.
- Verificação de endereços públicos antes de conectar; sem seguir redirecionamentos.
- A página separa consultas web das ferramentas disponíveis somente no NetHunter local.
- Endpoint de saúde em `/health`.
- Sem histórico persistente nesta versão.

### NetHunter offline

- Inventário de Nmap, Metasploit, SQLMap, Whois, Dig, cURL, Wget, TCPDump, Traceroute, IP, SS, Git e Python.
- Informações do ambiente e UID efetivo.
- Instalação explícita de uma lista permitida de ferramentas de diagnóstico.
- Metasploit e SQLMap são detectados se já estiverem instalados; não são instalados nem iniciados automaticamente.
- Nmap oferece descoberta de hosts e inventário TCP com detecção de versões dos 100 principais serviços, limitado a redes IPv4 privadas de até 256 endereços e com confirmação de autorização.

## Estrutura

```text
TOOLS/
├── app.py
├── core/                  # DNS, IP, validação e verificações web
├── shadowtools/           # consulta RDAP e validação auxiliar
├── offline.py             # menu local e instalador de pacotes permitidos
├── offline/
│   ├── main.py            # menu de inventário
│   └── tool_registry.py   # catálogo local de executáveis
├── templates/
├── static/
├── tests/
├── install.sh
├── requirements.txt
├── requirements-dev.txt
├── render.yaml
├── AGENTS.md
└── README.md
```

## Instalação no Kali NetHunter

Clone o repositório **dentro do Kali**:

```bash
git clone https://github.com/ghostshadowaa/TOOLS.git
cd TOOLS
bash install.sh
```

Depois, execute o menu local:

```bash
python3 offline.py
```

Para abrir diretamente o inventário por categorias:

```bash
python3 offline/main.py
```

O menu inclui descoberta de hosts e inventário TCP de serviços do Nmap. Ambos exigem rede IPv4 privada de até 256 endereços e confirmação de autorização; o inventário de serviços usa detecção de versão nos 100 principais serviços TCP. Não executa scripts NSE de vulnerabilidade.

O menu de instalação usa APT e pede confirmação antes de instalar a lista permitida. Se o APT informar falta de permissões, entre como root do ambiente NetHunter e execute novamente. **Root dentro do PRoot não equivale a root real do Android.**

## Executar o painel localmente

Requer Python 3.10 ou superior.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export APP_SECRET_KEY="use-um-segredo-longo-e-aleatorio"
export DASHBOARD_TOKEN="defina-um-token-forte"
export COOKIE_SECURE=0
python app.py
```

Abra `http://127.0.0.1:5000`.

## Deploy no Render

1. Crie um Blueprint no Render e conecte este repositório.
2. O `render.yaml` configura build, Gunicorn, variáveis secretas e `/health`.
3. Abra **Environment** no serviço e consulte o valor de `DASHBOARD_TOKEN` gerado pelo Render. Use esse valor para entrar no painel.
4. Mantenha `APP_SECRET_KEY` e `DASHBOARD_TOKEN` privados. Nunca os coloque no código ou no GitHub.
5. A configuração de produção ativa cookies Secure.

O serviço gratuito pode suspender-se após inatividade. O disco padrão é efêmero; não use arquivos locais para guardar histórico ou dados importantes. Ainda não há banco de dados configurado.

## API autenticada

Todas as rotas de consulta exigem sessão autenticada e token CSRF:

- `POST /api/dns` — JSON: `{"domain":"example.com"}`
- `POST /api/ip` — JSON: `{"ip":"1.1.1.1","rdap":false}`
- `POST /api/web-check` — JSON: `{"domain":"example.com"}`

O RDAP é opcional. Quando marcado no painel, o IP público consultado é enviado ao serviço externo `rdap.org`; contatos e dados pessoais são omitidos da resposta.

## Privacidade e limites

- DNS usa o resolvedor configurado no ambiente servidor.
- A verificação web conecta somente a IPs públicos validados, usa HTTPS na porta 443 e não segue redirecionamentos.
- A consulta RDAP só ocorre após seleção explícita no painel.
- Não há busca de pessoas por CPF, RG, telefone, endereço, nome, e-mail ou username; não há dossiês pessoais, busca de credenciais ou enumeração de contas.
- Verifique somente sistemas próprios ou com autorização explícita.
- O painel web não executa comandos de shell nem ferramentas locais do NetHunter.
- Entradas não são gravadas em histórico nesta versão.

## Testes

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

O GitHub Actions executa os testes e a verificação de sintaxe a cada push e pull request.

## Licença

Ainda não definida.
