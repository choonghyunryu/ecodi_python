-- Description: 외부데이터 테이블 업데이트 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_update
(
    table_id           VARCHAR(50) NOT NULL,
    update_seq         INTEGER NOT NULL,
    prvdr_cycle        VARCHAR(2) NOT NULL,
    data_base_pov      VARCHAR(20) NOT NULL,
    update_date        CHAR(10) NOT NULL,
    cret_dt            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm            VARCHAR(20) NOT NULL,
    mdfy_dt            TIMESTAMP,
    mdfy_nm            VARCHAR(20),
    CONSTRAINT mt_table_update_pkey PRIMARY KEY (table_id, update_seq)
);

COMMENT ON TABLE ecodi_meta.mt_table_update IS '외부데이터 테이블 업데이트 정보';

COMMENT ON COLUMN mt_table_update.table_id IS '테이블 이름';
COMMENT ON COLUMN mt_table_update.update_seq IS '업데이트 순번';
COMMENT ON COLUMN mt_table_update.prvdr_cycle IS '데이터 제공 주기';
COMMENT ON COLUMN mt_table_update.data_base_pov IS '데이터 기준 시점';
COMMENT ON COLUMN mt_table_update.update_date IS '데이터 갱신 일자';
COMMENT ON COLUMN mt_table_update.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_table_update.cret_nm IS '생성자';
COMMENT ON COLUMN mt_table_update.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_table_update.mdfy_nm IS '수정자';
