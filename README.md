# gpt-web-auto-access
## GPT Web 자동화 예제 스크립트

#### 기존 Chrome 세션(로그인된 상태)에 연결하여 CAPTCHA/인증 우회 및 이미지 업로드/다운로드 지원

#### 스크립트 실행 시 동일한 인스턴스(포트 9222)에 연결하여 세션 재사용, `invoke`로 텍스트/이미지 전송 및 응답(텍스트, 이미지 URL 리스트) 반환

#### debug 모드로 크롬에 접속 하는 것이기 때문에 보안 이슈에 주의 해야함 
#### 코드 재사용시 자신의 임시 크롬 프로파일 디렉토리가 노출 되는지 확인이 필요함 