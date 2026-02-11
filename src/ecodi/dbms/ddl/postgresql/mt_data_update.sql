-- Description: 외부데이터 업데이트 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_update
(
    data_id             CHAR(6) NOT NULL,
    data_prvdr_cycle    VARCHAR(2) NOT NULL,
    data_base_pov       VARCHAR(20) NOT NULL,
    data_update_date    CHAR(10) NOT NULL,
    cret_dt             TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm             VARCHAR(20) NOT NULL,
    mdfy_dt             TIMESTAMP,
    mdfy_nm             VARCHAR(20),
    CONSTRAINT mt_data_update_pkey PRIMARY KEY (data_id, data_prvdr_cycle, data_base_pov)
);

COMMENT ON TABLE ecodi_meta.mt_data_update IS '외부 데이터 업데이트 정보';

COMMENT ON COLUMN mt_data_update.data_id IS '데이터 아이디';
COMMENT ON COLUMN mt_data_update.data_prvdr_cycle IS '데이터 제공 주기';
COMMENT ON COLUMN mt_data_update.data_base_pov IS '데이터 기준 시점';
COMMENT ON COLUMN mt_data_update.data_update_date IS '데이터 갱신 일자';
COMMENT ON COLUMN mt_data_update.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_data_update.cret_nm IS '생성자';
COMMENT ON COLUMN mt_data_update.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_data_update.mdfy_nm IS '수정자';
