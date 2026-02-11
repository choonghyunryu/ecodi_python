-- Description: 외부 데이터 테이블 컬럼 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_column
(
    table_id           VARCHAR(50) NOT NULL,
    column_seq         INTEGER NOT NULL,
    column_id          VARCHAR(50) NOT NULL,
    column_nm          VARCHAR(50) NOT NULL,
    code_id            VARCHAR(20),
    pov_region         VARCHAR(20),
    pov_age            VARCHAR(20),
    column_type        VARCHAR(20) NOT NULL,
    column_len         VARCHAR(10) NOT NULL,
    column_default     VARCHAR(50),
    column_null        CHAR(1) DEFAULT 'N' NOT NULL,
    column_pk          CHAR(1) DEFAULT 'N' NOT NULL,
    column_fk          CHAR(1) DEFAULT 'N' NOT NULL,
    column_clss        VARCHAR(20) NOT NULL,
    column_unit_clss   VARCHAR(20),
    column_unit        INTEGER,
    column_desc        VARCHAR(200),
    cret_dt            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm            VARCHAR(20) NOT NULL,
    mdfy_dt            TIMESTAMP,
    mdfy_nm            VARCHAR(20),
    CONSTRAINT mt_table_column_pkey PRIMARY KEY (table_id, column_seq)
);

COMMENT ON TABLE ecodi_meta.mt_table_column IS '외부 데이터 테이블 컬럼 정보';

COMMENT ON COLUMN mt_table_column.table_id IS '테이블 이름';
COMMENT ON COLUMN mt_table_column.column_seq IS '데이터컬럼 순번';
COMMENT ON COLUMN mt_table_column.column_id IS '데이터 컬럼';
COMMENT ON COLUMN mt_table_column.column_nm IS '데이터 컬럼 명칭';
COMMENT ON COLUMN mt_table_column.code_id IS '코드 ID';
COMMENT ON COLUMN mt_table_column.pov_region IS '지역관점';
COMMENT ON COLUMN mt_table_column.pov_age IS '연령대 관점';
COMMENT ON COLUMN mt_table_column.column_type IS '데이터 형';
COMMENT ON COLUMN mt_table_column.column_len IS '데이터 길이';
COMMENT ON COLUMN mt_table_column.column_default IS '데이터 기본값';
COMMENT ON COLUMN mt_table_column.column_null IS '널값 여부';
COMMENT ON COLUMN mt_table_column.column_pk IS 'PK 여부';
COMMENT ON COLUMN mt_table_column.column_fk IS 'FK 여부';
COMMENT ON COLUMN mt_table_column.column_clss IS '데이터 컬럼 구분';
COMMENT ON COLUMN mt_table_column.column_unit_clss IS '데이터 컬럼 단위 명칭';
COMMENT ON COLUMN mt_table_column.column_unit IS '데이터 컬럼 단위';
COMMENT ON COLUMN mt_table_column.column_desc IS '데이터 컬럼 비고';
COMMENT ON COLUMN mt_table_column.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_table_column.cret_nm IS '생성자';
COMMENT ON COLUMN mt_table_column.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_table_column.mdfy_nm IS '수정자';
