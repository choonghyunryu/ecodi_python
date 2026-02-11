-- Description: KOSIS 지표목록 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_indctr
(
    ind_seq      INT NOT NULL                    COMMENT '순번',
    ind_l_nm     VARCHAR(100) NOT NULL           COMMENT '지표대분류명',
    ind_m_nm     VARCHAR(100) NOT NULL           COMMENT '지표중분류명',
    ind_nm       VARCHAR(100) NOT NULL           COMMENT '지표명',
    ind_id       VARCHAR(20) NOT NULL            COMMENT '지표ID',
    region_cls   VARCHAR(40) NOT NULL            COMMENT '지역구분',
    pub_start_dt VARCHAR(40) NOT NULL            COMMENT '수록시작시점',
    pub_end_dt   VARCHAR(40) NOT NULL            COMMENT '수록종료시점',
    pub_period   VARCHAR(40) NOT NULL            COMMENT '수록주기',
    explain_tf   VARCHAR(1) NOT NULL             COMMENT '설명자료유무', 
    ind_m_clss   VARCHAR(10) NOT NULL            COMMENT '지표중분류 코드',
    cret_dt      DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm      VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt      DATETIME                        COMMENT '수정일시',
    mdfy_nm      VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_indctr_pkey PRIMARY KEY (ind_id)
);

ALTER TABLE ecodi_meta.mt_kosis_indctr COMMENT = 'KOSIS 지표목록';
