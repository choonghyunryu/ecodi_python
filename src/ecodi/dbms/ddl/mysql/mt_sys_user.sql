-- Description: 데이터 수집/통합 시스템 사용자
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_sys_user
(
    user_id_enc VARCHAR(20) NOT NULL                      COMMENT '크롤러 서버 사용자 아이디',
    user_nm_enc VARCHAR(20) NOT NULL                      COMMENT '사용자',
    is_meta     CHAR(1) DEFAULT 'Y' NOT NULL              COMMENT '메타 스키마 권한',
    is_data     CHAR(1) DEFAULT 'Y' NOT NULL              COMMENT '데이터 스키마 권한',
    start_date  VARCHAR(10) NOT NULL                      COMMENT '사용자 등록 일자',
    end_date    VARCHAR(10) DEFAULT '9999-12-31' NOT NULL COMMENT '사용자 제거 일자',
    used        CHAR(1) NOT NULL                          COMMENT '사용 여부',
    cret_dt     DATETIME DEFAULT now() NOT NULL           COMMENT '생성일시',
    cret_nm     VARCHAR(20) NOT NULL                      COMMENT '생성자',
    mdfy_dt     DATETIME                                  COMMENT '수정일시',
    mdfy_nm     VARCHAR(20)                               COMMENT '수정자',
    CONSTRAINT mt_sys_user_pkey PRIMARY KEY (user_id_enc)
);

ALTER TABLE ecodi_meta.mt_sys_user COMMENT = '데이터 수집/통합 시스템 사용자';

