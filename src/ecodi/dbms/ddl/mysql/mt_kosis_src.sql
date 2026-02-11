-- Description: KOSIS 데이터 출처 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_src
(
    tbl_id      VARCHAR(40) NOT NULL            COMMENT '통계표 ID',
    org_id      VARCHAR(40) NOT NULL            COMMENT '제공기관 코드', 
    stat_id     VARCHAR(40) NOT NULL            COMMENT '통계조사 ID',
    josa_nm     VARCHAR(100)                    COMMENT '출처 명칭',
    dept_phone  VARCHAR(40)                     COMMENT '출처 전화번호',
    dept_nm     VARCHAR(100)                    COMMENT '제공 부서',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_src_pkey PRIMARY KEY (tbl_id, org_id)
);

ALTER TABLE ecodi_meta.mt_kosis_src COMMENT = 'KOSIS 데이터 출처 정보';
