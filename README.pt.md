[English](README.md) · **Português** 🇧🇷

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
