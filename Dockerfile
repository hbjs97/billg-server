FROM python:3.12-slim

ENV TZ=Asia/Seoul

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 필수 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev tzdata git \
    libgl1-mesa-glx libglib2.0-0 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-group dev --frozen --compile-bytecode \
    && uv pip install . --compile-bytecode

CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--proxy-headers", "--port", "80", "--host", "0.0.0.0"]