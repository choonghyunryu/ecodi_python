-- Description: KOSIS 데이터 제공기관 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_org
(
    org_id        VARCHAR(40) NOT NULL            COMMENT '기관 코드',
    org_nm        VARCHAR(50) NOT NULL            COMMENT '기관명',
    org_type      VARCHAR(40)                     COMMENT '기관 유형',
    phone_no      VARCHAR(40)                     COMMENT '전화번호',
    fax_no        VARCHAR(40)                     COMMENT '팩스번호',
    post_cd       VARCHAR(40)                     COMMENT '우편번호',
    addr          VARCHAR(50)                     COMMENT '주소',
    use_yn        CHAR(1)                         COMMENT '사용여부',
    appr_stat_yn  CHAR(1)                         COMMENT '승인통계유무',
    homepage      VARCHAR(50)                     COMMENT '홈페이지',
    org_nm_eng    VARCHAR(50)                     COMMENT '기관명(영문)',
    org_reg_date  DATE                            COMMENT '등록일',
    org_mdfy_date DATE                            COMMENT '최종수정일',
    cret_dt     DATETIME DEFAULT now() NOT NULL   COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL              COMMENT '생성자',
    mdfy_dt     DATETIME                          COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                       COMMENT '수정자',
    CONSTRAINT mt_kosis_org_pkey PRIMARY KEY (org_id)
);

ALTER TABLE ecodi_meta.mt_kosis_org COMMENT = 'KOSIS 데이터 제공기관 정보';
