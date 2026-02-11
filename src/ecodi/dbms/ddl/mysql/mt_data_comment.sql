-- Description: 외부데이터 주석 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_comment
(
    data_id             CHAR(6) NOT NULL                COMMENT '데이터 아이디',
    data_comment        VARCHAR(2000)                   COMMENT '데이터 기준 시점',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_data_comment_pkey PRIMARY KEY (data_id)
);

ALTER TABLE ecodi_meta.mt_data_comment COMMENT = '외부데이터 주석 정보';
