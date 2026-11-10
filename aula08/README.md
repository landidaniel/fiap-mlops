# Aula 08 - Deploy Contínuo de Modelos (CI/CD de ML)

> **Repositório**: https://github.com/josenetoo/fiap-ml-aula08

## 🎯 Objetivo

Fechar o curso com o **deploy de verdade**: entender as estratégias de troca de
modelo sem downtime (Blue-Green/Canary), orquestrar a API de inferência no
**Kubernetes**, e amarrar um **pipeline de CI/CD** que valida, publica imagem
versionada e dispara o deploy da nova versão. **Última aula do curso.**

## 📹 Vídeos desta Aula

| Vídeo | Tema | O que você vai fazer |
|-------|------|---------------------|
| 8.1 | DevOps para ML e Estratégias de Deploy | Risco do deploy manual, roteamento de tráfego, Blue-Green/Canary, monitoramento (conceitual + demo leve) |
| 8.2 | Orquestração Escalável com Kubernetes | Deployment + Service + probes, self-healing, scaling e rolling update no Docker Desktop |
| 8.3 | Pipeline de CI/CD para Modelos | CI (lint+test+validate), CD (build+push Docker Hub), deploy da nova versão |

## 🏗️ Visão Geral

```
  git push main      →  CI:  lint → test (matrix) → train + validate → artifact
  git tag v1.0.0     →  CD:  build → push (Docker Hub) → smoke test
  kubectl set image  →  Deploy: rolling update no cluster (sem downtime)
```

Detalhes em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 📁 Estrutura do Repositório

```
.
├── .gitignore
├── .dockerignore
├── .flake8
├── README.md
├── requirements.txt
├── pytest.ini
├── pyproject.toml             # config do black
├── Dockerfile                 # imagem que serve a API (gunicorn)
├── .github/
│   └── workflows/
│       ├── ci.yml             # lint → test → train+validate
│       └── cd.yml             # build → push → smoke test
├── k8s/
│   ├── deployment.yaml        # 2 réplicas + probes + rolling update
│   ├── service.yaml           # NodePort 30080
│   └── blue-green/            # deploy-blue + deploy-green + service (switch por selector)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CHEATSHEET.md
│   ├── HANDS-ON-08-01.md      # DevOps + estratégias de deploy
│   ├── HANDS-ON-08-02.md      # Kubernetes
│   └── HANDS-ON-08-03.md      # CI/CD
├── src/
│   ├── serve/
│   │   └── app.py             # API Flask: /health /ready /version /predict
│   └── train/
│       ├── train.py
│       └── validate_model.py
└── tests/
    ├── test_smoke.py
    ├── test_train.py
    └── test_app.py            # testa a API de inferência
```

## ✅ Pré-requisitos

| Requisito | Como verificar |
|-----------|----------------|
| Aulas 01-07 concluídas | Estrutura entendida |
| Docker Desktop + Kubernetes habilitado | `kubectl config get-contexts` mostra `docker-desktop` |
| Conta GitHub | `gh auth status` ou login |
| Conta Docker Hub | https://hub.docker.com |

## 🔑 Secrets necessários (GitHub Actions)

| Secret | Onde configurar |
|--------|-----------------|
| `DOCKERHUB_USERNAME` | Repo → Settings → Secrets and variables → Actions |
| `DOCKERHUB_TOKEN` | Mesmo lugar (gerar token no Docker Hub, Read+Write) |

> ⚠️ Nunca commite valores de secrets. Use sempre `${{ secrets.NOME }}`.

## 🚀 Como Usar

1. **Fork** este repositório
2. Habilite o Kubernetes no Docker Desktop
3. Configure os secrets do Docker Hub no GitHub
4. Siga os hands-on em `docs/HANDS-ON-08-*.md`
5. Push → CI roda. `git tag v1.0.0` → CD publica. `kubectl set image` → deploy.

## 🧪 Rodar localmente

```bash
pip install -r requirements.txt
flake8 src tests
black --check src tests
pytest tests/ -v --cov=src
python src/train/train.py && python src/train/validate_model.py
```

## 📚 Documentação

| Vídeo | Hands-on |
|-------|----------|
| 8.1 - DevOps + Estratégias de Deploy | [HANDS-ON-08-01.md](docs/HANDS-ON-08-01.md) |
| 8.2 - Kubernetes | [HANDS-ON-08-02.md](docs/HANDS-ON-08-02.md) |
| 8.3 - CI/CD | [HANDS-ON-08-03.md](docs/HANDS-ON-08-03.md) |

**Referência rápida**: [Cheatsheet](docs/CHEATSHEET.md)

---

**FIAP - Pós Tech Machine Learning Engineering**

🎉 **Última aula do curso!**
