-- Description: 외부 데이터 스니펫 분류체계 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_snippet_clss
(
    snippet_clss        CHAR(6) NOT NULL,
    snippet_clss_nm     VARCHAR(20) NOT NULL,
    snippet_pclss       CHAR(3),
    snippet_pclss_nm    VARCHAR(20),
    cret_dt             TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm             VARCHAR(20) NOT NULL,
    mdfy_dt             TIMESTAMP,
    mdfy_nm             VARCHAR(20),
    CONSTRAINT mt_snippet_clss_pkey PRIMARY KEY (snippet_clss)
);

COMMENT ON TABLE ecodi_meta.mt_snippet_clss IS '외부 데이터 스니펫 분류체계';

COMMENT ON COLUMN mt_snippet_clss.snippet_clss IS '스니펫 분류체계';
COMMENT ON COLUMN mt_snippet_clss.snippet_clss_nm IS '스니펫 분류체계 명칭';
COMMENT ON COLUMN mt_snippet_clss.snippet_pclss IS '스니펫 상위 분류체계';
COMMENT ON COLUMN mt_snippet_clss.snippet_pclss_nm IS '스니펫 상위 분류체계 명칭';
COMMENT ON COLUMN mt_snippet_clss.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_snippet_clss.cret_nm IS '생성자';
COMMENT ON COLUMN mt_snippet_clss.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_snippet_clss.mdfy_nm IS '수정자';
