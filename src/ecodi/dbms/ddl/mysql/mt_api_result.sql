-- Description: API 호출 결과 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_result
(
    api_url_id     CHAR(6) NOT NULL                COMMENT 'API URL 아이디',
    result_seq     INT NOT NULL                    COMMENT '결과 순번',
    result_id      VARCHAR(20) NOT NULL            COMMENT '결과 변수',
    result_nm      VARCHAR(50) NOT NULL            COMMENT '결과 변수명',
    data_type      VARCHAR(20)                     COMMENT '결과 데이터 유형',
    data_len       INT                             COMMENT '결과 데이터 길이',
    is_pk          CHAR(1) DEFAULT 'N'             COMMENT 'PK 여부',
    is_missing     CHAR(1) DEFAULT 'N'             COMMENT '결측치 여부',
    param_id       VARCHAR(50)                     COMMENT '값에 사용할 파라미터변수',
    cret_dt        DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm        VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt        DATETIME                        COMMENT '수정일시',
    mdfy_nm        VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_api_result_pkey PRIMARY KEY (api_url_id, result_seq)
);

ALTER TABLE ecodi_meta.mt_api_result COMMENT = 'API 호출 결과';
