-- Description: 지역 메타 정보로서의 지역 데이터 시군구 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_region_cty
(
    mega_cd    CHAR(2) NOT NULL,
    mega_nm    VARCHAR(20) NOT NULL,
    cty_cd     CHAR(5) NOT NULL,
    cty_nm     VARCHAR(20) NOT NULL,    
    land_area  NUMERIC,
    cret_dt    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm    VARCHAR(20) NOT NULL,
    mdfy_dt    TIMESTAMP,
    mdfy_nm    VARCHAR(20),
    CONSTRAINT mt_region_cty_pkey PRIMARY KEY (cty_cd)
);

COMMENT ON TABLE ecodi_meta.mt_region_cty IS '지역 데이터 시군구 정보';

COMMENT ON COLUMN mt_region_cty.mega_cd IS '시도 코드';
COMMENT ON COLUMN mt_region_cty.mega_nm IS '시도명';
COMMENT ON COLUMN mt_region_cty.cty_cd IS '시군구 코드';
COMMENT ON COLUMN mt_region_cty.cty_nm IS '시군구명';
COMMENT ON COLUMN mt_region_cty.land_area IS '면적';
COMMENT ON COLUMN mt_region_cty.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_region_cty.cret_nm IS '생성자';
COMMENT ON COLUMN mt_region_cty.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_region_cty.mdfy_nm IS '수정자';