import geopandas as gpd
from sqlalchemy import create_engine


db_params = {
    'dbname': 'paris',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': '5432',
}



geojson_file_path = 'routes.geojson'
geojson_file_path2 = 'stops.geojson'
geojson_file_path3 = 'sections.geojson'


table_name = 'routes'
table_name2 = 'stops'
table_name3 = 'sections'


gdf = gpd.read_file(geojson_file_path)
gdf2 = gpd.read_file(geojson_file_path2)
gdf3 = gpd.read_file(geojson_file_path3)


engine = create_engine(f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["dbname"]}')


gdf.to_postgis(table_name, engine, if_exists='replace', index=False)
gdf2.to_postgis(table_name2, engine, if_exists='replace', index=False)
gdf3.to_postgis(table_name3, engine, if_exists='replace', index=False)
