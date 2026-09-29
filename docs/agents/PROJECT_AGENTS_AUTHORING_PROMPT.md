# Project AGENTS Authoring Prompt

이 템플릿은 새 프로젝트의 루트 `AGENTS.md`를 생성하거나 장기 규칙 변경 시 갱신할 때 사용한다.
템플릿 자체를 `AGENTS.md`로 복사하지 않는다. 생성 결과는 프로젝트 소유이며 Veyrix 관리 산출물이 아니다.

## 실행 프롬프트

현재 저장소를 조사해 루트 `AGENTS.md`를 생성하거나 최소 수정하라.
프로젝트의 장기적인 사실·계약·명령만 기록하고 일반 기술 튜토리얼, Veyrix Skill 본문,
OMO orchestration 규칙이나 일시적 작업 상태를 복제하지 마라.

### 1. 경계와 기존 상태

- 사용자가 지정한 프로젝트 경계를 우선하고, 없으면 현재 작업 트리/저장소 루트를 확인한다.
- 기존 루트·상위·하위 `AGENTS.md`, README/CONTRIBUTING, 유지되는 설계 문서와 현재 작업 트리 변경을 확인한다.
- 기존 `AGENTS.md`가 있으면 사용자 규칙·언어·관리 블록을 보존한다. symlink나 다른 도구 소유 파일은 직접 덮어쓰지 않는다.
- 이 요청의 영구 변경은 대상 루트 `AGENTS.md` 하나뿐이다. 미리보기 요청이면 파일을 쓰지 않는다.

### 2. 근거 중심 조사

전체 파일을 무차별로 읽지 말고 구조를 파악한 뒤 필요한 근거를 읽는다.

- 빌드·패키지·workspace·runtime 버전 설정, wrapper, script, formatter/linter, CI.
- 주요 module 책임과 입증된 dependency 방향을 보여주는 대표 source/test/ADR.
- 테스트 종류·위치·실제 실행 경로와 필요한 local service/env 이름.
- API·DB·message·serialization 계약, migration, generator 설정과 generated ownership.
- 기존 Veyrix/OMO 자료는 실제 존재하고 이번 문서에 필요한 범위만.

명령 존재와 실행 성공을 구분한다. 한 구현 사례를 정책으로 만들지 않는다.
확인할 수 없는 architecture, version, coverage, runtime activation이나 지원 범위를 발명하지 않는다.

### 3. 책임 분리

- OpenCode의 host/permission, OMO Slim의 agent/delegation/model 정책을 새로 정의하지 않는다.
- Veyrix가 있으면 `veyrix.yml`은 사용자 선택, lock/managed receipt는 resolution/ownership 자료로 취급한다.
- `.agents/skills/` 전체가 Veyrix 소유라고 단정하지 말고 확인된 managed ID만 구분한다.
- Skill 선택·routing 목록을 AGENTS에 복제하지 않는다. 선택됨/배치됨/허용됨/실제 사용됨을 구분한다.
- Veyrix가 없어도 문서 작성은 진행한다. 설치·profile 변경·permission 확대는 이 요청 범위가 아니다.

### 4. 작성 기준

다음 중 실제 근거와 미래 의사결정 가치가 있는 섹션만 사용하고 빈 섹션은 만들지 않는다.

- Project: 목적과 구조 이해에 필요한 최소 배경.
- Authority: 규칙·계약의 source of truth와 읽어야 할 시점.
- Architecture: module 책임과 입증된 dependency/process boundary.
- Ownership: generated/vendor/external 영역과 지원되는 수정 경로.
- Contracts: API/DB/message/schema의 authoritative source.
- Development / Verification: 실제 명령, 실행 위치, prerequisite와 확인 범위.
- Project-specific constraints: 저장소에서 확인한 함정과 명시적 예외.

가능하면 저장소 상대 경로를 사용한다. 보통 50~120줄 안팎을 목표로 하되 중요한 기존 계약을
줄 수 때문에 삭제하지 않는다. 긴 세부사항은 유지되는 원문 경로와 읽을 시점을 안내한다.

다음은 새로 넣지 않는다: 일반 framework best practice, 공통 review/security/regression checklist,
자동 설치, 새 MCP/agent/command, 추정한 명령·architecture·test PASS, 현재 branch 진행상태,
TODO/placeholder, Veyrix ownership header, 매 작업마다 AGENTS를 재생성하라는 지시.

### 5. 안전한 적용

기존 문서가 정확하면 `NOOP`으로 끝낸다. 오래된 내용 수정/삭제에는 근거가 있어야 한다.
쓰기 직전에 대상 파일을 다시 읽고 concurrent user change가 있으면 현재 내용을 기준으로 재계산한다.
쓰기 후 diff를 확인해 자신이 바꾼 영구 파일이 허용된 AGENTS 하나인지 확인한다.
commit/push/PR/merge는 별도 요청 없이는 수행하지 않는다.

### 6. 결과 보고

- 결과: `CREATED`, `UPDATED`, `NOOP`, `PREVIEW`, `BLOCKED`.
- 핵심 변경: 추가·수정·보존·의도적으로 생략한 규칙.
- 근거: 주요 사실/규칙과 실제 확인한 파일·설정·symbol/section.
- 검증: `ACTUAL_PASS`, `ACTUAL_FAIL`, `STATIC`, `NOT_RUN`, `BLOCKED`를 구분.
- 미확정 사항: 충돌, 접근 불가, 조사 한계, 미검증 runtime/command.

이 정적 authoring 절차는 실제 OpenCode load, OMO delegation 또는 모델 품질 검증을 대신하지 않는다.
