-- Description: KOSIS 데이터 제공기관 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_org
(
    org_id        VARCHAR(40) NOT NULL,
    org_nm        VARCHAR(50) NOT NULL,
    org_type      VARCHAR(40),
    phone_no      VARCHAR(40),
    fax_no        VARCHAR(40),
    post_cd       VARCHAR(40),
    addr          VARCHAR(50),
    use_yn        CHAR(1),
    appr_stat_yn  CHAR(1),
    homepage      VARCHAR(50),
    org_nm_eng    VARCHAR(50),
    org_reg_date  DATE,
    org_mdfy_date DATE,
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_kosis_org_pkey PRIMARY KEY (org_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_org IS 'KOSIS 데이터 제공기관 정보';

COMMENT ON COLUMN mt_kosis_org.org_id IS '기관 코드';
COMMENT ON COLUMN mt_kosis_org.org_nm IS '기관명';
COMMENT ON COLUMN mt_kosis_org.org_type IS '기관 유형';
COMMENT ON COLUMN mt_kosis_org.phone_no IS '전화번호';
COMMENT ON COLUMN mt_kosis_org.fax_no IS '팩스번호';
COMMENT ON COLUMN mt_kosis_org.post_cd IS '우편번호';
COMMENT ON COLUMN mt_kosis_org.addr IS '주소';
COMMENT ON COLUMN mt_kosis_org.use_yn IS '사용여부';
COMMENT ON COLUMN mt_kosis_org.appr_stat_yn IS '승인통계유무';
COMMENT ON COLUMN mt_kosis_org.homepage IS '홈페이지';
COMMENT ON COLUMN mt_kosis_org.org_nm_eng IS '기관명(영문)';
COMMENT ON COLUMN mt_kosis_org.org_reg_date IS '등록일';
COMMENT ON COLUMN mt_kosis_org.org_mdfy_date IS '최종수정일';
COMMENT ON COLUMN mt_kosis_org.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_org.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_org.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_org.mdfy_nm IS '수정자';
