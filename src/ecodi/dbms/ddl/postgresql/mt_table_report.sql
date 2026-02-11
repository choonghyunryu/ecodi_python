-- Description: 외부 데이터 테이블 레포트 활용 사례 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_table_report
(
    table_id           VARCHAR(50) NOT NULL,
    report_id          CHAR(6) NOT NULL,
    report_seq         INTEGER NOT NULL,
    report_nm          VARCHAR(50) NOT NULL,
    publish_date       VARCHAR(10) NOT NULL,
    abstract           VARCHAR(1000) NOT NULL,
    file_name          VARCHAR(50) NOT NULL,
    reg_menu           VARCHAR(50) NOT NULL,
    reg_url            VARCHAR(500) NOT NULL,
    store_path         VARCHAR(2000) NOT NULL,
    usage_name         VARCHAR(50),
    usage_desc         VARCHAR(200),
    usage_sql          VARCHAR(2000),
    cret_dt            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm            VARCHAR(20) NOT NULL,
    mdfy_dt            TIMESTAMP,
    mdfy_nm            VARCHAR(20),
    CONSTRAINT mt_table_report_pkey PRIMARY KEY (table_id, report_id, report_seq)
);

COMMENT ON TABLE ecodi_meta.mt_table_report IS '외부 데이터 테이블 레포트 활용 사례';

COMMENT ON COLUMN mt_table_report.table_id IS '테이블 이름';
COMMENT ON COLUMN mt_table_report.report_id IS '레포트 ID';
COMMENT ON COLUMN mt_table_report.report_seq IS '순번';
COMMENT ON COLUMN mt_table_report.report_nm IS '레포트 명칭';
COMMENT ON COLUMN mt_table_report.publish_date IS '레포트 발행일자';
COMMENT ON COLUMN mt_table_report.abstract IS '레포트 초록';
COMMENT ON COLUMN mt_table_report.file_name IS '레포트 파일명';
COMMENT ON COLUMN mt_table_report.reg_menu IS '레포트 파일 게시 메뉴 경로';
COMMENT ON COLUMN mt_table_report.reg_url IS '레포트 게시 URL';
COMMENT ON COLUMN mt_table_report.store_path IS '레포트 파일 적재 디렉토리 경로';
COMMENT ON COLUMN mt_table_report.usage_name IS '데이터 사용 이름';
COMMENT ON COLUMN mt_table_report.usage_desc IS '데이터 사용 개요';
COMMENT ON COLUMN mt_table_report.usage_sql IS '데이터 사용 SQL';
COMMENT ON COLUMN mt_table_report.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_table_report.cret_nm IS '생성자';
COMMENT ON COLUMN mt_table_report.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_table_report.mdfy_nm IS '수정자';
