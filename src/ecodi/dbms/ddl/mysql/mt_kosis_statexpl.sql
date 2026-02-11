-- Description: KOSIS 통계조사 설명 테이블 생성
CREATE TABLE IF NOT EXISTS ecodi_meta.mt_kosis_statexpl
(
    stat_id          VARCHAR(40) NOT NULL            COMMENT '통계조사 ID',
    stat_nm          VARCHAR(100) NOT NULL           COMMENT '조사명',
    stat_kind        VARCHAR(10)                     COMMENT '작성유형',
    stat_end         VARCHAR(100)                    COMMENT '통계종류',
    stat_continue    VARCHAR(50)                     COMMENT '계속여부',
    basis_law        VARCHAR(200)                    COMMENT '법적근거',
    writing_purps    VARCHAR(2000)                   COMMENT '조사목적',
    examin_pd        VARCHAR(100)                    COMMENT '조사기간',
    stat_period      VARCHAR(50)                     COMMENT '조사주기',
    writing_system   VARCHAR(200)                    COMMENT '조사체계',
    writing_tel      VARCHAR(200)                    COMMENT '연락처',
    stat_field       VARCHAR(200)                    COMMENT '통계(활용)분야·실태',
    examin_objrange  VARCHAR(2000)                   COMMENT '조사 대상범위',
    examin_objarea   VARCHAR(200)                    COMMENT '조사 대상지역',
    josa_unit        VARCHAR(2000)                   COMMENT '조사단위 및 조사대상규모',
    apply_group      VARCHAR(100)                    COMMENT '적용분류',
    josa_itm         VARCHAR(2000)                   COMMENT '조사항목',
    pub_period       VARCHAR(100)                    COMMENT '공표주기',
    pub_extent       VARCHAR(200)                    COMMENT '공표범위',
    pub_date         VARCHAR(2000)                   COMMENT '공표시기',
    publict_mth      VARCHAR(2000)                   COMMENT '공표방법 및 URL',
    examin_trget_pd  VARCHAR(100)                    COMMENT '조사대상기간 및 조사기준시점',
    data_user_note   VARCHAR(2000)                   COMMENT '자료이용시 유의사항',
    main_term_expl   VARCHAR(2000)                   COMMENT '주요 용어해설',
    data_collect_mth VARCHAR(200)                    COMMENT '자료 수집방법',
    examin_history   VARCHAR(2000)                   COMMENT '조사연혁',
    confm_no         VARCHAR(10)                     COMMENT '승인번호',
    confm_date       VARCHAR(10)                     COMMENT '승인일자',
    cret_dt          DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
    cret_nm          VARCHAR(20) NOT NULL            COMMENT '생성자',
    mdfy_dt          DATETIME                        COMMENT '수정일시',
    mdfy_nm          VARCHAR(20)                     COMMENT '수정자',
    CONSTRAINT mt_kosis_statexpl_pkey PRIMARY KEY (stat_id)
);

ALTER TABLE ecodi_meta.mt_kosis_statexpl COMMENT = 'KOSIS 통계조사 설명';