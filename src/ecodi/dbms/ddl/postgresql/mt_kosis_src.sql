-- Description: KOSIS 데이터 출처 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_src
(
    tbl_id      VARCHAR(40) NOT NULL,
    org_id      VARCHAR(40) NOT NULL, 
    stat_id     VARCHAR(40) NOT NULL,
    josa_nm     VARCHAR(100),
    dept_phone  VARCHAR(40),
    dept_nm     VARCHAR(100),
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_src_pkey PRIMARY KEY (tbl_id, org_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_src IS 'KOSIS 데이터 출처 정보';

COMMENT ON COLUMN mt_kosis_src.tbl_id IS '통계표 ID';
COMMENT ON COLUMN mt_kosis_src.org_id IS '제공기관 코드';
COMMENT ON COLUMN mt_kosis_src.stat_id IS '통계조사 ID';
COMMENT ON COLUMN mt_kosis_src.josa_nm IS '출처 명칭';
COMMENT ON COLUMN mt_kosis_src.dept_phone IS '출처 전화번호';
COMMENT ON COLUMN mt_kosis_src.dept_nm IS '제공 부서';
COMMENT ON COLUMN mt_kosis_src.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_src.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_src.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_src.mdfy_nm IS '수정자';
