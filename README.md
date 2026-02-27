# ecodi_python

## Conda environments

### List conda environments

```
conda env list 
```

### Activate conda environment

```
conda activate dev_python 
```


## Install python packages

### Jupyter Lab

```
pip install ipykernel  
pip install jupyterlab  
```

### DBMS connectors

```
pip install psycopg2 
pip install mysql-connector-python
pip install sqlalchemy
```


### Create packages connectors

```
pip install build  
```

## Create python package

### Create package structure

```
$ tree
.
├── dist
│   ├── ecodi-0.1.1-py3-none-any.whl
│   └── ecodi-0.1.1.tar.gz
├── Environments.Rmd
├── pyproject.toml
├── README.md
├── src
│   ├── ecodi
│   │   ├── __init__.py
│   │   ├── API.py
│   │   ├── dbms
│   │   │   ├── ddl
│   │   │   │   ├── mysql
│   │   │   │   │   ├── mt_api_errmsg.sql
│   │   │   │   │   ├── mt_api_key.sql
│   │   │   │   │   ├── mt_api_param.sql
│   │   │   │   │   ├── mt_api_paramset.sql
│   │   │   │   │   ├── mt_api_result.sql
│   │   │   │   │   ├── mt_api_url.sql
│   │   │   │   │   ├── mt_code_list.sql
│   │   │   │   │   ├── mt_data_comment.sql
│   │   │   │   │   ├── mt_data_item.sql
│   │   │   │   │   ├── mt_data_list.sql
│   │   │   │   │   ├── mt_data_prvdr.sql
│   │   │   │   │   ├── mt_data_update.sql
│   │   │   │   │   ├── mt_kosis_indctr.sql
│   │   │   │   │   ├── mt_kosis_indexpl.sql
│   │   │   │   │   ├── mt_kosis_indlist.sql
│   │   │   │   │   ├── mt_kosis_itm.sql
│   │   │   │   │   ├── mt_kosis_org.sql
│   │   │   │   │   ├── mt_kosis_prd.sql
│   │   │   │   │   ├── mt_kosis_prdse.sql
│   │   │   │   │   ├── mt_kosis_src.sql
│   │   │   │   │   ├── mt_kosis_stat.sql
│   │   │   │   │   ├── mt_kosis_statbl.sql
│   │   │   │   │   ├── mt_kosis_statexpl.sql
│   │   │   │   │   ├── mt_kosis_tbl.sql
│   │   │   │   │   ├── mt_log_dataimp.sql
│   │   │   │   │   ├── mt_log_manage.sql
│   │   │   │   │   ├── mt_region_admi.sql
│   │   │   │   │   ├── mt_region_cty.sql
│   │   │   │   │   ├── mt_region_mega.sql
│   │   │   │   │   ├── mt_schema_list.sql
│   │   │   │   │   ├── mt_snippet_clss.sql
│   │   │   │   │   ├── mt_sys_user.sql
│   │   │   │   │   ├── mt_table_clss.sql
│   │   │   │   │   ├── mt_table_column.sql
│   │   │   │   │   ├── mt_table_comment.sql
│   │   │   │   │   ├── mt_table_list.sql
│   │   │   │   │   ├── mt_table_report.sql
│   │   │   │   │   ├── mt_table_snippet.sql
│   │   │   │   │   └── mt_table_update.sql
│   │   │   │   └── postgresql
│   │   │   │       ├── mt_api_errmsg.sql
│   │   │   │       ├── mt_api_key.sql
│   │   │   │       ├── mt_api_param.sql
│   │   │   │       ├── mt_api_paramset.sql
│   │   │   │       ├── mt_api_result.sql
│   │   │   │       ├── mt_api_url.sql
│   │   │   │       ├── mt_code_list.sql
│   │   │   │       ├── mt_data_comment.sql
│   │   │   │       ├── mt_data_item.sql
│   │   │   │       ├── mt_data_list.sql
│   │   │   │       ├── mt_data_prvdr.sql
│   │   │   │       ├── mt_data_update.sql
│   │   │   │       ├── mt_kosis_indctr.sql
│   │   │   │       ├── mt_kosis_indexpl.sql
│   │   │   │       ├── mt_kosis_indlist.sql
│   │   │   │       ├── mt_kosis_itm.sql
│   │   │   │       ├── mt_kosis_org.sql
│   │   │   │       ├── mt_kosis_prd.sql
│   │   │   │       ├── mt_kosis_prdse.sql
│   │   │   │       ├── mt_kosis_src.sql
│   │   │   │       ├── mt_kosis_stat.sql
│   │   │   │       ├── mt_kosis_statbl.sql
│   │   │   │       ├── mt_kosis_statexpl.sql
│   │   │   │       ├── mt_kosis_tbl.sql
│   │   │   │       ├── mt_log_dataimp.sql
│   │   │   │       ├── mt_log_manage.sql
│   │   │   │       ├── mt_region_admi.sql
│   │   │   │       ├── mt_region_cty.sql
│   │   │   │       ├── mt_region_mega.sql
│   │   │   │       ├── mt_schema_list.sql
│   │   │   │       ├── mt_snippet_clss.sql
│   │   │   │       ├── mt_sys_user.sql
│   │   │   │       ├── mt_table_clss.sql
│   │   │   │       ├── mt_table_column.sql
│   │   │   │       ├── mt_table_comment.sql
│   │   │   │       ├── mt_table_list.sql
│   │   │   │       ├── mt_table_report.sql
│   │   │   │       ├── mt_table_snippet.sql
│   │   │   │       └── mt_table_update.sql
│   │   │   └── meta
│   │   │       ├── mt_api_errmsg.csv
│   │   │       ├── mt_api_key.csv
│   │   │       ├── mt_api_param.csv
│   │   │       ├── mt_api_paramset.csv
│   │   │       ├── mt_api_result.csv
│   │   │       ├── mt_api_url.csv
│   │   │       ├── mt_code_list.csv
│   │   │       ├── mt_data_list.csv
│   │   │       ├── mt_data_prvdr.csv
│   │   │       ├── mt_kosis_prdse.csv
│   │   │       ├── mt_region_admi.csv
│   │   │       ├── mt_region_cty.csv
│   │   │       ├── mt_region_mega.csv
│   │   │       ├── mt_schema_list.csv
│   │   │       └── mt_sys_user.csv
│   │   ├── DBMS.py
│   │   ├── ecodi_system.py
│   │   ├── env.py
│   │   ├── KOSIS.py
│   │   ├── preprocess.py
│   │   ├── resource_infomation.py
│   │   └── utils.py
│   └── ecodi.egg-info
│       ├── dependency_links.txt
│       ├── PKG-INFO
│       ├── SOURCES.txt
│       └── top_level.txt
└── tests

11 directories, 112 files
```


### Build package

```
python -m build
```

### Install package

```
pip install ./dist/ecodi-0.1.2-py3-none-any.whl
```


