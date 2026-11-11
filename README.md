# FIAP MLOps

Projeto desenvolvido durante a Pós-Tech em Machine Learning Engineering da FIAP.

Este repositório reúne a evolução prática de um projeto de Machine Learning ao longo das aulas de MLOps, desde ingestão e validação de dados até treinamento, testes automatizados, orquestração, CI/CD e deploy de uma API de inferência em Kubernetes.

## Objetivos do projeto

- Organizar um projeto de Machine Learning com separação de responsabilidades.
- Criar pipelines de ingestão, validação, transformação e treinamento.
- Versionar código e dados com Git, GitHub e DVC.
- Automatizar testes, lint, formatação e validação do modelo.
- Empacotar a API de inferência em uma imagem Docker versionada.
- Publicar a imagem no Docker Hub através do GitHub Actions.
- Validar a imagem publicada com smoke tests.
- Executar a API em Kubernetes com réplicas, probes, Service, rolling update, rollback e Blue-Green deployment.

## Conteúdos trabalhados

- Ambientes virtuais e organização de projetos Python.
- Ingestão, validação e transformação de dados.
- Feature Engineering e pipelines com Scikit-Learn.
- Treinamento, avaliação e persistência de modelos.
- Reprodutibilidade e escolha de modelos.
- Testes automatizados com Pytest e cobertura de código.
- Qualidade de código com Flake8 e Black.
- Versionamento de código com Git e GitHub.
- Versionamento de dados e artefatos com DVC.
- Orquestração de pipelines com Airflow.
- Retreinamento automático e detecção de drift.
- Containers com Docker.
- CI/CD com GitHub Actions.
- Publicação de imagens no Docker Hub.
- Deploy de modelos com Kubernetes.
- Readiness probe, liveness probe e self-healing.
- Escalabilidade, rolling update, rollback e Blue-Green deployment.

## Organização do repositório

```text
fiap-mlops/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── .dvc/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── models/
├── src/
│   ├── data/
│   ├── features/
│   ├── train/
│   └── pipeline.py
├── tests/
├── aula05/
├── aula06/
├── aula07/
├── aula08/
│   ├── Dockerfile
│   ├── k8s/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── blue-green/
│   ├── src/
│   │   ├── serve/
│   │   └── train/
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
├── config.yaml
├── .gitignore
├── .dvcignore
├── pytest.ini
├── requirements.txt
└── README.md
```

> As aulas anteriores possuem componentes integrados à estrutura principal do projeto. A Aula 8 possui uma estrutura isolada em `aula08/` para facilitar a construção da imagem e a execução do pipeline de CI/CD.

## Aula 8: API de inferência

A API da Aula 8 utiliza Flask e Gunicorn e disponibiliza:

| Endpoint | Função |
|---|---|
| `GET /health` | Verifica se o processo está ativo. |
| `GET /ready` | Verifica se o modelo foi carregado e está pronto. |
| `GET /version` | Retorna a versão da aplicação/modelo. |
| `POST /predict` | Recebe quatro características da Iris e retorna a previsão. |

Exemplo de requisição:

```bash
curl -s -X POST http://localhost:30080/predict \
  -H 'Content-Type: application/json' \
  -d '{"features":[6.3,3.3,6.0,2.5]}'
```

## Executar os testes localmente

Entre na pasta da Aula 8 e crie um ambiente virtual, se necessário:

