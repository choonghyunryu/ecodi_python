-- Description: DBMS 스키마 정보
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_schema_list
(
    schema_nm  VARCHAR(20) NOT NULL,
    schema_use VARCHAR(200) NOT NULL,    
    cret_dt    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm    VARCHAR(20) NOT NULL,
    mdfy_dt    TIMESTAMP,
    mdfy_nm    VARCHAR(20),
    CONSTRAINT mt_schema_list_pkey PRIMARY KEY (schema_nm)
);

COMMENT ON TABLE ecodi_meta.mt_schema_list IS 'DBMS 스키마 정보';

COMMENT ON COLUMN mt_schema_list.schema_nm IS 'DB 스키마명';
COMMENT ON COLUMN mt_schema_list.schema_use IS 'DB 스키마 용도';
COMMENT ON COLUMN mt_schema_list.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_schema_list.cret_nm IS '생성자';
COMMENT ON COLUMN mt_schema_list.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_schema_list.mdfy_nm IS '수정자';
