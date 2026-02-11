-- Description: 외부 데이터 원천 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_prvdr
(
    raw_site_id    CHAR(6) NOT NULL                COMMENT '원천 사이트 아이디',
    raw_site_nm    VARCHAR(50) NOT NULL            COMMENT '원천 사이트 명칭',
    raw_site_url   VARCHAR(50) NOT NULL            COMMENT '원천 사이트 URL',
    site_suplr_nm  VARCHAR(20) NOT NULL            COMMENT '원천 사이트 공급처 명칭',
    site_org_cd    VARCHAR(10) NOT NULL            COMMENT '공급처 민관 구분 코드',
    cret_dt        DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm        VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt        DATETIME                        COMMENT '수정일시',
    mdfy_nm        VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_data_prvdr_pkey PRIMARY KEY (raw_site_id)
);

ALTER TABLE ecodi_meta.mt_data_prvdr COMMENT = '외부 데이터 원천 정보';
