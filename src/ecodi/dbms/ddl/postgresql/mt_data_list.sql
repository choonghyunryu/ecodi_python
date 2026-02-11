-- Description: 외부 데이터 목록 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_list
(
    data_id            CHAR(6) NOT NULL,
    raw_site_id        CHAR(6) NOT NULL,
    api_url_id         CHAR(6),
    data_nm            VARCHAR(50) NOT NULL,
    raw_table_id       VARCHAR(20) NOT NULL,
    raw_table_nm       VARCHAR(50) NOT NULL,
    raw_schema_nm      VARCHAR(20) NOT NULL,
    site_page_url      VARCHAR(200),
    site_page_nm       VARCHAR(50),
    prvdr_nm           VARCHAR(50) NOT NULL,
    prvdr_nm_eng       VARCHAR(50),
    prvdr_dept_nm      VARCHAR(50),
    prvdr_phone        VARCHAR(50),
    prvdr_cycle        VARCHAR(2) NOT NULL,
    data_end_pov       VARCHAR(20),
    data_start_pov     VARCHAR(20),
    pov_region_mega    CHAR(1) DEFAULT 'N' NOT NULL,
    pov_region_cty     CHAR(1) DEFAULT 'N' NOT NULL,
    pov_region_admi    CHAR(1) DEFAULT 'N' NOT NULL,
    pov_age_lc         CHAR(1) DEFAULT 'N' NOT NULL,
    pov_age_10         CHAR(1) DEFAULT 'N' NOT NULL,
    pov_age_5          CHAR(1) DEFAULT 'N' NOT NULL,
    cret_dt             TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm             VARCHAR(20) NOT NULL,
    mdfy_dt             TIMESTAMP,
    mdfy_nm             VARCHAR(20),
    CONSTRAINT mt_data_list_pkey PRIMARY KEY (data_id)
);

COMMENT ON TABLE ecodi_meta.mt_data_list IS '외부 데이터 목록';

COMMENT ON COLUMN mt_data_list.data_id IS '데이터 아이디';
COMMENT ON COLUMN mt_data_list.raw_site_id IS '원천 사이트 아이디';
COMMENT ON COLUMN mt_data_list.api_url_id IS 'API URL 아이디';
COMMENT ON COLUMN mt_data_list.data_nm IS '데이터 명칭';
COMMENT ON COLUMN mt_data_list.raw_table_id IS '원천 테이블 이름';
COMMENT ON COLUMN mt_data_list.raw_table_nm IS '원천 테이블 논리명';
COMMENT ON COLUMN mt_data_list.raw_schema_nm IS '원천 데이터 스키마명';
COMMENT ON COLUMN mt_data_list.site_page_url IS '원천 사이트 페이지 URL';
COMMENT ON COLUMN mt_data_list.site_page_nm IS '원천 사이트 페이지명';
COMMENT ON COLUMN mt_data_list.prvdr_nm IS '데이터 제공처명';
COMMENT ON COLUMN mt_data_list.prvdr_nm_eng IS '데이터 제공처 영문명';
COMMENT ON COLUMN mt_data_list.prvdr_dept_nm IS '데이터 제공처 부서명';
COMMENT ON COLUMN mt_data_list.prvdr_phone IS '데이터 제공처 연락처';
COMMENT ON COLUMN mt_data_list.prvdr_cycle IS '데이터 제공 주기';
COMMENT ON COLUMN mt_data_list.data_end_pov IS '데이터 종료시점';
COMMENT ON COLUMN mt_data_list.data_start_pov IS '데이터 시작 시점';
COMMENT ON COLUMN mt_data_list.pov_region_mega IS '지역_시도 집계 여부';
COMMENT ON COLUMN mt_data_list.pov_region_cty IS '지역_시군구 집계 여부';
COMMENT ON COLUMN mt_data_list.pov_region_admi IS '지역_읍면동 집계 여부';
COMMENT ON COLUMN mt_data_list.pov_age_lc IS '연령대_생애 집계 여부';
COMMENT ON COLUMN mt_data_list.pov_age_10 IS '연령대_10세 집계 여부';
COMMENT ON COLUMN mt_data_list.pov_age_5 IS '연령대_5세 집계 여부';
COMMENT ON COLUMN mt_data_list.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_data_list.cret_nm IS '생성자';
COMMENT ON COLUMN mt_data_list.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_data_list.mdfy_nm IS '수정자';
