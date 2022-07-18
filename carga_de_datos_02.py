# %% [markdown]
# 

# %% [markdown]
# ### Paso 1: Importación de librerías

# %%
import datetime 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
sns.set(style="whitegrid", color_codes=True)

# %% [markdown]
# ### Paso 2: Carga de datos
# 

# %%
df = pd.read_parquet ('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2018-01.parquet')

# %% [markdown]
# ### Paso 3: Limpieza y Transformación

# %% [markdown]
# #### a) Se eliminaron columnas innecesarias

# %%
df.drop(columns=['congestion_surcharge','airport_fee'],inplace=True)

# %% [markdown]
# #### b) Se eliminaron registros duplicados

# %%
df.drop_duplicates(inplace=True)

# %% [markdown]
# #### c) Se renombraron las columnas

# %%
df.rename(columns =
                    {'VendorID':'vendor_id',
                    'RatecodeID':'ratecode_id',
                    'PULocationID':'pu_zone_id',
                    'DOLocationID':'do_zone_id'}, inplace = True)

# %% [markdown]
# #### d) Se creó una nueva columna, fare_per_mile, para estudiar la relación entre fare_amount y trip_distance

# %%
df['fare_per_mile'] = df.fare_amount / df.trip_distance

# %% [markdown]
# Debido que algunos registros tenían trip_distance 0, el fare_per_mile es infinito o NaN. Se les asignó 0 a estos registros

# %%
df.fare_per_mile[df.fare_per_mile > 100000] = 0

# %%
df.fare_per_mile.fillna(0,inplace=True)

# %% [markdown]
# #### e) Se creó una nueva columna, trip_time, para identificar el tiempo de viaje en segundos

# %% [markdown]
# Primero se calculó la diferencia de tiempo

# %%
df['trip_time'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime

# %% [markdown]
# Luego se convirtió a segundos

# %%
df.trip_time = df.trip_time.dt.total_seconds()

# %% [markdown]
# #### f) Se creó una nueva columna, fare_per_minute, para identificar la relación entre el fare_amount y el trip_time

# %%
df['fare_per_minute'] = df.fare_amount / (df.trip_time / 60)

# %%
df.fare_per_minute[df.fare_per_minute > 100000] = 0

# %%
df.fare_per_minute.fillna(0,inplace=True)

# %% [markdown]
# #### g) Se creó una nueva columna, id_borough, para identificar a qué Borough pertenece cada viaje

# %% [markdown]
# Lo primero es cargar el dataframe con las zonas de taxis

# %%
df_zones = pd.read_csv('https://raw.githubusercontent.com/soyHenry/DS-Proyecto_Grupal_TaxisNYC/main/taxi%2B_zone_lookup.csv')

# %% [markdown]
# Se reemplazaron los nombres de los boroughs por id's

# %%
df_zones.Borough.replace({"Bronx":0, "Brooklyn":1, "Manhattan":2, "Queens":3, "Staten Island":4, "EWR":5, "Unknown":6}, inplace=True)


# %% [markdown]
# Se creó un diccionario de zonas con su respectivo borough_id para luego mapear

# %%
dic_zone_borough = {df_zones.LocationID[i] : df_zones.Borough[i] for i in range (0,len(df_zones))}

# %% [markdown]
# Se creó una nueva columna con su respectivo borough_id

# %%
df['borough_id'] = df.pu_zone_id.map(dic_zone_borough)

# %% [markdown]
# #### h) Se creó una nueva columna, id_time_borough, para posteriormente relacionar con la tabla de daots climáticos

# %%
df['id_time_borough'] = df.tpep_pickup_datetime.dt.strftime('%Y%m%d%H') + df.borough_id.astype(str)

# %% [markdown]
# #### i) Se marcaron registros que poseen outliers

# %% [markdown]
# Creamos la columna para identificar el outliers

# %%
df['outlier'] = 1

# %% [markdown]
# Outliers trip_distance

# %%
# Calculamos rango intercuartílico, mínimo, y máximo
IQR = df.trip_distance.quantile(.75) - df.trip_distance.quantile(.25)
min = df.trip_distance.quantile(.25) - (1.5 * IQR)
max = df.trip_distance.quantile(.75) + (1.5 * IQR)

# Indentificamos outliers
df.loc[df.trip_distance < min, "outlier"] = 0
df.loc[df.trip_distance > max, "outlier"] = 0

# %% [markdown]
# Outliers fare_amount

# %%
# Calculamos rango intercuartílico, mínimo, y máximo
IQR = df.fare_amount.quantile(.75) - df.fare_amount.quantile(.25)
min = df.fare_amount.quantile(.25) - (1.5 * IQR)
max = df.fare_amount.quantile(.75) + (1.5 * IQR)

# Indentificamos outliers
df.loc[df.fare_amount < min, "outlier"] = 0
df.loc[df.fare_amount > max, "outlier"] = 0

# %% [markdown]
# Outliers trip_time

# %%
# Calculamos rango intercuartílico, mínimo, y máximo
IQR = df.trip_time.quantile(.75) - df.trip_time.quantile(.25)
min = df.trip_time.quantile(.25) - (1.5 * IQR)
max = df.trip_time.quantile(.75) + (1.5 * IQR)

# Indentificamos outliers
df.loc[df.trip_time < min, "outlier"] = 0
df.loc[df.trip_time > max, "outlier"] = 0


