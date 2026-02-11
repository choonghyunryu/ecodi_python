-- Description: 외부데이터 테이블 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_comment
(
    table_id           VARCHAR(50) NOT NULL,
    comment_seq        INTEGER NOT NULL,
    table_comment      VARCHAR(2000),
    cret_dt            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm            VARCHAR(20) NOT NULL,
    mdfy_dt            TIMESTAMP,
    mdfy_nm            VARCHAR(20),
    CONSTRAINT mt_table_comment_pkey PRIMARY KEY (table_id, comment_seq)
);

COMMENT ON TABLE ecodi_meta.mt_table_comment IS '외부데이터 테이블 주석 정보';

COMMENT ON COLUMN mt_table_comment.table_id IS '테이블 이름';
COMMENT ON COLUMN mt_table_comment.comment_seq IS '주석 순번';
COMMENT ON COLUMN mt_table_comment.table_comment IS '테이블 주석정보';
COMMENT ON COLUMN mt_table_comment.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_table_comment.cret_nm IS '생성자';
COMMENT ON COLUMN mt_table_comment.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_table_comment.mdfy_nm IS '수정자';
