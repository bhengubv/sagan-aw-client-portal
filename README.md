<a id="en"></a>
**English** · [Português](#pt)

# AW Client Report Portal
#### built by **Sagan**

# A full day of client-report prep — done in minutes. In your exact format.

Pull every balance from your banks and custodians **automatically**, let the system do **all the math**, and hand your client a polished **cash-flow** and **net-worth** report — with no Canva, no spreadsheets, no calculator, and no errors.

### ⏱️ A day → minutes  ·  ✅ Zero manual math  ·  🎯 Your templates, untouched  ·  🔒 Your data stays yours

---

## How it works

**1 · Open a client, hit *Generate* — the numbers fill themselves.**
The portal reaches into **Plaid, Schwab, RightCapital, Zillow and Pinnacle**, pulls the balances, and shows you **exactly where each number came from**. Anything it can't reach, it flags — so you never hunt for a figure again.

![Balances auto-filled from your connected providers, each tagged with its source](docs/img/autofill.png)

**2 · One click, and the math is done.**
Inflows, outflows, retirement, the trust, liabilities, net worth — **every total calculated and re-checked for you**.

![Report ready — every total computed, ready to download or send](docs/img/review.png)

**3 · Your reports, your format.**
Pixel-perfect **SACS** (cash-flow) and **TCC** (net-worth) PDFs — exactly the way Andrew built them. Download, email, or save to Dropbox.

| Cash-flow (SACS) | Net-worth (TCC) |
|:--:|:--:|
| ![SACS cash-flow report](docs/img/report-sacs.png) | ![TCC net-worth report](docs/img/report-tcc.png) |

---

# 🚀 Try it on your computer — in about 5 minutes

> You only need **Python** installed first (it's free — [download it here](https://www.python.org/downloads/), version 3.10 or newer). Then follow the steps below, copying each block into a terminal/PowerShell window.

### Step 1 — Get the files
**[⬇️ Download the ZIP](https://github.com/bhengubv/sagan-aw-client-portal/archive/refs/heads/main.zip)** and unzip it, then open a terminal **inside that folder**.
*(Prefer git? `git clone https://github.com/bhengubv/sagan-aw-client-portal.git` then `cd sagan-aw-client-portal`.)*

### Step 2 — Install it (one time)
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
**Mac / Linux:**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### Step 3 — Load the demo data
```powershell
.\.venv\Scripts\python.exe seed.py
```
*(Mac/Linux: `.venv/bin/python seed.py`)*

### Step 4 — Start it (two terminal windows, leave both open)
**Window 1** — the data service:
```powershell
.\.venv\Scripts\python.exe run_sandbox.py
```
**Window 2** — the portal:
```powershell
.\.venv\Scripts\python.exe run.py
```

### Step 5 — Open it
Go to **http://127.0.0.1:5000** in your browser and sign in:

| Email | Password |
|---|---|
| **owner@firm.test** | **changeme123** |

*(Other logins: `planner@firm.test`, `assistant@firm.test`, `superadmin@firm.test` for the admin view — all `changeme123`.)*

### Step 6 — See the magic
Open **The Sample Household → Generate report**. Watch the balances **fill in by themselves**, type the one remaining number, click **Generate**, and download your SACS & TCC reports. 🎉

> **Stuck?** Most common fix: if the balances don't auto-fill, make sure **Window 1 (`run_sandbox.py`) is still running**. Full troubleshooting → **[SETUP.md](SETUP.md)**.

---

## Why your team will love it

- **⏱️ A day becomes minutes.** Spend that time with clients, not in Canva.
- **✅ No more math errors.** Every figure is computed and cross-checked automatically.
- **🎯 Nothing changes for your clients.** Same reports, same format — just faster and flawless.
- **🔒 Secure by design.** Read-only access, your data stays yours, and **nothing is ever used to train an AI**.
- **📈 Grow without hiring.** Take on more clients without adding headcount.

## ▶️ See the 2-minute walkthrough

**[Watch the walkthrough](#)**  *(drop your Loom link here)*

---

## Under the hood

Built to the full Technical Specification — **all four phases, every element functional, 104 automated tests passing.**

- **Phase 1 — Portal core:** client management, the deterministic calculation engine, fixed-layout SACS & TCC PDFs, secure login with two-factor, audit log.
- **Phase 2 — Integrations:** an encrypted credential vault and read-only connectors for **Plaid, Schwab, RightCapital, Zillow, Pinnacle, PreciseFP** (+ Dropbox/Canva), with a built-in sandbox so it runs end-to-end before any real account is connected.
- **Phase 3 — AI & client-facing:** statement reading, anomaly flagging, automated client onboarding & reminders, an expense worksheet, and report distribution by email/Dropbox/Canva.
- **Phase 4 — Multi-firm platform:** self-serve sign-up, per-firm branding, usage billing, and an admin console.

**Run the tests:** `.\.venv\Scripts\python.exe -m pytest` (104 tests, ~40s).

### Going live (for the implementation team)

Local is a demo backed by a sandbox. To deploy it and connect **real** accounts, start with
**[docs/IMPLEMENTATION_HANDOFF.md](docs/IMPLEMENTATION_HANDOFF.md)** —
then [DEPLOYMENT.md](docs/DEPLOYMENT.md), [PROVIDERS.md](docs/PROVIDERS.md), and [OPERATIONS.md](docs/OPERATIONS.md).
Full local setup & troubleshooting is in **[SETUP.md](SETUP.md)**.

<br>

---

<br>

<a id="pt"></a>
[English](#en) · **Português**

# AW Client Report Portal
#### desenvolvido pela **Sagan**

# Um dia inteiro de preparação de relatórios — feito em minutos. No seu formato exato.

Importe todos os saldos dos seus bancos e custodiantes **automaticamente**, deixe o sistema fazer **todos os cálculos** e entregue ao seu cliente um relatório de **fluxo de caixa** e **patrimônio líquido** impecável — sem Canva, sem planilhas, sem calculadora e sem erros.

### ⏱️ Um dia → minutos  ·  ✅ Zero cálculo manual  ·  🎯 Seus modelos, intactos  ·  🔒 Seus dados continuam seus

---

## Como funciona

**1 · Abra um cliente e clique em *Gerar* — os números se preenchem sozinhos.**
O portal se conecta ao **Plaid, Schwab, RightCapital, Zillow e Pinnacle**, importa os saldos e mostra **exatamente de onde veio cada número**. O que ele não conseguir buscar, ele sinaliza — assim você nunca mais precisa caçar um valor.

![Saldos preenchidos automaticamente pelos provedores conectados, cada um marcado com sua origem](docs/img/autofill.png)

**2 · Um clique, e os cálculos estão prontos.**
Entradas, saídas, previdência, o trust, passivos, patrimônio líquido — **cada total calculado e conferido para você**.

![Relatório pronto — todos os totais calculados, prontos para baixar ou enviar](docs/img/review.png)

**3 · Seus relatórios, seu formato.**
PDFs **SACS** (fluxo de caixa) e **TCC** (patrimônio líquido) perfeitos — exatamente como o Andrew os criou. Baixe, envie por e-mail ou salve no Dropbox.

| Fluxo de caixa (SACS) | Patrimônio líquido (TCC) |
|:--:|:--:|
| ![Relatório de fluxo de caixa SACS](docs/img/report-sacs.png) | ![Relatório de patrimônio líquido TCC](docs/img/report-tcc.png) |

---

# 🚀 Experimente no seu computador — em cerca de 5 minutos

> Você só precisa ter o **Python** instalado primeiro (é gratuito — [baixe aqui](https://www.python.org/downloads/), versão 3.10 ou mais recente). Depois siga os passos abaixo, copiando cada bloco em uma janela do terminal/PowerShell.

### Passo 1 — Baixe os arquivos
**[⬇️ Baixe o ZIP](https://github.com/bhengubv/sagan-aw-client-portal/archive/refs/heads/main.zip)** e descompacte; depois abra um terminal **dentro dessa pasta**.
*(Prefere git? `git clone https://github.com/bhengubv/sagan-aw-client-portal.git` e depois `cd sagan-aw-client-portal`.)*

### Passo 2 — Instale (uma única vez)
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
**Mac / Linux:**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### Passo 3 — Carregue os dados de demonstração
```powershell
.\.venv\Scripts\python.exe seed.py
```
*(Mac/Linux: `.venv/bin/python seed.py`)*

### Passo 4 — Inicie (duas janelas de terminal, deixe as duas abertas)
**Janela 1** — o serviço de dados:
```powershell
.\.venv\Scripts\python.exe run_sandbox.py
```
**Janela 2** — o portal:
```powershell
.\.venv\Scripts\python.exe run.py
```

### Passo 5 — Abra
Acesse **http://127.0.0.1:5000** no seu navegador e faça login:

| E-mail | Senha |
|---|---|
| **owner@firm.test** | **changeme123** |

*(Outros logins: `planner@firm.test`, `assistant@firm.test`, `superadmin@firm.test` para a visão de administrador — todos `changeme123`.)*

### Passo 6 — Veja a mágica
Abra **The Sample Household → Gerar relatório**. Veja os saldos **se preencherem sozinhos**, digite o único número que falta, clique em **Gerar** e baixe seus relatórios SACS e TCC. 🎉

> **Travou?** Solução mais comum: se os saldos não preencherem automaticamente, verifique se a **Janela 1 (`run_sandbox.py`) ainda está rodando**. Solução de problemas completa → **[SETUP.md](SETUP.md)**.

---

## Por que sua equipe vai adorar

- **⏱️ Um dia vira minutos.** Use esse tempo com os clientes, não no Canva.
- **✅ Sem mais erros de cálculo.** Cada valor é calculado e conferido automaticamente.
- **🎯 Nada muda para seus clientes.** Os mesmos relatórios, o mesmo formato — só que mais rápido e impecável.
- **🔒 Seguro por design.** Acesso somente leitura, seus dados continuam seus e **nada é usado para treinar IA**.
- **📈 Cresça sem contratar.** Atenda mais clientes sem aumentar a equipe.

## ▶️ Veja a demonstração de 2 minutos

**[Assista à demonstração](#)**  *(coloque seu link do Loom aqui)*

---

## Por dentro

Desenvolvido conforme a Especificação Técnica completa — **todas as quatro fases, cada elemento funcional, 104 testes automatizados passando.**

- **Fase 1 — Núcleo do portal:** gestão de clientes, o motor de cálculo determinístico, PDFs SACS e TCC com layout fixo, login seguro com autenticação de dois fatores, registro de auditoria.
- **Fase 2 — Integrações:** um cofre de credenciais criptografado e conectores somente leitura para **Plaid, Schwab, RightCapital, Zillow, Pinnacle, PreciseFP** (+ Dropbox/Canva), com um sandbox embutido para rodar de ponta a ponta antes de conectar qualquer conta real.
- **Fase 3 — IA e interface com o cliente:** leitura de extratos, sinalização de anomalias, onboarding automático de clientes e lembretes, uma planilha de despesas e distribuição de relatórios por e-mail/Dropbox/Canva.
- **Fase 4 — Plataforma multiempresa:** cadastro self-service, identidade visual por empresa, cobrança por uso e um console de administração.

**Rode os testes:** `.\.venv\Scripts\python.exe -m pytest` (104 testes, ~40s).

### Colocando em produção (para a equipe de implementação)

Localmente é uma demonstração apoiada por um sandbox. Para implantar e conectar contas **reais**,
comece por **[docs/IMPLEMENTATION_HANDOFF.md](docs/IMPLEMENTATION_HANDOFF.md)** —
depois [DEPLOYMENT.md](docs/DEPLOYMENT.md), [PROVIDERS.md](docs/PROVIDERS.md) e [OPERATIONS.md](docs/OPERATIONS.md).
A configuração local completa e a solução de problemas estão em **[SETUP.md](SETUP.md)**.
