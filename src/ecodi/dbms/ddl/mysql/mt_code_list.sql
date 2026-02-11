-- Description: 외부 데이터 코드 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_code_list
(
    code_id             CHAR(6) NOT NULL                COMMENT '코드 ID',
    code_nm             VARCHAR(20)                     COMMENT '코드 명칭',
    code_clss           VARCHAR(10)                     COMMENT '코드 구분',
    code_seq            INT                             COMMENT '코드 순번',
    code_encode         VARCHAR(20)                     COMMENT '코드 인코드',
    code_decode         VARCHAR(20)                     COMMENT '코드 디코드',
    code_desc           VARCHAR(200)                    COMMENT '코드 비고',
    parent_id           CHAR(6)                         COMMENT '상위 코드 ID',
    parent_encode       VARCHAR(20)                     COMMENT '상위 코드 인코드',
    cret_dt             DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm             VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt             DATETIME                        COMMENT '수정일시',
    mdfy_nm             VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_code_list_pkey PRIMARY KEY (code_id, code_encode)
);

ALTER TABLE ecodi_meta.mt_code_list COMMENT = '외부 데이터 코드 정보';
