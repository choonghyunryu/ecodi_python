-- Description: 외부 데이터 테이블 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_list
(
    table_id           VARCHAR(50) NOT NULL,
    schema_nm          VARCHAR(20) NOT NULL,
    data_id            CHAR(6) NOT NULL,        
    table_nm           VARCHAR(50) NOT NULL, 
    table_subclss      VARCHAR(20),
    pov_region         VARCHAR(20),
    pov_age            VARCHAR(20),
    table_desc         VARCHAR(200),
    cret_dt            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm            VARCHAR(20) NOT NULL,
    mdfy_dt            TIMESTAMP,
    mdfy_nm            VARCHAR(20),
    CONSTRAINT mt_table_list_pkey PRIMARY KEY (table_id)
);

COMMENT ON TABLE ecodi_meta.mt_table_list IS '외부 데이터 테이블 정보';

COMMENT ON COLUMN mt_table_list.table_id IS '테이블 이름';
COMMENT ON COLUMN mt_table_list.schema_nm IS 'DB 스키마 명';
COMMENT ON COLUMN mt_table_list.data_id IS '데이터 아이디';
COMMENT ON COLUMN mt_table_list.table_nm IS '테이블 논리명';
COMMENT ON COLUMN mt_table_list.table_subclss IS '테이블 서브 카테고리';
COMMENT ON COLUMN mt_table_list.pov_region IS '지역관점';
COMMENT ON COLUMN mt_table_list.pov_age IS '연령대 관점';
COMMENT ON COLUMN mt_table_list.table_desc IS '비고';
COMMENT ON COLUMN mt_table_list.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_table_list.cret_nm IS '생성자';
COMMENT ON COLUMN mt_table_list.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_table_list.mdfy_nm IS '수정자';
