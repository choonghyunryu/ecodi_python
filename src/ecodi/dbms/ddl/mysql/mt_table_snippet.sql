-- Description: 외부 데이터 테이블 스니펫 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_snippet
(
    table_id           VARCHAR(50) NOT NULL             COMMENT '테이블 이름',
    snippet_id         CHAR(6) NOT NULL                 COMMENT '스니펫 ID',
    snippet_nm         VARCHAR(50) NOT NULL             COMMENT '스니펫 명칭',
    snippet_func       VARCHAR(100) NOT NULL            COMMENT '스니펫 기능',
    snippet_func_clss  VARCHAR(10) NOT NULL             COMMENT '스니펫 기능 분류',
    snippet_clss       CHAR(6) NOT NULL                 COMMENT '스니펫 분류체계',
    snippet_param      VARCHAR(200) NOT NULL            COMMENT '스니펫 파라미터',
    snippet_def        VARCHAR(2000) NOT NULL           COMMENT '스니펫 정의',
    snippet_usage      VARCHAR(2000) NOT NULL           COMMENT '스니펫 사용 예제',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_table_snippet_pkey PRIMARY KEY (table_id, snippet_id)
);

ALTER TABLE ecodi_meta.mt_table_snippet COMMENT = '외부 데이터 테이블 스니펫';
