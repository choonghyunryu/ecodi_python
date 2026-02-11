-- Description: Open API KEY 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_key
(
    key_id      VARCHAR(20) NOT NULL,
    user_id_enc VARCHAR(20) NOT NULL,
    org_nm      VARCHAR(50) NOT NULL,
    org_nm_en   VARCHAR(50),
    key_enc     VARCHAR(200) NOT NULL,
    manage_url  VARCHAR(200) NOT NULL,
    reg_nm_enc  VARCHAR(20),
    reg_id_enc  VARCHAR(20) NOT NULL,
    valid_date  CHAR(10) NOT NULL,
    used        CHAR(1) NOT NULL,
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_api_key_pkey PRIMARY KEY (key_id, user_id_enc)
);

COMMENT ON TABLE ecodi_meta.mt_api_key IS 'Open API KEY 정보';

COMMENT ON COLUMN mt_api_key.key_id IS 'KEY 아이디';
COMMENT ON COLUMN mt_api_key.user_id_enc IS '크롤러 서버 사용자 아이디';
COMMENT ON COLUMN mt_api_key.org_nm IS '공급 기관명';
COMMENT ON COLUMN mt_api_key.org_nm_en IS '인코딩된 Open API Key';
COMMENT ON COLUMN mt_api_key.key_enc IS 'Key 관리 URL';
COMMENT ON COLUMN mt_api_key.manage_url IS 'KEY 발급자';
COMMENT ON COLUMN mt_api_key.reg_nm_enc IS 'KEY 발급자';
COMMENT ON COLUMN mt_api_key.reg_id_enc IS 'KEY 발급자 아이디';
COMMENT ON COLUMN mt_api_key.valid_date IS 'KEY 유효일자';
COMMENT ON COLUMN mt_api_key.used IS 'KEY 사용여부';
COMMENT ON COLUMN mt_api_key.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_api_key.cret_nm IS '생성자';
COMMENT ON COLUMN mt_api_key.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_api_key.mdfy_nm IS '수정자';
