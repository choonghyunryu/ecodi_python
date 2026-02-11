-- Description: 외부 데이터 항목 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_item
(
    data_id             CHAR(6) NOT NULL                COMMENT '데이터 아이디',
    data_item           VARCHAR(50) NOT NULL            COMMENT '데이터 항목',
    data_item_nm        VARCHAR(50) NOT NULL            COMMENT '데이터 항목 명칭',
    pov_region          VARCHAR(20)                     COMMENT '지역관점',
    pov_age             VARCHAR(20)                     COMMENT '연령대 관점',
    data_item_type      VARCHAR(20) NOT NULL            COMMENT '데이터 형',
    data_item_unit_clss VARCHAR(20)                     COMMENT '데이터 항목 단위 명칭',
    data_item_unit      INT                             COMMENT '데이터 항목 단위',
    data_item_desc      VARCHAR(200)                    COMMENT '데이터 항목 비고',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_data_item_pkey PRIMARY KEY (data_id, data_item)
);

ALTER TABLE ecodi_meta.mt_data_item COMMENT = '외부 데이터 항목 정보';
