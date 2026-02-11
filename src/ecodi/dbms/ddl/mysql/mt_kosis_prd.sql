-- Description: KOSIS 데이터 집계 주기/기간 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_prd
(
    tbl_id      VARCHAR(40) NOT NULL            COMMENT '통계표 ID',
    org_id      VARCHAR(40) NOT NULL            COMMENT '제공기관 코드', 
    prd_cd      VARCHAR(2) NOT NULL             COMMENT '집계주기 코드',
    prd_se      VARCHAR(10) NOT NULL            COMMENT '집계주기',
    strt_prd_de VARCHAR(20) NOT NULL            COMMENT '집계 시작 기간',
    end_prd_de  VARCHAR(20) NOT NULL            COMMENT '집계 종료 기간',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_prd_pkey PRIMARY KEY (tbl_id, org_id, prd_se)
);

ALTER TABLE ecodi_meta.mt_kosis_prd COMMENT = 'KOSIS 데이터 집계 주기/기간 정보';
