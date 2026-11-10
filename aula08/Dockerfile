FROM python:3.10-slim

WORKDIR /app

# 1. Deps primeiro: aproveita o cache de layer enquanto requirements nao muda
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Codigo
COPY src/ ./src/

# 3. Treina E VALIDA dentro do build -> imagem autocontida e reproduzivel.
#    Se a accuracy cair abaixo do threshold, o build FALHA aqui.
RUN python src/train/train.py && python src/train/validate_model.py

# 4. Metadados de versao (sobrescritos no build/k8s via --build-arg / env)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}
ENV MODEL_PATH=models/model.pkl

# 5. Serve a API de inferencia com gunicorn (2 workers)
EXPOSE 5001
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "src.serve.app:app"]
