-- Description: 외부 데이터 원천 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_prvdr
(
    raw_site_id    CHAR(6) NOT NULL,
    raw_site_nm    VARCHAR(50) NOT NULL,
    raw_site_url   VARCHAR(50) NOT NULL,
    site_suplr_nm  VARCHAR(20) NOT NULL,
    site_org_cd    VARCHAR(10) NOT NULL,
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_data_prvdr_pkey PRIMARY KEY (raw_site_id)
);

COMMENT ON TABLE ecodi_meta.mt_data_prvdr IS '외부 데이터 원천 정보';

COMMENT ON COLUMN mt_data_prvdr.raw_site_id IS '원천 사이트 아이디';
COMMENT ON COLUMN mt_data_prvdr.raw_site_nm IS '원천 사이트 명칭';
COMMENT ON COLUMN mt_data_prvdr.raw_site_url IS '원천 사이트 URL';
COMMENT ON COLUMN mt_data_prvdr.site_suplr_nm IS '원천 사이트 공급처 명칭';
COMMENT ON COLUMN mt_data_prvdr.site_org_cd IS '공급처 민관 구분 코드';
COMMENT ON COLUMN mt_data_prvdr.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_data_prvdr.cret_nm IS '생성자';
COMMENT ON COLUMN mt_data_prvdr.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_data_prvdr.mdfy_nm IS '수정자';
