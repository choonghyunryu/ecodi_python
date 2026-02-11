-- Description: API 호출 파라미터  값 목록 메타 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_api_paramset
(
    data_id        CHAR(6) NOT NULL                COMMENT '데이터 아이디',
    api_url_id     CHAR(6) NOT NULL                COMMENT 'API URL 아이디',
    param_seq      INT NOT NULL                    COMMENT '파라미터 순번',
    value_seq      INT NOT NULL                    COMMENT '값 순번',
    value_set      VARCHAR(50)                     COMMENT '값 목록',
    value_set_desc VARCHAR(200)                    COMMENT '값 목록 내용',
    parent_set     VARCHAR(50)                     COMMENT '상위 파라미터 값',    
    cret_dt        DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm        VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt        DATETIME                        COMMENT '수정일시',
    mdfy_nm        VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_api_paramset_pkey PRIMARY KEY (data_id, api_url_id, param_seq, value_seq)
);

ALTER TABLE ecodi_meta.mt_api_paramset COMMENT = 'API 호출 파라미터 값 목록';

