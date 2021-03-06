import os
import pandas as pd
from itertools import groupby
from datetime import datetime, timedelta, date
import pathlib
import shutil
import logging
import logging.config 

import constants as Constants

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

class Date:
    def __init__(self, day_offset: int = 0):
        self.dt = datetime.now() + timedelta(days = day_offset)
        self.standard = self.dt.strftime(Constants.DateFormats.Standard)
        self.formal = self.dt.strftime(Constants.DateFormats.Formal)
        self.int = self.dt.strftime(Constants.DateFormats.Int)

def get_statcast_date_range(start_dt: str = None, end_dt: str = None):
    """
    """
    start_date = datetime.strptime(start_dt,Constants.DateFormats.Standard).date()
    end_date = datetime.strptime(end_dt,Constants.DateFormats.Standard).date()
    dates = []
    start = start_date
    
    while start <= end_date:
        date_span = start.replace(month=3, day=15), start.replace(month=11,day=15)
        season_start, season_end = Constants.Statcast.ValidDates.get(start.year,date_span)
        
        if start < season_start:
            start = season_start
        elif start > season_end:
            start, _ = Constants.Statcast.ValidDates.get(start.year + 1, (date(month=3,day=15,year=start.year + 1), None))

        if start > end_date:
            break
        
        end = min(start + timedelta(0), end_date)
        dates.append((start,end))
        start += timedelta(days=1)

    return dates    

def parse_statcast_df(df) -> pd.DataFrame:
    """
    """
    data_copy = df.copy()

    string_columns = [
        dtype_tuple[0] for dtype_tuple in data_copy.dtypes.items() if str(dtype_tuple[1]) in ["object","string"]
    ]

    for column in string_columns:
        first_value_index = data_copy[column].first_valid_index()
        if first_value_index is None:
            continue
        first_value = data_copy[column].loc[first_value_index]

        if str(first_value).endswith('%') or column.endswith('%'):
            data_copy[column] = data_copy[column].astype(str).str.replace("%", "").astype(float) / 100.0
        else:
            for date_regex, date_format in Constants.Statcast.DateFormats:
                if isinstance(first_value, str) and date_regex.match(first_value):
                    data_copy[column] = data_copy[column].apply(pd.to_datetime, errors='ignore', format=date_format)
                    data_copy[column] = data_copy[column].convert_dtypes(convert_string=False)
                    break

    data_copy.rename(columns={c:c.replace('.','_') for c in data_copy.columns.values if '.' in c},inplace=True)

    return data_copy

def rank_dict_list(dl: list = None, order_by: list = None, asc: bool = False,
                    partition_by: list = [], name: str = None):
    """Pass list of dictionaries
    Val = The Value you want to rank on
    Asc = Ascending True, Desc False
    Rank = True / False
    Rank Key = String, will be added to dicts
    """
    dl_sorted = sorted(
        dl,
        key = lambda x: tuple((x[v] for v in partition_by + order_by)),
        reverse = False if asc else True
    )
    if name:
        if partition_by:
            groups = groupby(dl_sorted, key = lambda x: tuple((x[v] for v in partition_by)))
            for k, group in groups:
                [d.update({name: (i+1)}) for i, d in enumerate(group)]
        else:
            [d.update({name: (i + 1)}) for i, d in enumerate(dl_sorted)]
    return dl_sorted

def setup_project(name:str = None, suffix:str = None, purge_existing:bool = False):
    """
    """
    project_path = os.path.join(Constants.Project.Path,name)
    project_iter_path = os.path.join(project_path,suffix)

    if not os.path.isdir(project_path):
        pathlib.Path(project_path).mkdir(parents=True, exist_ok=True)
        logging.info(f'Created project path: {project_path}')

    if os.path.isdir(project_iter_path) and purge_existing:
        shutil.rmtree(project_iter_path)
        logging.info(f'Purged file contents of {project_iter_path}')
    else:
        pathlib.Path(project_iter_path).mkdir(parents=True, exist_ok=True)   
        logging.info(f'Created project iteration path: {project_iter_path}')      

    for subf in Constants.Project.Subfolders:
        pathlib.Path(os.path.join(project_iter_path,subf)).mkdir(parents = True, exist_ok = True)
    logging.info(f'Created all project subfolders..')

    return project_iter_path