```bash
cd aula08
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Execute as verificações de qualidade:

```bash
flake8 src tests
black --check src tests
pytest tests/ -v --cov=src --cov-report=term
python src/train/train.py
python src/train/validate_model.py
```

O pipeline local deve terminar com os testes aprovados e o modelo validado.

## CI com GitHub Actions

O workflow `.github/workflows/ci.yml` é executado em pushes para `main` e em Pull Requests. Ele realiza:

1. Flake8.
2. Verificação de formatação com Black.
3. Testes automatizados com Pytest.
4. Cobertura de código.
5. Treinamento do modelo.
6. Validação da acurácia.
7. Upload do modelo treinado como artifact.

Workflow: [CI](https://github.com/landidaniel/fiap-mlops/actions/workflows/ci.yml)

## CD com GitHub Actions e Docker Hub

O workflow `.github/workflows/cd.yml` é acionado por tags no formato `v*` ou manualmente pela interface do GitHub Actions.

O CD realiza:

1. Login seguro no Docker Hub por meio de Secrets.
2. Build da imagem Docker usando `aula08/Dockerfile`.
3. Treinamento e validação do modelo durante o build.
4. Push da imagem para o Docker Hub.
5. Smoke test do endpoint `/ready`.
6. Smoke test do endpoint `/predict`.

Secrets necessários no repositório GitHub:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

A imagem publicada no projeto é:

```text
landidaniel/fiap-ml-cicd:latest
```

Docker Hub: [landidaniel/fiap-ml-cicd](https://hub.docker.com/r/landidaniel/fiap-ml-cicd)

Para publicar uma versão versionada, crie uma tag e envie-a ao GitHub:

```bash
git tag v1.0.1
git push origin v1.0.1
```

## Deploy local no Kubernetes

O deploy da Aula 8 utiliza o Kubernetes do Docker Desktop. O runner hospedado do GitHub não consegue acessar o cluster local, portanto a etapa de deploy é executada localmente.

Pré-requisitos:

- Docker Desktop em execução.
- Kubernetes habilitado no Docker Desktop.
- Contexto `docker-desktop` configurado.

Verifique o cluster:

```bash
kubectl --context docker-desktop get nodes
```

Aplique os manifests:

```bash
kubectl --context docker-desktop apply -f aula08/k8s/
```

Aponte o Deployment para a imagem publicada:

```bash
kubectl --context docker-desktop set image \
  deployment/iris-api \
  iris-api=landidaniel/fiap-ml-cicd:latest
```

Acompanhe o rollout:

```bash
kubectl --context docker-desktop rollout status \
  deployment/iris-api \
  --timeout=180s
```

Verifique os pods:

```bash
kubectl --context docker-desktop get pods -l app=iris-api
```

O Service principal expõe a API em:

```text
http://localhost:30080
```

Testes:

```bash
curl -s http://localhost:30080/ready
curl -s http://localhost:30080/version
curl -s -X POST http://localhost:30080/predict \
  -H 'Content-Type: application/json' \
  -d '{"features":[6.3,3.3,6.0,2.5]}'
```

## Recursos demonstrados no Kubernetes

- Duas réplicas da API.
- Readiness probe em `/ready`.
- Liveness probe em `/health`.
- Recriação automática de pods.
- Escala manual de réplicas.
- Rolling update sem downtime.
- Rollback para uma versão anterior.
- Blue-Green deployment com troca do selector do Service.

## Limpeza local

Os recursos Kubernetes podem ser removidos com:

```bash
kubectl --context docker-desktop delete -f aula08/k8s/blue-green/ 2>/dev/null || true
kubectl --context docker-desktop delete -f aula08/k8s/ 2>/dev/null || true
```

Para limpar os dados locais do Docker:

```bash
docker system prune -a --volumes -f
docker builder prune -a -f
```

Esses comandos não removem o código do GitHub nem a imagem já publicada no Docker Hub.

## Status do projeto

- Aulas 1 a 7: atividades de MLOps, pipelines, qualidade, Airflow, MLflow e retreinamento.
- Aula 8.1: estratégias de deploy e CI/CD para modelos.
- Aula 8.2: Kubernetes, réplicas, probes, scaling, rolling update, rollback e Blue-Green.
- Aula 8.3: CI/CD com GitHub Actions, Docker Hub e smoke tests.
- API de inferência publicada e validada em Kubernetes local.

## Tecnologias

Python · Scikit-Learn · Flask · Gunicorn · Pytest · Flake8 · Black · Git · GitHub Actions · Docker · Docker Hub · Kubernetes · Airflow · MLflow · DVC

## Autor

Daniel Landi — [GitHub](https://github.com/landidaniel)
