-- Description: API 호출 파라미터  값 목록 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_paramset
(
    data_id        CHAR(6) NOT NULL,
    api_url_id     CHAR(6) NOT NULL,
    param_seq      INTEGER NOT NULL,
    value_seq      INTEGER NOT NULL,
    value_set      VARCHAR(50),
    value_set_desc VARCHAR(200),
    parent_set     VARCHAR(50),    
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_api_paramset_pkey PRIMARY KEY (data_id, api_url_id, param_seq, value_seq)
);

COMMENT ON TABLE ecodi_meta.mt_api_paramset IS 'API 호출 파라미터 값 목록';

COMMENT ON COLUMN mt_api_paramset.data_id IS '데이터 아이디';
COMMENT ON COLUMN mt_api_paramset.api_url_id IS 'API URL 아이디';
COMMENT ON COLUMN mt_api_paramset.param_seq IS '파라미터 순번';
COMMENT ON COLUMN mt_api_paramset.value_seq IS '값 순번';
COMMENT ON COLUMN mt_api_paramset.value_set IS '값 목록';
COMMENT ON COLUMN mt_api_paramset.value_set_desc IS '값 목록 내용';
COMMENT ON COLUMN mt_api_paramset.parent_set IS '상위 파라미터 값';
COMMENT ON COLUMN mt_api_paramset.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_api_paramset.cret_nm IS '생성자';
COMMENT ON COLUMN mt_api_paramset.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_api_paramset.mdfy_nm IS '수정자';