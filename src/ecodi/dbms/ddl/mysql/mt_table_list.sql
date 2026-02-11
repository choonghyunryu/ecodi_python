-- Description: 외부 데이터 테이블 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_list
(
    table_id           VARCHAR(50) NOT NULL            COMMENT '테이블 이름',
    schema_nm          VARCHAR(20) NOT NULL            COMMENT 'DB 스키마 명',
    data_id            CHAR(6) NOT NULL                COMMENT '데이터 아이디',        
    table_nm           VARCHAR(50) NOT NULL            COMMENT '테이블 논리명', 
    table_subclss      VARCHAR(20)                     COMMENT '테이블 서브 카테고리',
    pov_region         VARCHAR(20)                     COMMENT '지역관점',
    pov_age            VARCHAR(20)                     COMMENT '연령대 관점',
    table_desc         VARCHAR(200)                    COMMENT '비고',
    cret_dt            DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm            VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt            DATETIME                        COMMENT '수정일시',
    mdfy_nm            VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_table_list_pkey PRIMARY KEY (table_id)
);

ALTER TABLE ecodi_meta.mt_table_list COMMENT = '외부 데이터 테이블 정보';
