# Shadow Tools

Painel web e toolkit offline para diagnóstico, OSINT de fontes abertas e segurança defensiva.

> **Status:** scaffold inicial v0.1.0. Os cartões da interface indicam módulos planejados; eles ainda não executam consultas ou varreduras.

## Modos de uso

- **Online (Render):** interface Flask acessível pelo navegador. Não é um Kali remoto, não tem root Android e não deve executar comandos arbitrários enviados pelo navegador.
- **Offline (Kali NetHunter):** edição local planejada para ferramentas que precisam do ambiente Android/Kali, permissões locais ou execução no próprio dispositivo.

A ideia é compartilhar módulos Python seguros quando possível, mantendo adaptadores diferentes para web e terminal.

## Estrutura atual

```text
TOOLS/
├── app.py
├── requirements.txt
├── render.yaml
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── README.md
```

## Executar localmente

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

No Windows, ative o ambiente virtual com `.venv\\Scripts\\activate`.

## Deploy no Render

O repositório inclui `render.yaml`. No Render, crie um Blueprint e conecte este repositório. A configuração usa:

- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`
- Health check: `/health`

O serviço gratuito pode dormir após inatividade. O filesystem padrão do serviço é temporário; quando histórico/configurações forem implementados, usar banco de dados em vez de depender de arquivos locais.

## Módulos planejados

- DNS e informações técnicas de domínios administrados pelo usuário.
- Metadados técnicos de IPs públicos.
- Verificação de cabeçalhos HTTP e TLS em sites autorizados.
- Diagnóstico local de rede no NetHunter.
- Inventário de ferramentas disponíveis no ambiente local.

## Privacidade e uso responsável

- Não pesquisar, localizar, expor ou montar dossiês sobre pessoas por CPF, RG, telefone, endereço ou outros identificadores pessoais.
- Não coletar credenciais, dados privados ou informações obtidas por acesso não autorizado.
- Não enviar entradas do usuário a serviços externos sem informar claramente o destino e obter consentimento.
- Testes de rede e web devem ficar limitados a sistemas próprios ou com autorização explícita.
- A interface hospedada não deve aceitar comandos de shell arbitrários, execução remota de ferramentas ou elevação de privilégios.

## Desenvolvimento

A versão atual fornece somente o dashboard e o endpoint de saúde. Novos módulos devem ser implementados e testados antes de serem apresentados como funcionais.

## Licença

Ainda não definida.
