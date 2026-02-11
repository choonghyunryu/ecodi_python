-- Description: 외부데이터 업데이트 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_update
(
    data_id             CHAR(6) NOT NULL                COMMENT '데이터 아이디',
    data_prvdr_cycle    VARCHAR(2) NOT NULL             COMMENT '데이터 제공 주기',
    data_base_pov       VARCHAR(20) NOT NULL            COMMENT '데이터 기준 시점',
    data_update_date    CHAR(10) NOT NULL               COMMENT '데이터 갱신 일자',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_data_update_pkey PRIMARY KEY (data_id, data_prvdr_cycle, data_base_pov)
);

ALTER TABLE ecodi_meta.mt_data_update COMMENT = '외부데이터 업데이트 정보';
