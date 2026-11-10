# 🎬 Vídeo 8.2 - Orquestração Escalável com Kubernetes

**Aula**: 8 - Deploy Contínuo de Modelos (CI/CD de ML)  
**Vídeo**: 8.2  
**Temas**: Docker isolado → orquestração; Deployment; Service; Probes; Rolling update; Self-healing; Scaling

---

## 🚀 Sobre Este Vídeo

> **"Um container sozinho não se recupera quando cai. O Kubernetes reinicia, escala e troca de versão sem derrubar a API."**

No vídeo 8.1 vimos a **teoria** do deploy sem downtime. Aqui colocamos a **API de
inferência** dentro de um cluster Kubernetes rodando no **Docker Desktop** e vemos
réplicas, probes, self-healing, scaling e rolling update na prática.

| Etapa | Descrição |
|-------|-----------|
| **API de serving** | A app Flask que serve o modelo (`/health`, `/ready`, `/predict`) |
| **Imagem local** | Build sem precisar de registry (Docker Desktop compartilha o daemon) |
| **Deployment + Service** | Réplicas, probes, exposição via NodePort |
| **Self-healing** | Mata um pod e vê o cluster recriar |
| **Scaling** | `kubectl scale` de 2 → 4 réplicas |
| **Rolling update** | Troca de versão sem downtime |
| **Blue-Green** | Switch real trocando o `selector` do Service |

### Pré-requisitos

| Requisito | Como verificar |
|-----------|----------------|
| Docker Desktop com Kubernetes habilitado | Settings → Kubernetes → *Enable Kubernetes* |
| Cluster no ar | `kubectl config get-contexts` mostra `docker-desktop` |
| Node pronto | `kubectl --context docker-desktop get nodes` → `Ready` |

> ⚠️ Todos os comandos usam `--context docker-desktop` de propósito. Se você tiver
> outros clusters configurados, isso garante que **nada vai pro cluster errado**.
> Se quiser fixar o contexto: `kubectl config use-context docker-desktop`.

---

## 📚 Parte 1: Por Que Sair do Docker Solto

### Passo 1: O Limite do `docker run`

| Pergunta | `docker run` | Kubernetes |
|----------|--------------|------------|
| Container morreu, e agora? | Fica fora do ar até alguém rodar de novo | Recria sozinho (self-healing) |
| Preciso de 4 cópias | 4 `docker run` + um load balancer na mão | `replicas: 4` |
| Trocar de versão sem downtime | Manual (vídeo 8.1, Passo 8) | `kubectl set image` + rolling update |
| Como sei se está saudável? | `docker ps` e fé | readiness/liveness probes |
| Subiu, mas modelo não carregou | Recebe tráfego mesmo assim | Readiness segura o tráfego |

> 💡 **Ponto-chave**: Kubernetes é um **reconciliador**. Você declara o estado
> desejado ("quero 2 réplicas saudáveis da v1.0.0") e ele trabalha sem parar pra
> que a realidade bata com isso. Você para de dar ordens e passa a declarar metas.

---

## 🐳 Parte 2: A Imagem da API

### Passo 2: A Aplicação de Serving

A API que o cluster vai orquestrar está em `src/serve/app.py` (Flask + gunicorn).
Ela expõe os endpoints que o Kubernetes precisa:

| Endpoint | Uso no Kubernetes |
|----------|-------------------|
| `GET /health` | **liveness probe** — o processo está vivo? |
| `GET /ready` | **readiness probe** — o modelo carregou? pode receber tráfego? |
| `GET /version` | visualizar qual versão cada pod serve (útil no rolling update) |
| `POST /predict` | inferência (4 features → classe) |

> 🔍 **Nos bastidores**: liveness e readiness disparam ações **opostas**. Liveness
> falhou → o container é **reiniciado**. Readiness falhou → o pod só **sai do
> balanceamento**, sem morrer. Apontar os dois pro mesmo endpoint faz um modelo
> lento pra carregar entrar em loop de restart.

### Passo 3: Build da Imagem Local

