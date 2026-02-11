-- Description: API 호출 파라미터 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_param
(
    api_url_id     CHAR(6) NOT NULL,
    param_seq      INT NOT NULL,
    param_id       VARCHAR(50) NOT NULL,
    param_nm       VARCHAR(50) NOT NULL,
    default_value  VARCHAR(50),
    is_must        CHAR(1) DEFAULT 'Y' NOT NULL,
    is_key         CHAR(1) DEFAULT 'N' NOT NULL,
    is_constant    CHAR(1) DEFAULT 'N' NOT NULL,
    is_list        CHAR(1) DEFAULT 'Y' NOT NULL,
    parent_seq     INTEGER,
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_api_param_pkey PRIMARY KEY (api_url_id, param_seq)
);


COMMENT ON TABLE ecodi_meta.mt_api_param IS 'API 호출 파라미터';

COMMENT ON COLUMN mt_api_param.api_url_id IS 'API URL 아이디';
COMMENT ON COLUMN mt_api_param.param_seq IS '파라미터 순번';
COMMENT ON COLUMN mt_api_param.param_id IS '파라미터';
COMMENT ON COLUMN mt_api_param.param_nm IS '파라미터 명칭';
COMMENT ON COLUMN mt_api_param.default_value IS '기본 설정값';
COMMENT ON COLUMN mt_api_param.is_must IS '필수 파라미터 여부';
COMMENT ON COLUMN mt_api_param.is_key IS 'API Key 파라미터 여부';
COMMENT ON COLUMN mt_api_param.is_constant IS '파라미터값 상수여부';
COMMENT ON COLUMN mt_api_param.is_list IS '파라미터값 목록여부';
COMMENT ON COLUMN mt_api_param.parent_seq IS '상위 파라미터 순번';
COMMENT ON COLUMN mt_api_param.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_api_param.cret_nm IS '생성자';
COMMENT ON COLUMN mt_api_param.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_api_param.mdfy_nm IS '수정자';
