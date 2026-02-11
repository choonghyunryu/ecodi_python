-- Description: 외부 데이터 항목 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_item
(
    data_id             CHAR(6) NOT NULL,
    data_item           VARCHAR(50) NOT NULL,
    data_item_nm        VARCHAR(50) NOT NULL,
    pov_region          VARCHAR(20),
    pov_age             VARCHAR(20),
    data_item_type      VARCHAR(20) NOT NULL,
    data_item_unit_clss VARCHAR(20),
    data_item_unit      INTEGER,
    data_item_desc      VARCHAR(200),
    cret_dt             TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm             VARCHAR(20) NOT NULL,
    mdfy_dt             TIMESTAMP,
    mdfy_nm             VARCHAR(20),
    CONSTRAINT mt_data_item_pkey PRIMARY KEY (data_id, data_item)
);

COMMENT ON TABLE ecodi_meta.mt_data_item IS '외부데이터 항목 정보';

COMMENT ON COLUMN mt_data_item.data_id IS '데이터 아이디';
COMMENT ON COLUMN mt_data_item.data_item IS '데이터 항목';
COMMENT ON COLUMN mt_data_item.data_item_nm IS '데이터 항목 명칭';
COMMENT ON COLUMN mt_data_item.pov_region IS '지역관점';
COMMENT ON COLUMN mt_data_item.pov_age IS '연령대 관점';
COMMENT ON COLUMN mt_data_item.data_item_type IS '데이터 형';
COMMENT ON COLUMN mt_data_item.data_item_unit_clss IS '데이터 항목 단위 명칭';
COMMENT ON COLUMN mt_data_item.data_item_unit IS '데이터 항목 단위';
COMMENT ON COLUMN mt_data_item.data_item_desc IS '데이터 항목 비고';
COMMENT ON COLUMN mt_data_item.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_data_item.cret_nm IS '생성자';
COMMENT ON COLUMN mt_data_item.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_data_item.mdfy_nm IS '수정자';
