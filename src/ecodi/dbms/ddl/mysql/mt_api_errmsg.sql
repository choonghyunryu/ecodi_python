-- Description: API 호출 오류 메시지 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_errmsg
(
    api_url_id     CHAR(6) NOT NULL                COMMENT 'API URL 아이디',
    err_cd         VARCHAR(20) NOT NULL            COMMENT '오류 코드',
    err_msg        VARCHAR(50) NOT NULL            COMMENT '오류 메시지',
    action         VARCHAR(50) NOT NULL            COMMENT '조치방법',
    cret_dt        DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm        VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt        DATETIME                        COMMENT '수정일시',
    mdfy_nm        VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_api_errmsg_pkey PRIMARY KEY (api_url_id, err_cd)
);

ALTER TABLE ecodi_meta.mt_api_errmsg COMMENT = 'API 호출 오류 메시지';