No Docker Desktop, o cluster usa **o mesmo daemon** do seu Docker. Então uma imagem
buildada localmente já fica visível pro Kubernetes — **sem push pra registry**.

**Linux/Mac e Windows:**
```bash
docker build -t fiap-ml-iris:1.0.0 --build-arg APP_VERSION=1.0.0 .
```

**Resultado esperado** (treino + validação acontecem dentro do build):
```
 => [6/6] RUN python src/train/train.py && python src/train/validate_model.py
 => => Accuracy: 0.900
 => => ✅ Modelo aprovado
 => naming to docker.io/library/fiap-ml-iris:1.0.0
```

> 🔍 **Nos bastidores**: o manifest usa `imagePullPolicy: IfNotPresent`. Com a
> default (`Always` para tag `latest`), o cluster tentaria **puxar do registry** e
> daria `ErrImagePull` — a imagem só existe local. Por isso a tag é `1.0.0`, não `latest`.

✅ Imagem disponível pro cluster.

---

## ⚙️ Parte 3: Deployment e Service

### Passo 4: O Deployment

`k8s/deployment.yaml` declara **2 réplicas** da API com probes e limites de recurso:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iris-api
  labels:
    app: iris-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: iris-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: iris-api
    spec:
      containers:
        - name: iris-api
          image: fiap-ml-iris:1.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5001
          env:
            - name: APP_VERSION
              value: "1.0.0"
          readinessProbe:
            httpGet:
              path: /ready
              port: 5001
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 5001
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

> 🔍 **Nos bastidores**: `maxUnavailable: 0` + `maxSurge: 1` é o que garante
> **downtime zero**: sobe o pod novo, **espera a readiness dele** e só então derruba
> um antigo. Com a default (`maxUnavailable: 25%`), há uma janela de capacidade
> reduzida no meio do deploy.

### Passo 5: O Service

`k8s/service.yaml` expõe as réplicas atrás de um único endereço estável:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: iris-api
  labels:
    app: iris-api
spec:
  type: NodePort
  selector:
    app: iris-api
  ports:
    - name: http
      port: 80
      targetPort: 5001
      nodePort: 30080
```

> 🔍 **Nos bastidores**: o Service acha os pods pelo `selector: app=iris-api`, não
> por IP — pod morre e nasce com IP novo, ele reassocia sozinho. É esse mesmo
> `selector` que o **blue-green do vídeo 8.1** troca pra desviar o tráfego entre versões.

### Passo 6: Aplicar

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop apply -f k8s/
kubectl --context docker-desktop rollout status deployment/iris-api --timeout=90s
```

**Resultado esperado:**
```
deployment.apps/iris-api created
service/iris-api created
deployment "iris-api" successfully rolled out
```

**Ver os pods:**
```bash
kubectl --context docker-desktop get pods -l app=iris-api
```
```
NAME                        READY   STATUS    RESTARTS   AGE
iris-api-68695f7d48-956g7   1/1     Running   0          13s
iris-api-68695f7d48-rfb2k   1/1     Running   0          13s
```

✅ Duas réplicas no ar e prontas (readiness passou).

### Passo 7: Testar via Service

O NodePort `30080` é exposto em `localhost` pelo Docker Desktop:

**Linux/Mac e Windows:**
```bash
curl -s localhost:30080/ready
curl -s -X POST localhost:30080/predict \
  -H 'Content-Type: application/json' -d '{"features":[6.3,3.3,6.0,2.5]}'
```

**Resultado esperado:**
```
{"status":"ready","version":"1.0.0"}
{"label":"virginica","prediction":2,"version":"1.0.0"}
```

> 💡 Se o `30080` não responder no seu setup, use port-forward (funciona em
> qualquer cluster): `kubectl --context docker-desktop port-forward svc/iris-api 8080:80`
> e chame `localhost:8080`.

✅ Tráfego entrando pelo Service e balanceado entre as réplicas.

---

## 🩺 Parte 4: Self-Healing

### Passo 8: Matar um Pod e Ver Renascer

