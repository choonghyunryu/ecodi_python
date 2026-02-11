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
│   ├── ecodi-0.1.0-py3-none-any.whl
│   └── ecodi-0.1.0.tar.gz
├── pyproject.toml
├── README.md
├── src
│   ├── ecodi
│   │   ├── __init__.py
│   │   ├── API.py
│   │   ├── DBMS.py
│   │   ├── env.py
│   │   └── KOSIS.py
│   └── ecodi.egg-info
│       ├── dependency_links.txt
│       ├── PKG-INFO
│       ├── SOURCES.txt
│       └── top_level.txt
└── tests

6 directories, 13 files
```


### Build package

```
python -m build
```

### Install package

```
pip install ./dist/ecodi-0.0.9-py3-none-any.whl
```


