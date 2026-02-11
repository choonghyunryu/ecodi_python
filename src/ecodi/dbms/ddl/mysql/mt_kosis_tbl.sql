-- Description: KOSIS 데이터 명칭 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_tbl
(
    tbl_id      VARCHAR(40) NOT NULL            COMMENT '통계표 ID',
    org_id      VARCHAR(40) NOT NULL            COMMENT '제공기관 코드',  
    tbl_nm      VARCHAR(300) NOT NULL           COMMENT '데이터 명칭',
    tbl_nm_eng  VARCHAR(300) NOT NULL           COMMENT '데이터 명칭 영문명',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_tbl_pkey PRIMARY KEY (tbl_id, org_id)
);

ALTER TABLE ecodi_meta.mt_kosis_tbl COMMENT = 'KOSIS 데이터 명칭 정보';
