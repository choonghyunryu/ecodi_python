-- Description: 외부 데이터 테이블 레포트 활용 사례 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_report
(
    table_id           VARCHAR(50) NOT NULL            COMMENT '테이블 이름',
    report_id          CHAR(6) NOT NULL                COMMENT '레포트 ID',
    report_seq         INT NOT NULL                    COMMENT '순번',
    report_nm          VARCHAR(50) NOT NULL            COMMENT '레포트 명칭',
    publish_date       VARCHAR(10) NOT NULL            COMMENT '레포트 발행일자',
    abstract           VARCHAR(1000) NOT NULL          COMMENT '레포트 초록',
    file_name          VARCHAR(50) NOT NULL            COMMENT '레포트 파일명',
    reg_menu           VARCHAR(50) NOT NULL            COMMENT '레포트 파일 게시 메뉴 경로',
    reg_url            VARCHAR(500) NOT NULL           COMMENT '레포트 게시 URL',
    store_path         VARCHAR(2000) NOT NULL          COMMENT '레포트 파일 적재 디렉토리 경로',
    usage_name         VARCHAR(50)                     COMMENT '데이터 사용 이름',
    usage_desc         VARCHAR(200)                    COMMENT '데이터 사용 개요',
    usage_sql          VARCHAR(2000)                   COMMENT '데이터 사용 SQL',
    cret_dt            DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm            VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt            DATETIME                        COMMENT '수정일시',
    mdfy_nm            VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_table_report_pkey PRIMARY KEY (table_id, report_id, report_seq)
);

ALTER TABLE ecodi_meta.mt_table_report COMMENT = '외부 데이터 테이블 레포트 활용 사례';
