-- Description: API 호출 파라미터 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_param
(
    api_url_id     CHAR(6) NOT NULL                COMMENT 'API URL 아이디',
    param_seq      INT NOT NULL                    COMMENT '파라미터 순번',
    param_id       VARCHAR(50) NOT NULL            COMMENT '파라미터',
    param_nm       VARCHAR(50) NOT NULL            COMMENT '파라미터 명칭',
    default_value  VARCHAR(50)                     COMMENT '기본 설정값',
    is_must        CHAR(1) DEFAULT 'Y' NOT NULL    COMMENT '필수 파라미터 여부',
    is_key         CHAR(1) DEFAULT 'N' NOT NULL    COMMENT 'API Key 파라미터 여부',
    is_constant    CHAR(1) DEFAULT 'N' NOT NULL    COMMENT '파라미터값 상수여부',
    is_list        CHAR(1) DEFAULT 'Y' NOT NULL    COMMENT '파라미터값 목록여부',
    parent_seq     INT                             COMMENT '상위 파라미터 순번',
    cret_dt        DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm        VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt        DATETIME                        COMMENT '수정일시',
    mdfy_nm        VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_api_param_pkey PRIMARY KEY (api_url_id, param_seq)
);

ALTER TABLE ecodi_meta.mt_api_param COMMENT = 'API 호출 파라미터';