**Linux/Mac e Windows:**
```bash
# Pega o nome de um pod e mata
POD=$(kubectl --context docker-desktop get pods -l app=iris-api -o jsonpath='{.items[0].metadata.name}')
kubectl --context docker-desktop delete pod "$POD"

# Observa o cluster recriar (Ctrl+C pra sair)
kubectl --context docker-desktop get pods -l app=iris-api -w
```

**Resultado esperado:** o pod deletado some e **outro nasce em segundos**, voltando
pra 2/2. A API nunca ficou indisponível — a outra réplica segurou o tráfego.

> 🔍 **Nos bastidores**: você não pediu o pod de volta. O **ReplicaSet** tem
> `replicas: 2` como meta e reconcilia: viu 1 pod, criou outro. É o mesmo loop que
> recupera de um nó reiniciado ou de um `OOMKilled`.

---

## 📈 Parte 5: Scaling

### Passo 9: Escalar Horizontalmente

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop scale deployment/iris-api --replicas=4
kubectl --context docker-desktop get pods -l app=iris-api
```

**Resultado esperado:** 4 pods `Running`. Mais réplicas = mais throughput e mais
tolerância a falha, sem mudar nada na aplicação.

**Voltar pra 2:**
```bash
kubectl --context docker-desktop scale deployment/iris-api --replicas=2
```

> 💡 Em produção, `HorizontalPodAutoscaler` faz isso automático com base em
> CPU/memória ou métrica custom (ex.: requests por segundo). Aqui fizemos manual
> pra ver o efeito.

---

## 🔄 Parte 6: Rolling Update (sem downtime)

### Passo 10: Buildar a v2.0.0

**Linux/Mac e Windows:**
```bash
docker build -t fiap-ml-iris:2.0.0 --build-arg APP_VERSION=2.0.0 .
```

### Passo 11: Trocar a Versão no Ar

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop set image deployment/iris-api iris-api=fiap-ml-iris:2.0.0
kubectl --context docker-desktop set env   deployment/iris-api APP_VERSION=2.0.0
kubectl --context docker-desktop rollout status deployment/iris-api --timeout=90s
```

**Resultado esperado:**
```
deployment.apps/iris-api image updated
Waiting for deployment "iris-api" rollout to finish: 1 out of 2 new replicas have been updated...
Waiting for deployment "iris-api" rollout to finish: 1 old replicas are pending termination...
deployment "iris-api" successfully rolled out
```

**Confirmar a versão servida:**
```bash
curl -s localhost:30080/version
```
```
{"model_path":"models/model.pkl","version":"2.0.0"}
```

> 🔍 **Nos bastidores**: durante o rollout o Service balanceou pods v1.0.0 (saindo)
> e v2.0.0 (entrando) **ao mesmo tempo**. O pod novo só recebe tráfego depois da
> readiness, e o antigo só morre depois — por isso não há buraco.

### Passo 12: Rollback Instantâneo

Achou que a v2.0.0 está ruim? Volta sem rebuildar nada:

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop rollout undo deployment/iris-api
kubectl --context docker-desktop rollout status deployment/iris-api --timeout=90s
```

> 🔍 **Nos bastidores**: o `undo` não refaz deploy — ele **reescala o ReplicaSet
> anterior** de volta pra cima. Por isso é instantâneo: a definição da versão antiga
> nunca foi apagada (`kubectl rollout history deployment/iris-api`).

---

## 🔵🟢 Parte 7: Blue-Green (o switch real do vídeo 8.1)

O rolling update troca os pods **no mesmo Deployment**, gradual. O blue-green é
diferente: mantém **dois Deployments completos** (blue e green) e um Service que
aponta para um deles. O switch é trocar o `selector` do Service — instantâneo, e o
endereço de acesso nunca muda.

Os manifests estão em `k8s/blue-green/`: `deploy-blue.yaml` (imagem `1.0.0`,
label `version: blue`), `deploy-green.yaml` (imagem `2.0.0`, label `version: green`)
e `service.yaml` (NodePort 30090, começando no `blue`).

### Passo 13: Subir Blue e Green

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop apply -f k8s/blue-green/
kubectl --context docker-desktop rollout status deployment/iris-api-blue  --timeout=90s
kubectl --context docker-desktop rollout status deployment/iris-api-green --timeout=90s

# O Service começa apontando pro blue
curl -s localhost:30090/version
```

