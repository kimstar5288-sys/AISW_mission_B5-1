# Mini Redis — 자료구조와 알고리즘 학습 미션

## 실행
Python 3.8 이상, 외부 패키지 불필요. VS Code에서 이 폴더를 열고 터미널에서 실행:

```bash
python mini_redis.py
```

Windows에서 `python` 명령이 안 되면 `py mini_redis.py`, macOS/Linux에서는 `python3 mini_redis.py`.

테스트:

```bash
python -m unittest discover -v
```

## 명령어
`SET key value`, `GET key`, `DEL key`, `EXISTS key`, `DBSIZE`, `KEYS`, `CONFIG SET maxmemory bytes`, `INFO memory`, `EXPIRE key seconds`, `TTL key`, `quit`.

보너스: `SUBSCRIBE channel subscriber`, `PUBLISH channel message`, `RECEIVE subscriber`.

## 핵심 구현
- `linked_list.py`: 센티널을 사용하는 이중 연결 리스트. 노드가 주어지면 O(1) 이동/삭제.
- `hash_map.py`: UTF-8 바이트 기반 131 다항 해시, 별도 체이닝, 부하율 0.75 초과 시 2배 확장. 평균 O(1), 최악 O(n).
- `dynamic_array.py`: 직접 용량 관리 및 2배 확장.
- `min_heap.py`: 동적 배열 기반 최소 힙. 삽입/삭제 O(log n), 최솟값 확인 O(1).
- `mini_redis.py`: 해시맵으로 키 검색, 이중 연결 리스트로 LRU 순서 추적, 힙으로 TTL 만료 시각 관리.
- `trees.py`: 이진 트리 순회 4종 및 BST 삽입/검색/삭제.
- `test_mini_redis.py`: 자동 단위 테스트.

## 설계 및 주의사항
1. `used_memory`는 키와 값의 UTF-8 인코딩 바이트 길이만 계산하며 자료구조 오버헤드는 제외한다.
2. LRU 앞쪽이 최근 사용 키, 뒤쪽이 가장 오래된 키다. SET/성공한 GET에서만 최근 사용 순서를 갱신한다.
3. 만료 힙은 lazy deletion을 사용한다. 덮어쓰기·삭제·EXPIRE 재설정 시 이전 힙 레코드는 무효화되고, 최상단 도달 시 제거된다. 따라서 힙에는 오래된 레코드가 잠시 남을 수 있다.
4. 만료 키는 명령 처리 시 일괄 정리한다. 별도 백그라운드 스레드는 사용하지 않는다.
5. 새 SET 엔트리 하나가 제한보다 크면 OOM으로 저장하지 않으며 기존 데이터는 보존한다.
6. `CONFIG SET maxmemory`로 제한을 낮추면 즉시 LRU 정리한다.
7. Pub/Sub는 실제 Redis와 다른 교육용 단일 프로세스 큐 모델이다. 네트워크·영속성 없음.
8. 입력은 `shlex`를 사용하므로 따옴표로 감싼 공백 포함 문자열을 지원한다.

## 수동 검증 예시
```
CONFIG SET maxmemory 12
SET a hello
SET b world
GET a
SET c okay
INFO memory
KEYS
EXPIRE a 2
TTL a
SUBSCRIBE news kim
PUBLISH news hello
RECEIVE kim
quit
```

## 학습목표 해설
**해시 충돌**: 서로 다른 키가 같은 버킷 인덱스를 갖더라도 각 버킷의 연결 리스트에서 키 전체를 비교하여 구분한다. 키 개수/버킷 수가 0.75를 넘으면 버킷 수를 두 배로 늘려 재배치한다.

**O(1) LRU**: 해시맵에서 엔트리(연결 리스트 노드 참조)를 평균 O(1)에 찾고, 이중 연결 리스트는 노드의 앞뒤 연결만 바꾸므로 이동이 O(1)이다. 제거할 키는 꼬리 바로 앞에서 즉시 찾는다.

**TTL 최소 힙**: 가장 가까운 만료 시각이 루트에 있어 O(1)로 확인한다. 만료된 요소를 꺼낼 때 O(log n)이므로 전체 키를 매번 훑지 않아도 된다.

**메모리 제한**: SET 전 단일 항목의 크기를 검사 → 값 저장/교체 → `used_memory` 조정 → 제한 초과 동안 LRU 꼬리 키 삭제 → 제거 시 크기 차감 및 `evicted_keys` 증가.
