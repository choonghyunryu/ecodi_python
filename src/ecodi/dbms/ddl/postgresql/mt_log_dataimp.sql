-- Description: 데이터 수집/통합 로그
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_log_dataimp
(
    user_id    VARCHAR(20) NOT NULL,
    db_id      VARCHAR(20) NOT NULL,    
    schema_nm  VARCHAR(20) NOT NULL,
    start_dt   TIMESTAMP NOT NULL,
    end_dt     TIMESTAMP NOT NULL,
    data_id    CHAR(6) NOT NULL,
    table_id   VARCHAR(50) NOT NULL,
    table_nm   VARCHAR(50) NOT NULL,
    api_params VARCHAR(500),
    record_cnt INTEGER,
    column_cnt INTEGER,
    status     VARCHAR(20) NOT NULL,
    error_msg  VARCHAR(1000),
    cret_dt    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm    VARCHAR(20) NOT NULL,
    mdfy_dt    TIMESTAMP,
    mdfy_nm    VARCHAR(20),
    CONSTRAINT mt_log_dataimp_pkey PRIMARY KEY (user_id, db_id, schema_nm, start_dt, table_id, api_params)
);

COMMENT ON TABLE ecodi_meta.mt_log_dataimp IS '데이터 수집/통합 로그';

COMMENT ON COLUMN mt_log_dataimp.user_id IS '크롤러 서버 사용자 아이디';
COMMENT ON COLUMN mt_log_dataimp.db_id IS 'DBMS 아이디';
COMMENT ON COLUMN mt_log_dataimp.schema_nm IS 'DB 스키마 명';
COMMENT ON COLUMN mt_log_dataimp.start_dt IS '실행 시작일시';
COMMENT ON COLUMN mt_log_dataimp.end_dt IS '실행 종료일시';
COMMENT ON COLUMN mt_log_dataimp.data_id IS '데이터 아이디';
COMMENT ON COLUMN mt_log_dataimp.table_id IS '테이블 아이디';
COMMENT ON COLUMN mt_log_dataimp.table_nm IS '테이블 명칭';
COMMENT ON COLUMN mt_log_dataimp.api_params IS 'API 호출 파라미터';
COMMENT ON COLUMN mt_log_dataimp.record_cnt IS '처리 레코드 건수';
COMMENT ON COLUMN mt_log_dataimp.column_cnt IS '처리 컬럼수';
COMMENT ON COLUMN mt_log_dataimp.status IS '실행 상태';
COMMENT ON COLUMN mt_log_dataimp.error_msg IS '에러 메시지';
COMMENT ON COLUMN mt_log_dataimp.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_log_dataimp.cret_nm IS '생성자';
COMMENT ON COLUMN mt_log_dataimp.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_log_dataimp.mdfy_nm IS '수정자';
