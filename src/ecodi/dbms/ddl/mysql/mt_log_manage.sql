-- Description: 테이블 데이터 Import 로그
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_log_manage
(
    user_id    VARCHAR(20) NOT NULL            COMMENT '크롤러 서버 사용자 아이디',
    db_id      VARCHAR(20) NOT NULL            COMMENT 'DBMS 아이디',
    schema_nm  VARCHAR(20) NOT NULL            COMMENT 'DBMS 스키마 명',
    start_dt   DATETIME NOT NULL               COMMENT '실행 시작일시',
    rand_key   INT NOT NULL                    COMMENT '랜덤 키',
    end_dt     DATETIME NOT NULL               COMMENT '실행 종료일시',
    record_cnt INT                             COMMENT '처리 레코드 건수',
    column_cnt INT                             COMMENT '처리 컬럼수',
    sql_stmt   VARCHAR(4000) NOT NULL          COMMENT '실행 SQL',
    status     VARCHAR(20) NOT NULL            COMMENT '실행 상태',
    error_msg  VARCHAR(1000)                   COMMENT '에러 메시지',
    cret_dt    DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm    VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt    DATETIME                        COMMENT '수정일시',
    mdfy_nm    VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_log_manage_pkey PRIMARY KEY (user_id, db_id, schema_nm, start_dt, rand_key)
);

ALTER TABLE ecodi_meta.mt_log_manage COMMENT = '테이블 데이터 Import 로그';
