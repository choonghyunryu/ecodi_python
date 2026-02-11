-- Description: KOSIS 지표목록 계층구조 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_indlist
(
    ind_l_clss  CHAR(1) NOT NULL,
    ind_m_clss  VARCHAR(10) NOT NULL,
    ind_l_nm    VARCHAR(100) NOT NULL,
    ind_m_nm    VARCHAR(100) NOT NULL,
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_indlist_pkey PRIMARY KEY (ind_m_clss)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_indlist IS 'KOSIS 지표목록 계층구조';

COMMENT ON COLUMN mt_kosis_indlist.ind_l_clss IS '지표대분류 코드';
COMMENT ON COLUMN mt_kosis_indlist.ind_m_clss IS '지표중분류 코드';
COMMENT ON COLUMN mt_kosis_indlist.ind_l_nm IS '지표대분류명';
COMMENT ON COLUMN mt_kosis_indlist.ind_m_nm IS '지표중분류명';
COMMENT ON COLUMN mt_kosis_indlist.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_indlist.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_indlist.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_indlist.mdfy_nm IS '수정자';
