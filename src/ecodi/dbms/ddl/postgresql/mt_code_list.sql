-- Description: 외부 데이터 코드 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_code_list
(
    code_id        CHAR(6) NOT NULL,
    code_nm        VARCHAR(20),
    code_clss      VARCHAR(10),
    code_seq       INTEGER,
    code_encode    VARCHAR(20),
    code_decode    VARCHAR(20),
    code_desc      VARCHAR(200),
    parent_id      CHAR(6),
    parent_encode  VARCHAR(20),
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_code_list_pkey PRIMARY KEY (code_id, code_encode)
);


COMMENT ON TABLE ecodi_meta.mt_code_list IS '외부 데이터 코드 정보';

COMMENT ON COLUMN mt_code_list.code_id IS '코드 ID';
COMMENT ON COLUMN mt_code_list.code_nm IS '코드 명칭';
COMMENT ON COLUMN mt_code_list.code_clss IS '코드 구분';
COMMENT ON COLUMN mt_code_list.code_seq IS '코드 순번';
COMMENT ON COLUMN mt_code_list.code_encode IS '코드 인코드';
COMMENT ON COLUMN mt_code_list.code_decode IS '코드 디코드';
COMMENT ON COLUMN mt_code_list.code_desc IS '코드 비고';
COMMENT ON COLUMN mt_code_list.parent_id IS '상위 코드 ID';
COMMENT ON COLUMN mt_code_list.parent_encode IS '상위 코드 인코드';
COMMENT ON COLUMN mt_code_list.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_code_list.cret_nm IS '생성자';
COMMENT ON COLUMN mt_code_list.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_code_list.mdfy_nm IS '수정자';
