-- Description: 지역 메타 정보로서의 지역 데이터 읍면동 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_region_admi
(
    mega_cd    CHAR(2) NOT NULL,
    mega_nm    VARCHAR(20) NOT NULL,
    cty_cd     CHAR(5) NOT NULL,
    cty_nm     VARCHAR(20) NOT NULL,    
    admi_cd    CHAR(8) NOT NULL,
    admi_nm    VARCHAR(20) NOT NULL,        
    land_area  NUMERIC,
    cret_dt    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm    VARCHAR(20) NOT NULL,
    mdfy_dt    TIMESTAMP,
    mdfy_nm    VARCHAR(20),
    CONSTRAINT mt_region_admi_pkey PRIMARY KEY (admi_cd)
);

COMMENT ON TABLE ecodi_meta.mt_region_admi IS '지역 데이터 읍면동 정보';

COMMENT ON COLUMN mt_region_admi.mega_cd IS '시도 코드';
COMMENT ON COLUMN mt_region_admi.mega_nm IS '시도명';
COMMENT ON COLUMN mt_region_admi.cty_cd IS '시군구 코드';
COMMENT ON COLUMN mt_region_admi.cty_nm IS '시군구명';
COMMENT ON COLUMN mt_region_admi.admi_cd IS '읍면동 코드';
COMMENT ON COLUMN mt_region_admi.admi_nm IS '읍면동명';
COMMENT ON COLUMN mt_region_admi.land_area IS '면적';
COMMENT ON COLUMN mt_region_admi.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_region_admi.cret_nm IS '생성자';
COMMENT ON COLUMN mt_region_admi.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_region_admi.mdfy_nm IS '수정자';
