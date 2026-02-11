-- Description: KOSIS 지표설명 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_indexpl
(
    ind_id       VARCHAR(20) NOT NULL,
    ind_nm       VARCHAR(100) NOT NULL,
    ind_title    VARCHAR(100) NOT NULL,
    ind_define   VARCHAR(1000) NOT NULL,
    ind_exprsn   VARCHAR(1000) NOT NULL,
    ind_src      VARCHAR(100) NOT NULL,
    cret_dt      TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm      VARCHAR(20) NOT NULL,
    mdfy_dt      TIMESTAMP,
    mdfy_nm      VARCHAR(20),
    CONSTRAINT mt_kosis_indexpl_pkey PRIMARY KEY (ind_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_indexpl IS 'KOSIS 지표설명';

COMMENT ON COLUMN mt_kosis_indexpl.ind_id IS '지표ID';
COMMENT ON COLUMN mt_kosis_indexpl.ind_nm IS '지표명';
COMMENT ON COLUMN mt_kosis_indexpl.ind_title IS '설명자료 제목';
COMMENT ON COLUMN mt_kosis_indexpl.ind_define IS '지표개념';
COMMENT ON COLUMN mt_kosis_indexpl.ind_exprsn IS '산출방법';
COMMENT ON COLUMN mt_kosis_indexpl.ind_src IS '출처정보';
COMMENT ON COLUMN mt_kosis_indexpl.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_indexpl.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_indexpl.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_indexpl.mdfy_nm IS '수정자';
