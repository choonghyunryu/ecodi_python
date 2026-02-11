-- Description: KOSIS 통계목록 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_statbl
(
    org_id      VARCHAR(40),
    tbl_id      VARCHAR(40) NOT NULL,
    tbl_nm      VARCHAR(300),
    perent_id   VARCHAR(50) NOT NULL,
    vw_cd       VARCHAR(40) NOT NULL,
    vw_nm       VARCHAR(300) NOT NULL,    
    stat_id     VARCHAR(40) NOT NULL,
    send_de     VARCHAR(10),
    rec_tbl_se  VARCHAR(10),
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_statbl_pkey PRIMARY KEY (org_id, tbl_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_statbl IS 'KOSIS 통계목록';

COMMENT ON COLUMN mt_kosis_statbl.org_id IS '제공기관 코드';
COMMENT ON COLUMN mt_kosis_statbl.tbl_id IS '통계표 ID';
COMMENT ON COLUMN mt_kosis_statbl.tbl_nm IS '통계표명';
COMMENT ON COLUMN mt_kosis_statbl.perent_id IS '시작목록 ID';
COMMENT ON COLUMN mt_kosis_statbl.vw_cd IS '서비스뷰 ID';
COMMENT ON COLUMN mt_kosis_statbl.vw_nm IS '서비스뷰명';
COMMENT ON COLUMN mt_kosis_statbl.stat_id IS '통계조사 ID';
COMMENT ON COLUMN mt_kosis_statbl.send_de IS '최종갱신일';
COMMENT ON COLUMN mt_kosis_statbl.rec_tbl_se IS '추천 통계표 여부';
COMMENT ON COLUMN mt_kosis_statbl.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_statbl.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_statbl.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_statbl.mdfy_nm IS '수정자';
