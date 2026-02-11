-- Description: KOSIS 데이터 항목 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_itm
(
    tbl_id      VARCHAR(40) NOT NULL,
    org_id      VARCHAR(40) NOT NULL,  
    itm_seq     INTEGER NOT NULL,
    obj_id      VARCHAR(40) NOT NULL,
    obj_nm      VARCHAR(40) NOT NULL,
    obj_id_sn   INTEGER,
    obj_nm_eng  VARCHAR(40),
    up_itm_id   VARCHAR(40),
    itm_nm      VARCHAR(40) NOT NULL,
    itm_id      VARCHAR(40) NOT NULL,
    itm_nm_eng  VARCHAR(40),
    unit_id     VARCHAR(40),
    unit_nm     VARCHAR(40),
    unit_eng_nm VARCHAR(40),
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_itm_pkey PRIMARY KEY (tbl_id, org_id, itm_seq)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_itm IS 'KOSIS 데이터 항목 정보';

COMMENT ON COLUMN mt_kosis_itm.tbl_id IS '통계표 ID';
COMMENT ON COLUMN mt_kosis_itm.org_id IS '제공기관 코드';
COMMENT ON COLUMN mt_kosis_itm.itm_seq IS '데이터 항목 순번';
COMMENT ON COLUMN mt_kosis_itm.obj_id IS '객체 ID';
COMMENT ON COLUMN mt_kosis_itm.obj_nm IS '객체 명칭';
COMMENT ON COLUMN mt_kosis_itm.obj_id_sn IS '객체 ID 일련번호';
COMMENT ON COLUMN mt_kosis_itm.obj_nm_eng IS '객체 영문 명칭';
COMMENT ON COLUMN mt_kosis_itm.up_itm_id IS '상위 데이터 항목 ID';
COMMENT ON COLUMN mt_kosis_itm.itm_nm IS '데이터 항목 명칭';
COMMENT ON COLUMN mt_kosis_itm.itm_id IS '데이터 항목 ID';
COMMENT ON COLUMN mt_kosis_itm.itm_nm_eng IS '데이터 항목 영문 명칭';
COMMENT ON COLUMN mt_kosis_itm.unit_id IS '단위 ID';
COMMENT ON COLUMN mt_kosis_itm.unit_nm IS '단위 명칭';
COMMENT ON COLUMN mt_kosis_itm.unit_eng_nm IS '단위 영문 명칭';
COMMENT ON COLUMN mt_kosis_itm.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_itm.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_itm.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_itm.mdfy_nm IS '수정자';
