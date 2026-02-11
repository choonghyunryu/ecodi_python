-- Description: API 호출 오류 메시지 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_errmsg
(
    api_url_id     CHAR(6) NOT NULL,
    err_cd         VARCHAR(20) NOT NULL,
    err_msg        VARCHAR(50) NOT NULL,
    action         VARCHAR(50) NOT NULL,
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_api_errmsg_pkey PRIMARY KEY (api_url_id, err_cd)
);

COMMENT ON TABLE ecodi_meta.mt_api_errmsg IS 'API 호출 오류 메시지';

COMMENT ON COLUMN mt_api_errmsg.api_url_id IS 'API URL 아이디';
COMMENT ON COLUMN mt_api_errmsg.err_cd IS '오류 코드';
COMMENT ON COLUMN mt_api_errmsg.err_msg IS '오류 메시지';
COMMENT ON COLUMN mt_api_errmsg.action IS '조치방법';
COMMENT ON COLUMN mt_api_errmsg.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_api_errmsg.cret_nm IS '생성자';
COMMENT ON COLUMN mt_api_errmsg.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_api_errmsg.mdfy_nm IS '수정자';
