-- Description: 외부데이터 테이블 분류 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_clss
(
    table_id            VARCHAR(50) NOT NULL            COMMENT '테이블 이름',
    clss_seq            INT NOT NULL                    COMMENT '분류 순번',
    table_clss          CHAR(3) NOT NULL                COMMENT '테이블 분류',
    table_subclss       CHAR(6) NOT NULL                COMMENT '테이블 세부 분류',
    table_clss_nm       VARCHAR(100) NOT NULL           COMMENT '테이블 분류명',
    table_subclss_nm    VARCHAR(100) NOT NULL           COMMENT '테이블 세부 분류명',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_table_clss_pkey PRIMARY KEY (table_id, clss_seq, table_subclss)
);

ALTER TABLE ecodi_meta.mt_table_clss COMMENT = '외부데이터 테이블 분류 정보';


