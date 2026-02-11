-- Description: KOSIS 데이터 명칭 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_tbl
(
    tbl_id      VARCHAR(40) NOT NULL,
    org_id      VARCHAR(40) NOT NULL,  
    tbl_nm      VARCHAR(300) NOT NULL,
    tbl_nm_eng  VARCHAR(300) NOT NULL,
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_tbl_pkey PRIMARY KEY (tbl_id, org_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_tbl IS 'KOSIS 데이터 명칭 정보';

COMMENT ON COLUMN mt_kosis_tbl.tbl_id IS '통계표 ID';
COMMENT ON COLUMN mt_kosis_tbl.org_id IS '제공기관 코드';
COMMENT ON COLUMN mt_kosis_tbl.tbl_nm IS '데이터 명칭';
COMMENT ON COLUMN mt_kosis_tbl.tbl_nm_eng IS '데이터 명칭 영문명';
COMMENT ON COLUMN mt_kosis_tbl.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_tbl.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_tbl.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_tbl.mdfy_nm IS '수정자';
