-- Description: KOSIS 지표설명 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_indexpl
(
    ind_id       VARCHAR(20) NOT NULL            COMMENT '지표ID',
    ind_nm       VARCHAR(100) NOT NULL           COMMENT '지표명',
    ind_title    VARCHAR(100) NOT NULL           COMMENT '설명자료 제목',
    ind_define   VARCHAR(1000) NOT NULL          COMMENT '지표개념',
    ind_exprsn   VARCHAR(1000) NOT NULL          COMMENT '산출방법',
    ind_src      VARCHAR(100) NOT NULL           COMMENT '출처정보',
    cret_dt      DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm      VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt      DATETIME                        COMMENT '수정일시',
    mdfy_nm      VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_indexpl_pkey PRIMARY KEY (ind_id)
);

ALTER TABLE ecodi_meta.mt_kosis_indexpl COMMENT = 'KOSIS 지표설명';
