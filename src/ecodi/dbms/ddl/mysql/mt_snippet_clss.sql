-- Description: 외부 데이터 스니펫 분류체계 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_snippet_clss
(
    snippet_clss        CHAR(6) NOT NULL                COMMENT '스니펫 분류체계',
    snippet_clss_nm     VARCHAR(20) NOT NULL            COMMENT '스니펫 분류체계 명칭',
    snippet_pclss       CHAR(3)                         COMMENT '스니펫 상위 분류체계',
    snippet_pclss_nm    VARCHAR(20)                     COMMENT '스니펫 상위 분류체계 명칭',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_snippet_clss_pkey PRIMARY KEY (snippet_clss)
);

ALTER TABLE ecodi_meta.mt_snippet_clss COMMENT = '외부 데이터 스니펫 분류체계';
