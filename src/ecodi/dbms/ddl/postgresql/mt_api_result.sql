-- Description: API 호출 결과 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_result
(
    api_url_id     CHAR(6) NOT NULL,
    result_seq     INTEGER NOT NULL,
    result_id      VARCHAR(20) NOT NULL,
    result_nm      VARCHAR(50) NOT NULL,
    data_type      VARCHAR(20),
    data_len       INTEGER,
    is_pk          CHAR(1) DEFAULT 'N',
    is_missing     CHAR(1) DEFAULT 'N',
    param_id       VARCHAR(50),
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_api_result_pkey PRIMARY KEY (api_url_id, result_seq)
);


COMMENT ON TABLE ecodi_meta.mt_api_result IS 'API 호출 결과';

COMMENT ON COLUMN mt_api_result.api_url_id IS 'API URL 아이디';
COMMENT ON COLUMN mt_api_result.result_seq IS '결과 순번';
COMMENT ON COLUMN mt_api_result.result_id IS '결과 변수';
COMMENT ON COLUMN mt_api_result.result_nm IS '결과 변수명';
COMMENT ON COLUMN mt_api_result.data_type IS '결과 데이터 유형';
COMMENT ON COLUMN mt_api_result.data_len IS '결과 데이터 길이';
COMMENT ON COLUMN mt_api_result.is_pk IS 'PK 여부';
COMMENT ON COLUMN mt_api_result.is_missing IS '결측치 여부';
COMMENT ON COLUMN mt_api_result.param_id IS '값에 사용할 파라미터변수';
COMMENT ON COLUMN mt_api_result.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_api_result.cret_nm IS '생성자';
COMMENT ON COLUMN mt_api_result.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_api_result.mdfy_nm IS '수정자';
