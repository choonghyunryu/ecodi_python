-- Description: KOSIS 데이터 집계 주기/기간 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_prd
(
    tbl_id      VARCHAR(40) NOT NULL,
    org_id      VARCHAR(40) NOT NULL, 
    prd_cd      VARCHAR(2) NOT NULL,
    prd_se      VARCHAR(10) NOT NULL,
    strt_prd_de VARCHAR(20) NOT NULL,
    end_prd_de  VARCHAR(20) NOT NULL,
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_prd_pkey PRIMARY KEY (tbl_id, org_id, prd_se)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_prd IS 'KOSIS 데이터 집계 주기/기간 정보';

COMMENT ON COLUMN mt_kosis_prd.tbl_id IS '통계표 ID';
COMMENT ON COLUMN mt_kosis_prd.org_id IS '제공기관 코드';
COMMENT ON COLUMN mt_kosis_prd.prd_cd IS '집계주기 코드';
COMMENT ON COLUMN mt_kosis_prd.prd_se IS '집계주기';
COMMENT ON COLUMN mt_kosis_prd.strt_prd_de IS '집계 시작 기간';
COMMENT ON COLUMN mt_kosis_prd.end_prd_de IS '집계 종료 기간';
COMMENT ON COLUMN mt_kosis_prd.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_prd.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_prd.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_prd.mdfy_nm IS '수정자';
