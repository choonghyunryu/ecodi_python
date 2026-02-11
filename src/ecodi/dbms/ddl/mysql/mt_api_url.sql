-- Description: API 호출 URL 정보 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_url
(
    api_url_id     CHAR(6) NOT NULL                COMMENT 'API URL 아이디',
    api_url_nm     VARCHAR(50) NOT NULL            COMMENT 'API URL 명칭',
    is_usekey      CHAR(1) DEFAULT 'Y' NOT NULL    COMMENT 'API Key 사용 여부',
    key_id         VARCHAR(20)                     COMMENT 'API Key 아이디',
    call_url       VARCHAR(200) NOT NULL           COMMENT 'API 호출 URL',
    call_methd     VARCHAR(20) NOT NULL            COMMENT '호출방법',
    return_type    VARCHAR(20) NOT NULL            COMMENT '반환 데이터 구조',
    param_cnt      INT NOT NULL                    COMMENT '파라미터 개수',
    limit_cell_cnt INT                             COMMENT 'Limit 셀 개수',
    cret_dt        DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm        VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt        DATETIME                        COMMENT '수정일시',
    mdfy_nm        VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_api_url_pkey PRIMARY KEY (api_url_id)
);

ALTER TABLE ecodi_meta.mt_api_url COMMENT = 'API 호출 URL';
