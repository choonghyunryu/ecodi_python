-- Description: 외부데이터 테이블 분류 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_clss
(
    table_id            VARCHAR(50) NOT NULL,
    clss_seq            INTEGER NOT NULL,
    table_clss          CHAR(3) NOT NULL,
    table_subclss       CHAR(6) NOT NULL,
    table_clss_nm       VARCHAR(100) NOT NULL,
    table_subclss_nm    VARCHAR(100) NOT NULL,
    cret_dt             TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm             VARCHAR(20) NOT NULL,
    mdfy_dt             TIMESTAMP,
    mdfy_nm             VARCHAR(20),
    CONSTRAINT mt_table_clss_pkey PRIMARY KEY (table_id, clss_seq, table_subclss)
);

COMMENT ON TABLE ecodi_meta.mt_table_clss IS '외부데이터 테이블 분류 정보';

COMMENT ON COLUMN mt_table_clss.table_id IS '테이블 이름';
COMMENT ON COLUMN mt_table_clss.clss_seq IS '분류 순번';
COMMENT ON COLUMN mt_table_clss.table_clss IS '테이블 분류';
COMMENT ON COLUMN mt_table_clss.table_subclss IS '테이블 세부 분류';
COMMENT ON COLUMN mt_table_clss.table_clss_nm IS '테이블 분류명';
COMMENT ON COLUMN mt_table_clss.table_subclss_nm IS '테이블 세부 분류명';
COMMENT ON COLUMN mt_table_clss.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_table_clss.cret_nm IS '생성자';
COMMENT ON COLUMN mt_table_clss.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_table_clss.mdfy_nm IS '수정자';