**Resultado esperado:**
```
{"model_path":"models/model.pkl","version":"blue-1.0.0"}
```

As duas versões estão no ar, mas o Service só entrega a `blue`. A `green` está
pronta, sendo validada, sem receber tráfego de cliente.

### Passo 14: O Switch (blue → green)

Trocar o `selector` do Service é o switch:

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop patch service iris-api-bg \
  -p '{"spec":{"selector":{"app":"iris-api","version":"green"}}}'

curl -s localhost:30090/version
```

**Resultado esperado:**
```
{"model_path":"models/model.pkl","version":"green-2.0.0"}
```

Mesmo endereço (`localhost:30090`), o cliente não mudou nada — só o backend trocou.

> 🔍 **Nos bastidores**: o patch reescreve o `selector` e o Service reassocia os
> endpoints na hora. Requests em voo terminam no pod blue; os novos já vão pro green.
> Diferente do rolling update, as duas versões seguem **inteiras** no ar — por isso
> o rollback é imediato e você pode validar a green com tráfego antes de promover.

### Passo 15: Rollback (green → blue)

Deu problema na green? Volta o selector:

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop patch service iris-api-bg \
  -p '{"spec":{"selector":{"app":"iris-api","version":"blue"}}}'

curl -s localhost:30090/version    # -> blue-1.0.0 de novo
```

| Rolling update | Blue-Green |
|----------------|------------|
| Um Deployment, pods trocados aos poucos | Dois Deployments completos no ar |
| Rollback reescala o ReplicaSet anterior | Rollback troca o selector de volta |
| Sem dobro de recurso | Custa o dobro durante a coexistência |

---

## 🧹 Parte 8: Limpeza

> ⚠️ Isto **remove** os Deployments e Services de teste do cluster local. É seguro:
> só afeta o contexto `docker-desktop`. Confirme antes se estiver num cluster real.

**Linux/Mac e Windows:**
```bash
kubectl --context docker-desktop delete -f k8s/blue-green/
kubectl --context docker-desktop delete -f k8s/
```

✅ Cluster limpo.

---

## 📦 Arquivos de Referência (versão final)

### `k8s/deployment.yaml` / `k8s/service.yaml`
Conteúdo idêntico ao mostrado nos Passos 4 e 5. Versão final — sem trechos temporários.

### `k8s/blue-green/` (`deploy-blue.yaml`, `deploy-green.yaml`, `service.yaml`)
Usados na Parte 7. Os dois Deployments só diferem em `image`, no label `version` e
no `APP_VERSION`; o Service alterna entre eles pelo `selector`.

> Único ponto a ajustar no vídeo 8.3: o campo `image` passa de `fiap-ml-iris:1.0.0`
> (local) para `SEU-USUARIO/fiap-ml-cicd:vX.Y.Z` (registry), quando o deploy
> consumir a imagem publicada pelo CD.

---

## 🔧 Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `ErrImagePull` / `ImagePullBackOff` | `imagePullPolicy: Always` numa imagem só local | Use `IfNotPresent` e tag versionada (não `latest`) |
| Pod em `CrashLoopBackOff` | App quebrou ao subir | `kubectl logs deploy/iris-api` |
| Pod fica `0/1 Running` | Readiness não passou | `kubectl describe pod <nome>`; ver `/ready` e o modelo |
| `connection refused` no 30080 | Service não subiu ou porta tomada | `kubectl get svc`; ou use `port-forward` |
| Liveness derruba pod em loop | Probe agressiva demais | Aumentar `initialDelaySeconds` da liveness |
| `kubectl` no cluster errado | Contexto atual é outro | Sempre `--context docker-desktop` |

---

**FIM DO VÍDEO 8.2** ✅

> Próximo (**8.3**): automatizar tudo. Em vez de buildar e trocar a imagem na mão,
> o **pipeline de CI/CD** valida, publica a imagem versionada e dispara o deploy
> da nova versão.
