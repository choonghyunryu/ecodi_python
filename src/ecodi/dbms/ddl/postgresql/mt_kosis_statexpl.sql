-- Description: KOSIS 통계조사 설명 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_statexpl
(
    stat_id          VARCHAR(40) NOT NULL,
    stat_nm          VARCHAR(100) NOT NULL,
    stat_kind        VARCHAR(10),
    stat_end         VARCHAR(100),
    stat_continue    VARCHAR(50),
    basis_law        VARCHAR(200),
    writing_purps    VARCHAR(2000),
    examin_pd        VARCHAR(100),
    stat_period      VARCHAR(50),
    writing_system   VARCHAR(200),
    writing_tel      VARCHAR(200),
    stat_field       VARCHAR(200),
    examin_objrange  VARCHAR(2000),
    examin_objarea   VARCHAR(200),
    josa_unit        VARCHAR(2000),
    apply_group      VARCHAR(100),
    josa_itm         VARCHAR(2000),
    pub_period       VARCHAR(100),
    pub_extent       VARCHAR(200),
    pub_date         VARCHAR(2000),
    publict_mth      VARCHAR(2000),
    examin_trget_pd  VARCHAR(100),
    data_user_note   VARCHAR(2000),
    main_term_expl   VARCHAR(2000),
    data_collect_mth VARCHAR(200),
    examin_history   VARCHAR(2000),
    confm_no         VARCHAR(10),
    confm_date       VARCHAR(10),
    cret_dt          TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cret_nm          VARCHAR(20) NOT NULL,
    mdfy_dt          TIMESTAMP,
    mdfy_nm          VARCHAR(20),
    CONSTRAINT mt_kosis_statexpl_pkey PRIMARY KEY (stat_id)
);

COMMENT ON TABLE ecodi_meta.mt_kosis_statexpl IS 'KOSIS 통계조사 설명';

COMMENT ON COLUMN mt_kosis_statexpl.stat_id IS '통계조사 ID';
COMMENT ON COLUMN mt_kosis_statexpl.stat_nm IS '조사명';
COMMENT ON COLUMN mt_kosis_statexpl.stat_kind IS '작성유형';
COMMENT ON COLUMN mt_kosis_statexpl.stat_end IS '통계종류';
COMMENT ON COLUMN mt_kosis_statexpl.stat_continue IS '계속여부';
COMMENT ON COLUMN mt_kosis_statexpl.basis_law IS '법적근거';
COMMENT ON COLUMN mt_kosis_statexpl.writing_purps IS '조사목적';
COMMENT ON COLUMN mt_kosis_statexpl.examin_pd IS '조사기간';
COMMENT ON COLUMN mt_kosis_statexpl.stat_period IS '조사주기';
COMMENT ON COLUMN mt_kosis_statexpl.writing_system IS '조사체계';
COMMENT ON COLUMN mt_kosis_statexpl.writing_tel IS '연락처';
COMMENT ON COLUMN mt_kosis_statexpl.stat_field IS '통계(활용) 분야·실태';
COMMENT ON COLUMN mt_kosis_statexpl.examin_objrange IS '조사 대상범위';
COMMENT ON COLUMN mt_kosis_statexpl.examin_objarea IS '조사 대상지역';
COMMENT ON COLUMN mt_kosis_statexpl.josa_unit IS '조사단위 및 조사대상규모';
COMMENT ON COLUMN mt_kosis_statexpl.apply_group IS '적용분류';
COMMENT ON COLUMN mt_kosis_statexpl.josa_itm IS '조사항목';
COMMENT ON COLUMN mt_kosis_statexpl.pub_period IS '공표주기';
COMMENT ON COLUMN mt_kosis_statexpl.pub_extent IS '공표범위';
COMMENT ON COLUMN mt_kosis_statexpl.pub_date IS '공표시기';
COMMENT ON COLUMN mt_kosis_statexpl.publict_mth IS '공표방법 및 URL';
COMMENT ON COLUMN mt_kosis_statexpl.examin_trget_pd IS '조사대상기간 및 조사기준시점';
COMMENT ON COLUMN mt_kosis_statexpl.data_user_note IS '자료이용시 유의사항';
COMMENT ON COLUMN mt_kosis_statexpl.main_term_expl IS '주요 용어해설';
COMMENT ON COLUMN mt_kosis_statexpl.data_collect_mth IS '자료 수집방법';
COMMENT ON COLUMN mt_kosis_statexpl.examin_history IS '조사연혁';
COMMENT ON COLUMN mt_kosis_statexpl.confm_no IS '승인번호';
COMMENT ON COLUMN mt_kosis_statexpl.confm_date IS '승인일자';
COMMENT ON COLUMN mt_kosis_statexpl.cret_dt IS '생성일시';
COMMENT ON COLUMN mt_kosis_statexpl.cret_nm IS '생성자';
COMMENT ON COLUMN mt_kosis_statexpl.mdfy_dt IS '수정일시';
COMMENT ON COLUMN mt_kosis_statexpl.mdfy_nm IS '수정자';
