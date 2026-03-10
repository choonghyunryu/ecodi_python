#     Initialize the ecoDI environment by loading system environment variables.
#     This function should be called at the start of your application to set up the environment.
#     """

from ecodi.env import (
    init_env,
    ecoDI_env,
    get_sysenv,
    set_env,
    unset_env,
    get_env,
    ecoDI_env,
    encode_base64,
    decode_base64,
    initial_meta
)

from ecodi.dbms import (
    _match_arg,
    _build_connection_string,
    _read_sql_file,
    _split_sql_statements,    
    db_connect,
    meta_connect,
    ods_connect,
    data_connect,
    is_connected,
    db_close,
    query_from_file,
    get_connection,
    getquery,
    deletequery,
    is_tabled,
    db_settable,
    db_load_csv,
    query_from_file,
    ddl_from_text,
    db_load_df,
    get_odsinfo,
    set_dbinfo,
    table_to_csv,
    schema_to_csv,
    db_send_query
)

from ecodi.KOSIS import (
    desc_kosis_stats,
    get_kosis_stats,
    from_meta_kosisdesc,
    get_kosis_indexpl,
    get_kosis_info,
    get_kosis_explanation,
    kosis_stats_list,
    kosis_list_level1,
    kosis_list_parent,
    kosis_list_stats,
    kosis_org_list,
    import_kosis_indexpl,
    import_kosis_statexpl,
    import_kosis_item,
    import_kosis_tbl,
    import_kosis_prd,
    import_kosis_src,
    tab_kosis_desc,
    mk_kosis_ddl_info,
    mk_kosis_ddl,
    insert_kosis_list,
    insert_kosis_item,
    insert_kosis_cmmt,
    insert_kosis_update,
    insert_kosis_paramset,
    reorg_kosis_data
)

from ecodi.api import (
    from_meta_apiurl,
    from_meta_param,
    from_meta_apikey,
    from_meta_datalist,
    from_meta_pramset,
    from_meta_result,
    from_meta_ddl,
    get_api_url,
    get_api_result,
    get_api_data,
    set_apikey_env,
    import_api_data
)

from ecodi.utils import (
    regist_apikey,
    unregist_apikey,
    write_apikey,
    read_apikey,
    get_prd_seq,
    get_os
)

from ecodi.ecodi_system import (
    get_log_manage,
    get_log_import,
    get_table_list,
    get_column_list
)

from ecodi.preprocess import (
    mapp_name2mega,
    mapp_name2cty,
    ods2data,
    mk_mart_ddl_info,
    mk_mart_ddl,
    mk_mart_table
)


env.init_env()
env.ecoDI_env()

__version__ = "0.1.1"
