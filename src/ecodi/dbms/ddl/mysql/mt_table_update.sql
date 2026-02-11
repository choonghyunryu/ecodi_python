-- Description: 외부데이터 테이블 업데이트 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_update
(
    table_id           VARCHAR(50) NOT NULL            COMMENT '테이블 이름',
    update_seq         INT NOT NULL                    COMMENT '업데이트 순번',
    prvdr_cycle        VARCHAR(2) NOT NULL             COMMENT '데이터 제공 주기',
    data_base_pov      VARCHAR(20) NOT NULL            COMMENT '데이터 기준 시점',
    update_date        CHAR(10) NOT NULL               COMMENT '데이터 갱신 일자',
    cret_dt            DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm            VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt            DATETIME                        COMMENT '수정일시',
    mdfy_nm            VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_table_update_pkey PRIMARY KEY (table_id, update_seq)
);

