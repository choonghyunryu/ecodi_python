-- Description: DBMS 스키마 정보
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_schema_list
(
    schema_nm  VARCHAR(20) NOT NULL            COMMENT 'DB 스키마명',
    schema_use VARCHAR(200) NOT NULL           COMMENT 'DB 스키마 용도',    
    cret_dt    DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm    VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt    DATETIME                        COMMENT '수정일시',
    mdfy_nm    VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_schema_list_pkey PRIMARY KEY (schema_nm)
);

ALTER TABLE ecodi_meta.mt_schema_list COMMENT = 'DBMS 스키마 정보';
