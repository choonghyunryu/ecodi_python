-- Description: KOSIS API 주기코드 및 시점 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_prdse
(
    prd_se      VARCHAR(20) NOT NULL,
    prd_desc    VARCHAR(20) NOT NULL,
    prd_cd      VARCHAR(2) NOT NULL,
    out_json    VARCHAR(2) NOT NULL,
    out_sdmx    VARCHAR(2) NOT NULL,
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_prdse_pkey PRIMARY KEY (prd_se)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_prdse IS 'KOSIS API 주기코드 및 시점';

COMMENT ON COLUMN mt_kosis_prdse.prd_se IS '집계주기';
COMMENT ON COLUMN mt_kosis_prdse.prd_desc IS '주기 설명';
COMMENT ON COLUMN mt_kosis_prdse.prd_cd IS '집계주기 코드';
COMMENT ON COLUMN mt_kosis_prdse.out_json IS '출력값_JSON';
COMMENT ON COLUMN mt_kosis_prdse.out_sdmx IS '출력값_SDMX';
COMMENT ON COLUMN mt_kosis_prdse.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_prdse.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_prdse.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_prdse.mdfy_nm IS '수정자';
