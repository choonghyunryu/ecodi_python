-- Description: 외부 데이터 테이블 컬럼 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_column
(
    table_id           VARCHAR(50) NOT NULL            COMMENT '테이블 이름',
    column_seq         INT NOT NULL                    COMMENT '데이터컬럼 순번',
    column_id          VARCHAR(50) NOT NULL            COMMENT '데이터 컬럼',
    column_nm          VARCHAR(50) NOT NULL            COMMENT '데이터 컬럼 명칭',
    code_id            VARCHAR(20)                     COMMENT '코드 ID',
    pov_region         VARCHAR(20)                     COMMENT '지역관점',
    pov_age            VARCHAR(20)                     COMMENT '연령대 관점',
    column_type        VARCHAR(20) NOT NULL            COMMENT '데이터 형',
    column_len         VARCHAR(10) NOT NULL            COMMENT '데이터 길이',
    column_default     VARCHAR(50)                     COMMENT '데이터 기본값',
    column_null        CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '널값 여부',
    column_pk          CHAR(1) DEFAULT 'N' NOT NULL    COMMENT 'PK 여부',
    column_fk          CHAR(1) DEFAULT 'N' NOT NULL    COMMENT 'FK 여부',
    column_clss        VARCHAR(20) NOT NULL            COMMENT '데이터 컬럼 구분',
    column_unit_clss   VARCHAR(20)                     COMMENT '데이터 컬럼 단위 명칭',
    column_unit        INT                             COMMENT '데이터 컬럼 단위',
    column_desc        VARCHAR(200)                    COMMENT '데이터 컬럼 비고',
    cret_dt            DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm            VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt            DATETIME                        COMMENT '수정일시',
    mdfy_nm            VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_table_column_pkey PRIMARY KEY (table_id, column_seq)
);

ALTER TABLE ecodi_meta.mt_table_column COMMENT = '외부 데이터 테이블 컬럼 정보';


