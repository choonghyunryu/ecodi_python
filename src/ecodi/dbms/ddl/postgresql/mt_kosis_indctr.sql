-- Description: KOSIS 지표목록 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_indctr
(
    ind_seq      INTEGER NOT NULL,
    ind_l_nm     VARCHAR(100) NOT NULL,
    ind_m_nm     VARCHAR(100) NOT NULL,
    ind_nm       VARCHAR(100) NOT NULL,
    ind_id       VARCHAR(20) NOT NULL,
    region_cls   VARCHAR(40) NOT NULL,
    pub_start_dt VARCHAR(40) NOT NULL,
    pub_end_dt   VARCHAR(40) NOT NULL,
    pub_period   VARCHAR(40) NOT NULL,
    explain_tf   VARCHAR(1) NOT NULL, 
    ind_m_clss   VARCHAR(10) NOT NULL,
    cret_dt      TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm      VARCHAR(20) NOT NULL,
    mdfy_dt      TIMESTAMP,
    mdfy_nm      VARCHAR(20),
    CONSTRAINT mt_kosis_indctr_pkey PRIMARY KEY (ind_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_indctr IS 'KOSIS 지표목록';

COMMENT ON COLUMN mt_kosis_indctr.ind_seq IS '순번';
COMMENT ON COLUMN mt_kosis_indctr.ind_l_nm IS '지표대분류명';
COMMENT ON COLUMN mt_kosis_indctr.ind_m_nm IS '지표중분류명';
COMMENT ON COLUMN mt_kosis_indctr.ind_nm IS '지표명';
COMMENT ON COLUMN mt_kosis_indctr.ind_id IS '지표ID';
COMMENT ON COLUMN mt_kosis_indctr.region_cls IS '지역구분';
COMMENT ON COLUMN mt_kosis_indctr.pub_start_dt IS '수록시작시점';
COMMENT ON COLUMN mt_kosis_indctr.pub_end_dt IS '수록종료시점';
COMMENT ON COLUMN mt_kosis_indctr.pub_period IS '수록주기';
COMMENT ON COLUMN mt_kosis_indctr.explain_tf IS '설명자료유무';
COMMENT ON COLUMN mt_kosis_indctr.ind_m_clss IS '지표중분류 코드';
COMMENT ON COLUMN mt_kosis_indctr.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_indctr.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_indctr.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_indctr.mdfy_nm IS '수정자';
