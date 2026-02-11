-- Description: 외부데이터 주석 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_data_comment
(
    data_id        CHAR(6) NOT NULL,
    data_comment   VARCHAR(2000),
    cret_dt        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm        VARCHAR(20) NOT NULL,
    mdfy_dt        TIMESTAMP,
    mdfy_nm        VARCHAR(20),
    CONSTRAINT mt_data_comment_pkey PRIMARY KEY (data_id)
);

COMMENT ON TABLE ecodi_meta.mt_data_comment IS '외부데이터 주석 정보';

COMMENT ON COLUMN mt_data_comment.data_id IS '데이터 아이디';
COMMENT ON COLUMN mt_data_comment.data_comment IS '데이터 기준 시점';
COMMENT ON COLUMN mt_data_comment.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_data_comment.cret_nm IS '생성자';
COMMENT ON COLUMN mt_data_comment.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_data_comment.mdfy_nm IS '수정자';
