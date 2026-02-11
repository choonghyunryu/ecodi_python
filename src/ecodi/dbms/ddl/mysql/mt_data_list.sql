-- Description: 외부 데이터 목록 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_list
(
    data_id            CHAR(6) NOT NULL                COMMENT '데이터 아이디',
    raw_site_id        CHAR(6) NOT NULL                COMMENT '원천 사이트 아이디',
    api_url_id         CHAR(6)                         COMMENT 'API URL 아이디',
    data_nm            VARCHAR(50) NOT NULL            COMMENT '데이터 명칭',
    raw_table_id       VARCHAR(20) NOT NULL            COMMENT '원천 테이블 이름',
    raw_table_nm       VARCHAR(50) NOT NULL            COMMENT '원천 테이블 논리명',
    raw_schema_nm      VARCHAR(20) NOT NULL            COMMENT '원천 데이터 스키마명',
    site_page_url      VARCHAR(200)                    COMMENT '원천 사이트 페이지 URL',
    site_page_nm       VARCHAR(50)                     COMMENT '원천 사이트 페이지명',
    prvdr_nm           VARCHAR(50) NOT NULL            COMMENT '데이터 제공처명',
    prvdr_nm_eng       VARCHAR(50)                     COMMENT '데이터 제공처 영문명',
    prvdr_dept_nm      VARCHAR(50)                     COMMENT '데이터 제공처 부서명',
    prvdr_phone        VARCHAR(50)                     COMMENT '데이터 제공처 연락처',
    prvdr_cycle        VARCHAR(2) NOT NULL             COMMENT '데이터 제공 주기',
    data_end_pov       VARCHAR(20)                     COMMENT '데이터 종료시점',
    data_start_pov     VARCHAR(20)                     COMMENT '데이터 시작 시점',
    pov_region_mega    CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '지역_시도 집계 여부',
    pov_region_cty     CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '지역_시군구 집계 여부',
    pov_region_admi    CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '지역_읍면동 집계 여부',
    pov_age_lc         CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '연령대_생애주기 집계 여부',
    pov_age_10         CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '연령대_10세 집계 여부',
    pov_age_5          CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '연령대_5세 집계 여부',
    cret_dt            DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm            VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt            DATETIME                        COMMENT '수정일시',
    mdfy_nm            VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_data_list_pkey PRIMARY KEY (data_id)
);

ALTER TABLE ecodi_meta.mt_data_list COMMENT = '외부 데이터 목록';


