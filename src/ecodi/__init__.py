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
    init_env,
    encode_base64,
    decode_base64,
    initial_meta
)

from ecodi.DBMS import (
    _match_arg,
    _build_connection_string,
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
    db_load_csv
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
    import_kosis_indexpl
)

from ecodi.API import (
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
    set_apikey_env
)


env.init_env()
env.ecoDI_env()

__version__ = "0.1.1"
