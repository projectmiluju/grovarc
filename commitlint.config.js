export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 새 기능
        'fix',      // 버그 수정
        'docs',     // 문서
        'style',    // 포맷, 세미콜론 등 (코드 변경 없음)
        'refactor', // 리팩토링
        'test',     // 테스트
        'chore',    // 빌드, 설정, 패키지 등
        'perf',     // 성능 개선
        'ci',       // CI/CD
        'revert',   // 되돌리기
      ],
    ],
    'subject-case': [0], // 한글 커밋 메시지 허용
  },
};
