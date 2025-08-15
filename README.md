# BillG Server

> 🧾 FastAPI와 OpenAI Vision API로 구축된 AI 기반 영수증 데이터 추출 서비스

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [아키텍처](#아키텍처)
- [필수 요구사항](#필수-요구사항)
- [설치](#설치)
- [설정](#설정)
- [사용법](#사용법)
- [API 문서](#api-문서)
- [기여하기](#기여하기)
- [라이선스](#라이선스)

## 🎯 개요

BillG Server는 영수증 이미지 처리를 위해 특별히 설계된 고성능 텍스트 추출 서비스입니다. OpenAI의 GPT-4 Vision(멀티모달 LLM)을 활용하여 영수증 이미지를 이해하고 구조화된 데이터를 추출하며, 경비 추적, 회계 자동화, 재무 데이터 처리에 이상적입니다.

### 핵심 기능

- **다중 영수증 처리**: 단일 요청으로 여러 영수증 이미지 처리
- **구조화된 데이터 추출**: JSON 형식으로 특정 필드 추출
- **비동기 처리**: 고성능 비동기 아키텍처
- **요청 제한**: 남용 방지를 위한 내장 요청 제한
- **이미지 최적화**: 자동 이미지 크기 조정 및 전처리
- **다중 환경 지원**: 로컬, 스테이징, 프로덕션 환경 설정 가능

## ✨ 주요 기능

- 🚀 **FastAPI 프레임워크**: 현대적이고 빠르며 프로덕션에 즉시 사용 가능
- 🤖 **OpenAI GPT-4 Vision**: 멀티모달 AI를 활용한 영수증 텍스트 추출
- 📊 **구조화된 출력**: JSON 형식의 추출 결과
- 🔒 **보안**: Vault 지원을 통한 환경 기반 설정
- 🎯 **요청 제한**: IP 기반 요청 제한
- 📸 **이미지 처리**: 이미지 크기 조정 및 전처리
- 🐳 **Docker 지원**: 컨테이너화된 배포 준비 완료
- 🌐 **CORS 지원**: 설정 가능한 교차 출처 리소스 공유

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                     클라이언트 애플리케이션                │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI 애플리케이션                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │                   미들웨어 레이어                   │   │
│  │  • CORS 핸들러                                   │   │
│  │  • 요청 로거                                     │   │
│  │  • 예외 핸들러                                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │                   API 엔드포인트                   │   │
│  │  • /scan - 영수증 텍스트 추출                     │   │
│  │  • /actuator/health/* - 상태 체크              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │                   서비스 레이어                    │   │
│  │  • 텍스트 추출 서비스 (OpenAI Vision API)         │   │
│  │  • 이미지 전처리                                 │   │
│  │  • 요청 제한                                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      외부 서비스                         │
│  • OpenAI API (GPT-4 Vision)                          │
│  • Vault (비밀 관리)                                   │
└─────────────────────────────────────────────────────────┘
```

### 컴포넌트 구조

```
billg-server/
├── main.py                 # 애플리케이션 진입점 및 API 라우트
├── billg/
│   ├── __init__.py
│   ├── preprocessor.py     # 이미지 전처리 유틸리티
│   └── util/
│       ├── __init__.py
│       ├── exception.py    # 커스텀 예외 핸들러
│       ├── network.py      # 요청 제한 및 네트워크 유틸리티
│       ├── schema.py       # Pydantic 모델 및 스키마
│       └── vault.py        # 비밀 관리 통합
├── tests/                  # 테스트 스위트
│   └── test_limits.py
├── Dockerfile             # 컨테이너 설정
├── pyproject.toml         # 프로젝트 의존성 및 메타데이터
├── uv.lock               # 잠긴 의존성
└── tox.ini               # 테스트 자동화 설정
```

## 📋 필수 요구사항

- Python 3.10+ (3.12 권장)
- GPT-4 Vision 액세스 권한이 있는 OpenAI API 키
- UV 패키지 매니저 (권장) 또는 pip
- Docker (선택사항, 컨테이너화된 배포용)
- Redis (선택사항, 분산 요청 제한용)

## 🚀 설치

### UV 사용 (권장)

```bash
# 저장소 클론
git clone https://github.com/hbjs97/billg-server.git
cd billg-server

# 가상 환경 생성
uv venv --python 3.12.10
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv sync

# 개발 모드로 패키지 설치
uv pip install -e .
```

### pip 사용

```bash
# 저장소 클론
git clone https://github.com/hbjs97/billg-server.git
cd billg-server

# 가상 환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -e .
```

## ⚙️ 설정

### 환경 변수

프로젝트 루트에 `.env` 파일을 생성하세요:

```bash
# 필수
OPENAI_API_KEY=sk-your-openai-api-key

# 선택사항
PYTHON_ENV=local                    # local, staging, 또는 production
VAULT_URL=https://vault.example.com # Vault 서버 URL
VAULT_TOKEN=your-vault-token        # Vault 인증 토큰
```

### 환경별 설정

`PYTHON_ENV` 변수에 따라 애플리케이션 동작이 변경됩니다:

| 환경         | CORS 오리진               | 로깅 레벨 | 기능        |
| ------------ | ------------------------- | --------- | ----------- |
| `local`      | `*` (모두)                | DEBUG     | 전체 디버깅 |
| `staging`    | 제한적                    | INFO      | 테스트 기능 |
| `production` | `https://YOUR_SERVER_URL` | WARNING   | 최적화      |

### Vault 통합 (선택사항)

프로덕션 환경에서는 HashiCorp Vault를 사용하여 비밀을 관리하세요:

```python
# 초기화 코드에서
from billg.util import Vault

Vault.load(
    url="https://vault.example.com",
    app="billg",
    profile="production",
    mount_point="billg"
)
```

## 📖 사용법

### 서버 시작

#### 개발 모드

```bash
# FastAPI CLI 사용
fastapi dev main.py --reload

# 또는 Python 사용
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 프로덕션 모드

```bash
# FastAPI CLI 사용
fastapi run main.py --proxy-headers --port 80 --host 0.0.0.0
```

### 기본 사용 예제

```python
import requests
import base64

# 요청 준비
url = "http://localhost:8000/scan"
files = [
    ("files", ("receipt1.jpg", open("receipt1.jpg", "rb"), "image/jpeg")),
    ("files", ("receipt2.jpg", open("receipt2.jpg", "rb"), "image/jpeg"))
]
data = {
    "columns": ["date", "total_amount", "vendor_name", "items"]
}

# 요청 전송
response = requests.post(url, files=files, data=data)

# 응답 처리
if response.status_code == 200:
    results = response.json()["results"]
    for i, result in enumerate(results):
        print(f"영수증 {i+1}:")
        print(f"  날짜: {result.get('date')}")
        print(f"  총액: {result.get('total_amount')}")
        print(f"  상호명: {result.get('vendor_name')}")
```

## 📚 API 문서

### 엔드포인트

#### `POST /scan`

하나 이상의 영수증 이미지를 처리하고 지정된 데이터 필드를 추출합니다.

**요청:**

- **메서드**: POST
- **Content-Type**: multipart/form-data
- **요청 제한**: IP당 60초당 10개 요청

**매개변수:**

| 매개변수  | 타입     | 필수 | 설명                      |
| --------- | -------- | ---- | ------------------------- |
| `files`   | File[]   | 예   | 영수증 이미지 (JPEG, PNG) |
| `columns` | String[] | 예   | 영수증에서 추출할 필드    |

**지원되는 컬럼 타입:**

- 날짜/시간 필드: `date`, `time`, `datetime`, `purchase_date`
- 금액 필드: `total_amount`, `subtotal`, `tax`, `discount`
- 텍스트 필드: `vendor_name`, `store_address`, `receipt_number`
- 항목 목록: `items`, `products`

**응답:**

```json
{
  "results": [
    {
      "date": "2024-04-23 14:30:00",
      "total_amount": 42500,
      "vendor_name": "예제 상점",
      "items": ["상품 1", "상품 2"]
    }
  ]
}
```

**오류 응답:**

| 상태 코드 | 설명                             |
| --------- | -------------------------------- |
| 400       | 잘못된 요청 - 유효하지 않은 입력 |
| 429       | 너무 많은 요청 - 요청 제한 초과  |
| 500       | 내부 서버 오류                   |

#### `GET /actuator/health/liveness`

서비스가 살아있는지 확인합니다.

**응답:**

```json
{
  "message": "OK"
}
```

#### `GET /actuator/health/readiness`

서비스가 요청을 처리할 준비가 되었는지 확인합니다.

**응답:**

```json
{
  "message": "OK"
}
```

### 대화형 API 문서

로컬에서 실행 시 대화형 API 문서에 접근할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 기여하기

기여를 환영합니다! 다음 가이드라인을 따라주세요:

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경 사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. 풀 리퀘스트 열기

### 개발 워크플로우

1. **이슈 생성**: 문제나 기능 설명
2. **브랜치 생성**: 최신 `main`에서 생성
3. **개발**: 테스트와 함께 구현
4. **코드 리뷰**: 메인테이너에게 리뷰 요청
5. **병합**: 승인 및 CI 통과 후

### 코드 표준

- PEP 8 스타일 가이드 따르기
- 포괄적인 docstring 작성
- 타입 힌트 추가
- 80% 이상의 테스트 커버리지 유지
- 문서 업데이트

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- GPT-4 Vision API를 제공한 OpenAI
- FastAPI 프레임워크 개발자들
- 오픈 소스 커뮤니티 기여자들

## 📞 지원

문제 및 질문이 있으시면:

- GitHub 이슈: [github.com/hbjs97/billg-server/issues](https://github.com/hbjs97/billg-server/issues)
