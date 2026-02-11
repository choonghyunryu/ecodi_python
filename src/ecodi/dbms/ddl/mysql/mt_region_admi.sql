-- Description: 지역 메타 정보로서의 지역 데이터 읍면동 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_region_admi
(
    mega_cd             CHAR(2) NOT NULL                COMMENT '시도 코드',
    mega_nm             VARCHAR(20) NOT NULL            COMMENT '시도명',
    cty_cd              CHAR(5) NOT NULL                COMMENT '시군구 코드',
    cty_nm              VARCHAR(20) NOT NULL            COMMENT '시군구명',    
    admi_cd             CHAR(8) NOT NULL                COMMENT '읍면동 코드',
    admi_nm             VARCHAR(20) NOT NULL            COMMENT '읍면동명',        
    land_area           DOUBLE NOT NULL                 COMMENT '면적',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_region_admi_pkey PRIMARY KEY (admi_cd)
);

ALTER TABLE ecodi_meta.mt_region_admi COMMENT = '지역 데이터 읍면동 정보';
