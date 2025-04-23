# billg-server

## 설치

```sh
uv venv --python 3.12.10
source .venv/bin/activate

# 의존성 설치
uv sync
```

## lock

### 생성

```sh
uv lock
```

### 업데이트

```sh
uv lock --refresh
```

## Run Tests

### pytest

```bash
pip install pytest
python -m unittest discover -s tests -p 'test_*.py'
```

### tox

```bash
pip install -r requirements-test.txt
tox
```
