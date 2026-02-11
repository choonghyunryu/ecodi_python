-- Description: KOSIS API 주기코드 및 시점 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_prdse
(
    prd_se      VARCHAR(20) NOT NULL            COMMENT '집계주기',
    prd_desc    VARCHAR(20) NOT NULL            COMMENT '주기 설명',
    prd_cd      VARCHAR(2) NOT NULL             COMMENT '집계주기 코드',
    out_json    VARCHAR(2) NOT NULL             COMMENT '출력값_JSON',
    out_sdmx    VARCHAR(2) NOT NULL             COMMENT '출력값_SDMX',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_prdse_pkey PRIMARY KEY (prd_se)
);

ALTER TABLE ecodi_meta.mt_kosis_prdse COMMENT = 'KOSIS API 주기코드 및 시점';

