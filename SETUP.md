<a id="en"></a>
**English** · [Português](#pt)

# Setup — AW Client Report Portal

Get the portal running on your machine in about **5 minutes**, then click through the full
demo (auto-fill → generate → distribute). Everything runs locally — nothing is deployed and
no real accounts are touched.

---

## Prerequisites

- **Python 3.10+** — check with `python --version` (macOS/Linux: `python3 --version`)
- **Git** — to clone the repo
- ~200 MB of disk space

---

## 1 · Get the code

```bash
git clone https://github.com/bhengubv/sagan-aw-client-portal.git
cd sagan-aw-client-portal
```

## 2 · Create a virtual environment & install

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

> From here on, `PY` means your venv Python:
> Windows → `.\.venv\Scripts\python.exe` · macOS/Linux → `.venv/bin/python`

## 3 · Seed the demo data

```bash
PY seed.py
```
Creates two demo firms, seven connected providers, and a fully linked demo client.

## 4 · Start the two servers (two terminals)

**Terminal 1 — the provider sandbox** (powers the live auto-fill):
```bash
PY run_sandbox.py        # http://127.0.0.1:5050
```

**Terminal 2 — the portal**:
```bash
PY run.py                # http://127.0.0.1:5000
```

## 5 · Open it and sign in

Go to **http://127.0.0.1:5000** and sign in:

| Login | Password | Role |
|---|---|---|
| `owner@firm.test` | `changeme123` | Owner (full access) |
| `planner@firm.test` | `changeme123` | Planner |
| `assistant@firm.test` | `changeme123` | Assistant |
| `superadmin@firm.test` | `changeme123` | Platform admin (Admin console) |
| `northwind@firm.test` | `changeme123` | A second firm |

New firms can also self-register at **`/signup`**.

## 6 · Try the full flow

1. Open **The Sample Household** → click **Generate report**.
2. Watch the form **auto-fill ~9 balances** from the connected providers (each tagged with its source).
3. Fill the one remaining field (the mortgage balance) → **Generate report**.
4. **Download** the SACS & TCC PDFs, **email** them, or **save to Dropbox**.
5. Check **Billing** for metered usage, and sign in as `superadmin@firm.test` for the **Admin** console.

---

## Running the tests

The test suite is installed already — just run it:
```bash
PY -m pytest             # 104 tests, ~40s
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Auto-fill comes up empty | The **sandbox (:5050) isn't running** — start `PY run_sandbox.py` in its own terminal. |
| "Address already in use" / port busy | Something else is on `5000`/`5050`. Stop it, or change the port in `run.py` / `run_sandbox.py`. |
| Want a clean demo again | Delete `instance/aw_portal.db`, then re-run `PY seed.py`. |
| `pip install` SSL/permission errors | Make sure the venv is activated/used (`PY`), and you're on Python 3.10+. |

---

## Going live (production)

Local is a **demo** backed by a provider sandbox. To deploy it and connect **real** bank/custodian
accounts, follow the implementation docs:

- **[docs/IMPLEMENTATION_HANDOFF.md](docs/IMPLEMENTATION_HANDOFF.md)** — start here
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — hosting, Postgres, secrets, scheduled jobs
- **[docs/PROVIDERS.md](docs/PROVIDERS.md)** — connect each real provider (credentials, OAuth)
- **[docs/OPERATIONS.md](docs/OPERATIONS.md)** — day-to-day runbook

<br>

---

<br>

<a id="pt"></a>
[English](#en) · **Português**

# Configuração — AW Client Report Portal

Coloque o portal para rodar no seu computador em cerca de **5 minutos** e percorra a
demonstração completa (preenchimento automático → gerar → distribuir). Tudo roda localmente —
nada é implantado e nenhuma conta real é acessada.

---

## Pré-requisitos

- **Python 3.10+** — verifique com `python --version` (macOS/Linux: `python3 --version`)
- **Git** — para clonar o repositório
- ~200 MB de espaço em disco

---

## 1 · Baixe o código

```bash
git clone https://github.com/bhengubv/sagan-aw-client-portal.git
cd sagan-aw-client-portal
```

## 2 · Crie um ambiente virtual e instale

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

> Daqui em diante, `PY` significa o Python do seu venv:
> Windows → `.\.venv\Scripts\python.exe` · macOS/Linux → `.venv/bin/python`

## 3 · Carregue os dados de demonstração

```bash
PY seed.py
```
Cria duas empresas de demonstração, sete provedores conectados e um cliente totalmente vinculado.

## 4 · Inicie os dois servidores (dois terminais)

**Terminal 1 — o sandbox de provedores** (alimenta o preenchimento automático):
```bash
PY run_sandbox.py        # http://127.0.0.1:5050
```

**Terminal 2 — o portal**:
```bash
PY run.py                # http://127.0.0.1:5000
```

## 5 · Abra e faça login

Acesse **http://127.0.0.1:5000** e faça login:

| Login | Senha | Função |
|---|---|---|
| `owner@firm.test` | `changeme123` | Proprietário (acesso total) |
| `planner@firm.test` | `changeme123` | Planejador |
| `assistant@firm.test` | `changeme123` | Assistente |
| `superadmin@firm.test` | `changeme123` | Administrador da plataforma (console Admin) |
| `northwind@firm.test` | `changeme123` | Uma segunda empresa |

Novas empresas também podem se cadastrar em **`/signup`**.

## 6 · Experimente o fluxo completo

1. Abra **The Sample Household** → clique em **Gerar relatório**.
2. Veja o formulário **preencher ~9 saldos** automaticamente pelos provedores conectados (cada um marcado com sua origem).
3. Preencha o único campo restante (o saldo da hipoteca) → **Gerar relatório**.
4. **Baixe** os PDFs SACS e TCC, **envie por e-mail** ou **salve no Dropbox**.
5. Veja o uso medido em **Faturamento** e faça login como `superadmin@firm.test` para o console **Admin**.

---

## Rodando os testes

A suíte de testes já está instalada — é só rodar:
```bash
PY -m pytest             # 104 testes, ~40s
```

## Solução de problemas

| Sintoma | Solução |
|---|---|
| O preenchimento automático vem vazio | O **sandbox (:5050) não está rodando** — inicie `PY run_sandbox.py` em um terminal próprio. |
| "Address already in use" / porta ocupada | Algo já está usando `5000`/`5050`. Pare esse processo ou mude a porta em `run.py` / `run_sandbox.py`. |
| Quer uma demonstração limpa de novo | Apague `instance/aw_portal.db` e rode `PY seed.py` novamente. |
| Erros de SSL/permissão no `pip install` | Garanta que o venv está sendo usado (`PY`) e que você está no Python 3.10+. |

---

## Colocando em produção

Localmente é uma **demonstração** apoiada por um sandbox de provedores. Para implantar e conectar
contas **reais** de bancos/custodiantes, siga os documentos de implementação:

- **[docs/IMPLEMENTATION_HANDOFF.md](docs/IMPLEMENTATION_HANDOFF.md)** — comece por aqui
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — hospedagem, Postgres, segredos, tarefas agendadas
- **[docs/PROVIDERS.md](docs/PROVIDERS.md)** — conecte cada provedor real (credenciais, OAuth)
- **[docs/OPERATIONS.md](docs/OPERATIONS.md)** — manual do dia a dia
