-- Description: 외부 데이터 테이블 스니펫 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_snippet
(
    table_id           VARCHAR(50) NOT NULL,
    snippet_id         CHAR(6) NOT NULL,
    snippet_nm         VARCHAR(50) NOT NULL,
    snippet_func       VARCHAR(100) NOT NULL,
    snippet_func_clss  VARCHAR(10) NOT NULL,
    snippet_clss       CHAR(6) NOT NULL,
    snippet_param      VARCHAR(200) NOT NULL,
    snippet_def        VARCHAR(2000) NOT NULL,
    snippet_usage      VARCHAR(2000) NOT NULL,
    cret_dt            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm            VARCHAR(20) NOT NULL,
    mdfy_dt            TIMESTAMP,
    mdfy_nm            VARCHAR(20),
    CONSTRAINT mt_table_snippet_pkey PRIMARY KEY (table_id, snippet_id)
);

COMMENT ON TABLE ecodi_meta.mt_table_snippet IS '외부 데이터 테이블 스니펫';

COMMENT ON COLUMN mt_table_snippet.table_id IS '테이블 이름';
COMMENT ON COLUMN mt_table_snippet.snippet_id IS '스니펫 ID';
COMMENT ON COLUMN mt_table_snippet.snippet_nm IS '스니펫 명칭';
COMMENT ON COLUMN mt_table_snippet.snippet_func IS '스니펫 기능';
COMMENT ON COLUMN mt_table_snippet.snippet_func_clss IS '스니펫 기능 분류';
COMMENT ON COLUMN mt_table_snippet.snippet_clss IS '스니펫 분류체계';
COMMENT ON COLUMN mt_table_snippet.snippet_param IS '스니펫 파라미터';
COMMENT ON COLUMN mt_table_snippet.snippet_def IS '스니펫 정의';
COMMENT ON COLUMN mt_table_snippet.snippet_usage IS '스니펫 사용 예제';
COMMENT ON COLUMN mt_table_snippet.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_table_snippet.cret_nm IS '생성자';
COMMENT ON COLUMN mt_table_snippet.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_table_snippet.mdfy_nm IS '수정자';
