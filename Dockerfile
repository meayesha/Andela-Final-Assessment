# Hugging Face Spaces (and similar) single container: Next static export + FastAPI.
# HF sets PORT (often 7860). Default CMD uses 7860.

FROM node:22-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Clerk uses Server Actions — incompatible with output: 'export'. Ship a Clerk-free UI for this static bundle (use Vercel for full Clerk).
COPY frontend/docker-hf/layout.tsx ./app/layout.tsx
COPY frontend/docker-hf/page.tsx ./app/page.tsx
COPY frontend/docker-hf/ChatShell.tsx ./app/ChatShell.tsx
ENV STATIC_EXPORT=true
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
# docker-hf UI does not send Clerk; JWKS may still be set for cross-origin Vercel. Allow anonymous /api without Bearer.
ENV CLERK_AUTH_OPTIONAL=1
ENV PYTHONPATH=/app
ENV DATA_DIR=/data
RUN mkdir -p /data
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ /app/
COPY --from=frontend /app/frontend/out /app/static
EXPOSE 7860
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
