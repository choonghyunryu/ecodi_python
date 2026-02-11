-- Description: 테이블 데이터 Import 로그
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_log_manage
(
    user_id    VARCHAR(20) NOT NULL,
    db_id      VARCHAR(20) NOT NULL,
    schema_nm  VARCHAR(20) NOT NULL,
    start_dt   TIMESTAMP NOT NULL,
    rand_key   INTEGER NOT NULL,
    end_dt     TIMESTAMP NOT NULL,
    record_cnt INTEGER,
    column_cnt INTEGER,
    sql_stmt   VARCHAR(4000) NOT NULL,
    status     VARCHAR(20) NOT NULL,
    error_msg  VARCHAR(1000),
    cret_dt    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm    VARCHAR(20) NOT NULL,
    mdfy_dt    TIMESTAMP,
    mdfy_nm    VARCHAR(20),
    CONSTRAINT mt_log_manage_pkey PRIMARY KEY (user_id, db_id, schema_nm, start_dt, rand_key)
);

COMMENT ON TABLE ecodi_meta.mt_log_manage IS '테이블 데이터 Import 로그';

COMMENT ON COLUMN mt_log_manage.user_id IS '크롤러 서버 사용자 아이디';
COMMENT ON COLUMN mt_log_manage.db_id IS 'DBMS 아이디';
COMMENT ON COLUMN mt_log_manage.schema_nm IS 'DBMS 스키마 명';
COMMENT ON COLUMN mt_log_manage.start_dt IS '실행 시작일시';
COMMENT ON COLUMN mt_log_manage.rand_key IS '랜덤 키';
COMMENT ON COLUMN mt_log_manage.end_dt IS '실행 종료일시';
COMMENT ON COLUMN mt_log_manage.record_cnt IS '처리 레코드 건수';
COMMENT ON COLUMN mt_log_manage.column_cnt IS '처리 컬럼수';
COMMENT ON COLUMN mt_log_manage.sql_stmt IS '실행 SQL';
COMMENT ON COLUMN mt_log_manage.status IS '실행 상태';
COMMENT ON COLUMN mt_log_manage.error_msg IS '에러 메시지';
COMMENT ON COLUMN mt_log_manage.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_log_manage.cret_nm IS '생성자';
COMMENT ON COLUMN mt_log_manage.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_log_manage.mdfy_nm IS '수정자';
