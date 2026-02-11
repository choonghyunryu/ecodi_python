-- Description: 외부데이터 테이블 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_comment
(
    table_id            VARCHAR(50) NOT NULL            COMMENT '테이블 이름',
    comment_seq         INT NOT NULL                    COMMENT '주석 순번',
    table_comment       VARCHAR(2000)                   COMMENT '테이블 주석정보',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_table_comment_pkey PRIMARY KEY (table_id, comment_seq)
);

ALTER TABLE ecodi_meta.mt_table_comment COMMENT = '외부데이터 테이블 주석 정보';
