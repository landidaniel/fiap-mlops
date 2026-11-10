# 📋 CHEATSHEET - Aula 08: Deploy Contínuo de Modelos (CI/CD de ML)

> Comandos batem com os arquivos reais do repositório.

## Qualidade / CI local

```bash
pip install -r requirements.txt

flake8 src tests                 # lint
black --check src tests          # checa formatação (sem alterar)
black src tests                  # aplica formatação

pytest tests/ -v --cov=src --cov-report=term

python src/train/train.py        # treina -> models/model.pkl
python src/train/validate_model.py   # quality gate (accuracy >= 0.85)
```

## A API de inferência (local)

```bash
# servidor de dev
python src/serve/app.py          # sobe em :5001

# produção (mesma da imagem)
gunicorn --bind 0.0.0.0:5001 --workers 2 src.serve.app:app

# chamadas
curl localhost:5001/health
curl localhost:5001/ready
curl localhost:5001/version
curl -X POST localhost:5001/predict \
  -H 'Content-Type: application/json' -d '{"features":[5.1,3.5,1.4,0.2]}'
```

## Docker

```bash
# build (treina + valida dentro do build)
docker build -t fiap-ml-iris:1.0.0 --build-arg APP_VERSION=1.0.0 .

# rodar
docker run -d --name iris -p 5001:5001 fiap-ml-iris:1.0.0
docker logs -f iris
docker rm -f iris

# publicar no Docker Hub
docker tag fiap-ml-iris:1.0.0 SEU-USUARIO/fiap-ml-cicd:v1.0.0
docker push SEU-USUARIO/fiap-ml-cicd:v1.0.0
```

## Kubernetes (Docker Desktop)

```bash
# sempre apontando pro cluster local (evita cluster errado)
CTX="--context docker-desktop"

kubectl $CTX get nodes
kubectl $CTX apply -f k8s/
kubectl $CTX rollout status deployment/iris-api --timeout=90s
kubectl $CTX get pods -l app=iris-api
kubectl $CTX get svc iris-api

# acessar
curl localhost:30080/ready
# alternativa portável:
kubectl $CTX port-forward svc/iris-api 8080:80   # depois curl localhost:8080

# self-healing (mata um pod e vê renascer)
kubectl $CTX delete pod <nome-do-pod>
kubectl $CTX get pods -l app=iris-api -w

# scaling
kubectl $CTX scale deployment/iris-api --replicas=4
kubectl $CTX scale deployment/iris-api --replicas=2

# rolling update + rollback
kubectl $CTX set image deployment/iris-api iris-api=fiap-ml-iris:2.0.0
kubectl $CTX set env   deployment/iris-api APP_VERSION=2.0.0
kubectl $CTX rollout status  deployment/iris-api
kubectl $CTX rollout history deployment/iris-api
kubectl $CTX rollout undo    deployment/iris-api    # rollback

# debug
kubectl $CTX describe pod <nome>
kubectl $CTX logs deploy/iris-api

# limpeza
kubectl $CTX delete -f k8s/
```

## GitHub Actions - CI (resumo)

```yaml
# .github/workflows/ci.yml
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
jobs:
  lint:   # flake8 + black
  test:   # pytest --cov, matrix 3.9/3.10/3.11, needs: lint
  train-and-validate:   # train.py + validate_model.py, upload-artifact, needs: test
```

## GitHub Actions - CD (resumo)

```yaml
# .github/workflows/cd.yml
on:
  push: { tags: ['v*'] }
  workflow_dispatch:
jobs:
  build-and-push:   # buildx + login + metadata-action + build-push-action
  smoke-test:       # sobe imagem, curl /ready e /predict, needs: build-and-push
```

## Secrets no GitHub

```
Settings → Secrets and variables → Actions → New repository secret
  DOCKERHUB_USERNAME = seu-usuario
  DOCKERHUB_TOKEN    = dckr_pat_...   (Read+Write)

# no workflow:  ${{ secrets.DOCKERHUB_TOKEN }}   (nunca echo do valor)
```

## Versionamento Semântico

```bash
git tag v1.0.0 && git push origin v1.0.0   # dispara o CD
# v1.0.0 -> v1.0.1  PATCH (bugfix / retreino mesmos dados)
# v1.0.1 -> v1.1.0  MINOR (feature compatível)
# v1.1.0 -> v2.0.0  MAJOR (breaking: mudou o payload de input)
```

## Pinagem de versões (boa prática)

```yaml
- uses: actions/checkout@v4          # pinar tag (ou SHA) — nunca @latest
- uses: actions/setup-python@v5
- uses: docker/build-push-action@v5
```

```dockerfile
FROM python:3.10-slim                # base pinada, não :latest
```
