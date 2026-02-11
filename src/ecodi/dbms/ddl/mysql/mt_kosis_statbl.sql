-- Description: KOSIS 통계목록 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_statbl
(
    org_id      VARCHAR(40)                     COMMENT '제공기관 코드',
    tbl_id      VARCHAR(40) NOT NULL            COMMENT '통계표 ID',
    tbl_nm      VARCHAR(300)                    COMMENT '통계표명',
    perent_id   VARCHAR(50) NOT NULL            COMMENT '시작목록 ID',
    vw_cd       VARCHAR(40) NOT NULL            COMMENT '서비스뷰 ID',
    vw_nm       VARCHAR(300) NOT NULL           COMMENT '서비스뷰명',    
    stat_id     VARCHAR(40) NOT NULL            COMMENT '통계조사 ID',
    send_de     VARCHAR(10)                     COMMENT '최종갱신일',
    rec_tbl_se  VARCHAR(10)                     COMMENT '추천 통계표 여부',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_statbl_pkey PRIMARY KEY (org_id, tbl_id)
);

ALTER TABLE ecodi_meta.mt_kosis_statbl COMMENT = 'KOSIS 통계목록';
