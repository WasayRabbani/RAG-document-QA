FROM node:22-alpine AS frontend-build

WORKDIR /code/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code/backend

COPY backend/requirements.txt /code/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/backend/requirements.txt

COPY backend/ /code/backend/
COPY --from=frontend-build /code/frontend/dist /code/frontend/dist

RUN mkdir -p /code/backend/storage/indices /code/backend/storage/chunks /code/backend/uploads

EXPOSE 7860

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
