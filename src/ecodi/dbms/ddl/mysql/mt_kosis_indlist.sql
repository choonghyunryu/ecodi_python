-- Description: KOSIS 지표목록 계층구조 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_indlist
(
    ind_l_clss  CHAR(1) NOT NULL                COMMENT '지표대분류 코드',
    ind_m_clss  VARCHAR(10) NOT NULL            COMMENT '지표중분류 코드',
    ind_l_nm    VARCHAR(100) NOT NULL           COMMENT '지표대분류명',
    ind_m_nm   VARCHAR(100) NOT NULL            COMMENT '지표중분류명',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_indlist_pkey PRIMARY KEY (ind_m_clss)
);

ALTER TABLE ecodi_meta.mt_kosis_indlist COMMENT = 'KOSIS 지표목록 계층구조';
