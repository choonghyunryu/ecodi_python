-- Description: KOSIS 통계목록 계층구조 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_stat
(
    parent_id   VARCHAR(50) DEFAULT '' NOT NULL,
    vw_cd       VARCHAR(40) NOT NULL,
    vw_nm       VARCHAR(300) NOT NULL,
    list_id     VARCHAR(40) DEFAULT '' NOT NULL,
    list_nm     VARCHAR(300),
    org_id      VARCHAR(40),
    tbl_id      VARCHAR(40) DEFAULT '' NOT NULL,
    tbl_nm      VARCHAR(300),
    stat_id     VARCHAR(40) NOT NULL,
    send_de     VARCHAR(10),
    rec_tbl_se  VARCHAR(10),
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_stat_pkey PRIMARY KEY (parent_id, vw_cd, list_id, tbl_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_stat IS 'KOSIS 통계목록 계층구조';

COMMENT ON COLUMN mt_kosis_stat.parent_id IS '시작목록 ID';
COMMENT ON COLUMN mt_kosis_stat.vw_cd IS '서비스뷰 ID';
COMMENT ON COLUMN mt_kosis_stat.vw_nm IS '서비스뷰명';
COMMENT ON COLUMN mt_kosis_stat.list_id IS '목록 ID';
COMMENT ON COLUMN mt_kosis_stat.list_nm IS '목록명';
COMMENT ON COLUMN mt_kosis_stat.org_id IS '제공기관 코드';
COMMENT ON COLUMN mt_kosis_stat.tbl_id IS '통계표 ID';
COMMENT ON COLUMN mt_kosis_stat.tbl_nm IS '통계표명';
COMMENT ON COLUMN mt_kosis_stat.stat_id IS '통계조사 ID';
COMMENT ON COLUMN mt_kosis_stat.send_de IS '최종갱신일';
COMMENT ON COLUMN mt_kosis_stat.rec_tbl_se IS '추천 통계표 여부';
COMMENT ON COLUMN mt_kosis_stat.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_stat.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_stat.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_stat.mdfy_nm IS '수정자';
