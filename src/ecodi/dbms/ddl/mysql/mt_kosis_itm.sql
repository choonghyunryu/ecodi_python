-- Description: KOSIS 데이터 항목 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_itm
(
    tbl_id      VARCHAR(40) NOT NULL            COMMENT '통계표 ID',
    org_id      VARCHAR(40) NOT NULL            COMMENT '제공기관 코드',  
    itm_seq     INT NOT NULL                    COMMENT '데이터 항목 순번',
    obj_id      VARCHAR(40) NOT NULL            COMMENT '객체 ID',
    obj_nm      VARCHAR(40) NOT NULL            COMMENT '객체 명칭',
    obj_id_sn   INT                             COMMENT '객체 ID 일련번호',
    obj_nm_eng  VARCHAR(40)                     COMMENT '객체 영문 명칭',
    up_itm_id   VARCHAR(40)                     COMMENT '상위 데이터 항목 ID',
    itm_nm      VARCHAR(40) NOT NULL            COMMENT '데이터 항목 명칭',
    itm_id      VARCHAR(40) NOT NULL            COMMENT '데이터 항목 ID',
    itm_nm_eng  VARCHAR(40)                     COMMENT '데이터 항목 영문 명칭',
    unit_id     VARCHAR(40)                     COMMENT '단위 ID',
    unit_nm     VARCHAR(40)                     COMMENT '단위 명칭',
    unit_eng_nm VARCHAR(40)                     COMMENT '단위 영문 명칭',
    cret_dt     DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt     DATETIME                        COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_itm_pkey PRIMARY KEY (tbl_id, org_id, itm_seq)
);

ALTER TABLE ecodi_meta.mt_kosis_itm COMMENT = 'KOSIS 데이터 항목 정보';
