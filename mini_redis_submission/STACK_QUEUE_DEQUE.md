# 스택·큐·덱

- **스택(Stack)**: LIFO(후입선출). 예: 실행 취소, 함수 호출. `push`/`pop`을 연결 리스트 앞쪽에서 O(1)로 구현.
- **큐(Queue)**: FIFO(선입선출). 예: 메시지 대기열. 연결 리스트 뒤에 `insert_back`, 앞에서 `remove_front`를 사용하여 O(1).
- **덱(Deque)**: 양쪽에서 삽입·삭제 가능한 큐. 이중 연결 리스트의 `insert_front`, `insert_back`, `remove_front`, `remove_back` 활용.

본 프로젝트의 Pub/Sub는 구독자별 이중 연결 리스트를 FIFO 메시지 큐로 사용한다. `SUBSCRIBE channel subscriber` 후 `PUBLISH channel message`로 메시지를 넣고 `RECEIVE subscriber`로 읽는다. 실제 Redis Pub/Sub와 달리 단일 CLI에서 구독자 ID를 명시하는 교육용 모델이다.
