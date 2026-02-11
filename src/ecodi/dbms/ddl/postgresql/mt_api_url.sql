-- Description: API 호출 URL 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_url
(
    api_url_id     CHAR(6) NOT NULL,
    api_url_nm     VARCHAR(50) NOT NULL,
    is_usekey      CHAR(1) DEFAULT 'Y' NOT NULL,
    key_id         VARCHAR(20),
    call_url       VARCHAR(200) NOT NULL,
    call_methd     VARCHAR(20) NOT NULL,
    return_type    VARCHAR(20) NOT NULL,
    param_cnt      INTEGER NOT NULL,
    limit_cell_cnt INTEGER,
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_api_url_pkey PRIMARY KEY (api_url_id)
);

COMMENT ON TABLE ecodi_meta.mt_api_url IS 'API 호출 URL';

COMMENT ON COLUMN mt_api_url.api_url_id IS 'API URL 아이디';
COMMENT ON COLUMN mt_api_url.api_url_nm IS 'API URL 명칭';
COMMENT ON COLUMN mt_api_url.is_usekey IS 'API Key 사용 여부';
COMMENT ON COLUMN mt_api_url.key_id IS 'API Key 아이디';
COMMENT ON COLUMN mt_api_url.call_url IS 'API 호출 URL';
COMMENT ON COLUMN mt_api_url.call_methd IS '호출방법';
COMMENT ON COLUMN mt_api_url.return_type IS '반환 데이터 구조';
COMMENT ON COLUMN mt_api_url.param_cnt IS '파라미터 개수';
COMMENT ON COLUMN mt_api_url.limit_cell_cnt IS 'Limit 셀 개수';
COMMENT ON COLUMN mt_api_url.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_api_url.cret_nm IS '생성자';
COMMENT ON COLUMN mt_api_url.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_api_url.mdfy_nm IS '수정자';
