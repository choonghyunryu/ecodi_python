-- Description: 데이터 수집/통합 시스템 사용자
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_sys_user
(
    user_id_enc VARCHAR(20) NOT NULL,
    user_nm_enc VARCHAR(20) NOT NULL,
    is_meta     CHAR(1) DEFAULT 'Y' NOT NULL,
    is_data     CHAR(1) DEFAULT 'Y' NOT NULL,
    start_date  VARCHAR(10) NOT NULL,
    end_date    VARCHAR(10) DEFAULT '9999-12-31' NOT NULL,
    used        CHAR(1) NOT NULL,
    cret_dt     TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm     VARCHAR(20) NOT NULL,
    mdfy_dt     TIMESTAMP,
    mdfy_nm     VARCHAR(20),
    CONSTRAINT mt_sys_user_pkey PRIMARY KEY (user_id_enc)
);

COMMENT ON TABLE ecodi_meta.mt_sys_user IS '데이터 수집/통합 시스템 사용자';

COMMENT ON COLUMN mt_sys_user.user_id_enc IS '크롤러 서버 사용자 아이디';
COMMENT ON COLUMN mt_sys_user.user_nm_enc IS '사용자';
COMMENT ON COLUMN mt_sys_user.is_meta IS '메타 스키마 권한';
COMMENT ON COLUMN mt_sys_user.is_data IS '데이터 스키마 권한';
COMMENT ON COLUMN mt_sys_user.start_date IS '사용자 등록 일자';
COMMENT ON COLUMN mt_sys_user.end_date IS '사용자 제거 일자';
COMMENT ON COLUMN mt_sys_user.used IS '사용 여부';
COMMENT ON COLUMN mt_sys_user.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_sys_user.cret_nm IS '생성자';
COMMENT ON COLUMN mt_sys_user.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_sys_user.mdfy_nm IS '수정자';
