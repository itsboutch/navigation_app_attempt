import pandas as pd
from sqlalchemy import create_engine


db_params = {
    'dbname': 'paris',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': '5432',
}


csv_file_path = 'network_nodes.csv'
csv_file_path2 = 'network_temporal_week.csv'
csv_file_path3 = 'network_walk.csv'
csv_file_path4 = 'network_bus.csv'
csv_file_path5 = 'network_tram.csv'
csv_file_path6 = 'network_subway.csv'
csv_file_path7 = 'network_rail.csv'


table_name = 'network_nodes'
table_name2 = 'network_temporal_week'
table_name3 = 'network_walk'
table_name4 = 'network_bus'
table_name5 = 'network_tram'
table_name6 = 'network_subway'
table_name7 = 'network_rail'


df = pd.read_csv(csv_file_path, delimiter=';')
df2 = pd.read_csv(csv_file_path2)
df3 = pd.read_csv(csv_file_path3)
df4 = pd.read_csv(csv_file_path4, delimiter=';')
df5 = pd.read_csv(csv_file_path5, delimiter=';')
df6 = pd.read_csv(csv_file_path6, delimiter=';')
df7 = pd.read_csv(csv_file_path7, delimiter=';')


engine = create_engine(f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["dbname"]}')


df.to_sql(table_name, engine, if_exists='replace', index=False)
df2.to_sql(table_name2, engine, if_exists='replace', index=False)
df3.to_sql(table_name3, engine, if_exists='replace', index=False)
df4.to_sql(table_name4, engine, if_exists='replace', index=False)
df5.to_sql(table_name5, engine, if_exists='replace', index=False)
df6.to_sql(table_name6, engine, if_exists='replace', index=False)
df7.to_sql(table_name7, engine, if_exists='replace', index=False)






