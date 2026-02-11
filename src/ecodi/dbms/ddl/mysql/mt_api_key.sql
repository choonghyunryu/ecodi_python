-- Description: Open API KEY 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_key
(
    key_id      VARCHAR(20) NOT NULL            COMMENT 'KEY 아이디',
    user_id_enc VARCHAR(20) NOT NULL            COMMENT '크롤러 서버 사용자 아이디',
    org_nm      VARCHAR(50) NOT NULL            COMMENT '공급 기관명',
    org_nm_en   VARCHAR(50)                     COMMENT '인코딩된 Open API Key',
    key_enc     VARCHAR(200) NOT NULL           COMMENT 'Key 관리 URL',
    manage_url  VARCHAR(200) NOT NULL           COMMENT 'KEY 발급자',
    reg_nm_enc  VARCHAR(20)                     COMMENT 'KEY 발급자',
    reg_id_enc  VARCHAR(20) NOT NULL            COMMENT 'KEY 발급자 아이디',
    valid_date  CHAR(10) NOT NULL               COMMENT 'KEY 유효일자',
    used        CHAR(1) NOT NULL                COMMENT 'KEY 사용여부',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_api_key_pkey PRIMARY KEY (key_id, user_id_enc)
);

ALTER TABLE ecodi_meta.mt_api_key COMMENT = 'Open API KEY 정보';
