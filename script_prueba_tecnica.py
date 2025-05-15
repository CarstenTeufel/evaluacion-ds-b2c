                                        ######Script analisis dataset móvil.#######

#Cargamos librerías necesarias
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm



                                         ####0. Lectura y preparación de datos###
#Obtenemos usuario y lo guardamos en una variable

user = os.getlogin()

#Indicamos ruta de archivo csv.
ruta_dataset = f'C:/Users/{user}/Downloads/prueba_tecnica_entel_v1.4.5/prueba_tecnica_entel_v1.4.5/dataset_prueba.csv'


#Leemos archivo y lo almacenamos en la variable dataset_prueba. A simple vista, el archivo tiene separadores de coma. Se indica el separador.
df_usuarios_movil = pd.read_csv(ruta_dataset, sep=",") 

#Transformar columna last_date_of_month en tipo fecha 
df_usuarios_movil['last_date_of_month'] = pd.to_datetime(df_usuarios_movil['last_date_of_month'])



#Separar df original en entrenamiento y prueba
df_entrenamiento = df_usuarios_movil[df_usuarios_movil['last_date_of_month'].isin(['2014-06-30', '2014-07-31'])].copy()

df_prueba = df_usuarios_movil[df_usuarios_movil['last_date_of_month'] == '2014-08-31'].copy()

#Verificamos que la separación se haya hecho correctamente

print(sorted(df_entrenamiento['last_date_of_month'].unique()))
print(sorted(df_prueba['last_date_of_month'].unique()))






                                        ###1. Crear clasificación según ARPU###


#Asignar tipo numérico a ARPU 
df_entrenamiento['arpu'] = pd.to_numeric(df_entrenamiento['arpu'], errors='coerce')

#Separamos por deciles
df_entrenamiento['decil_arpu'] = pd.qcut(df_entrenamiento['arpu'], 10, labels=False, duplicates='drop') + 1

#creamos categoría según arpu
df_entrenamiento['clasificacion_clientes_revenue'] = (df_entrenamiento['decil_arpu'].replace({10: 'platino', 9: 'gold'})
)

#Los clientes que no son platino o gold, son otros
df_entrenamiento.loc[~df_entrenamiento['clasificacion_clientes_revenue'].isin(['platino', 'gold']), 'clasificacion_clientes_revenue'] = 'normal'

#Verificamos que la separación por decil sea la correcta
df_entrenamiento.groupby('clasificacion_clientes_revenue')['arpu'].mean().sort_values(ascending=False)

#Contamos según clasificacion_clientes_revenue
df_entrenamiento['clasificacion_clientes_revenue'].value_counts(dropna=False)



                                        ###2. Crear columna flag_recarga y contar apariciones###


#Creamos columna flag_recarga. Si es 0 igual a 1, entonces 1. Si no, 0
df_entrenamiento['flag_recarga'] = (df_entrenamiento['total_rech_num'] >= 1).astype(int)

#Contamos según flag_recarga
df_entrenamiento['flag_recarga'].value_counts(dropna=False)


                                        ###3. Contabilizar clientes con churn###

df_entrenamiento['churn'] = pd.to_numeric(df_entrenamiento['churn'], errors='coerce')

#contar total de clientes por mes
total_por_mes = df_entrenamiento.groupby('last_date_of_month').size()

#contar clientes con churn = 1
churn_1_por_mes = df_entrenamiento[df_entrenamiento['churn'] == 1].groupby('last_date_of_month').size()

#Calculamos la proporción
proporcion_churn_mensual = churn_1_por_mes / total_por_mes

print(proporcion_churn_mensual)



                                        ###4. Eliminar columnas con 70%+ null###



#Q de filas
total_filas = len(df_entrenamiento)

#Contar nulls 
nulos_por_columna = df_entrenamiento.isnull().sum()

#Calcular proporción de filas nulas por columna
porcentaje_nulos = nulos_por_columna / total_filas

#Obtenemos columnas con nulos mayor a 0.7
columnas_a_eliminar = porcentaje_nulos[porcentaje_nulos >= 0.7]

#Obtenemos Q de columnas a eliminar
print(f"Columnas a eliminar: {len(columnas_a_eliminar)}")

columnas_a_eliminar = porcentaje_nulos[porcentaje_nulos > 0.7].index


#Drop a columnas
df_entrenamiento = df_entrenamiento.drop(columns=columnas_a_eliminar)



#Al observar la columna std_og_t2c_mou, se identifica que solo tiene 0's o nulls, por lo que se elimina igualmente.
valores_unicos = df_entrenamiento['std_og_t2c_mou'].unique()
print(valores_unicos)

df_entrenamiento = df_entrenamiento.drop(columns=['std_og_t2c_mou'])



                                        ###5. Diferencias en total_rech_num según churn###


#Promedio: Los clientes sin Churn tienen mayor cantidad de recargas en promedio
df_entrenamiento.groupby('churn')['total_rech_num'].mean()

#Al dividir en cuartiles por numero de recargas entre clientes con o sin churn, se pueden observar diferencias notables en el Q de recargas.
##Los clientes sin churn recargan más hasta por cuartil
comparacion = df_entrenamiento.groupby('churn')['total_rech_num'].describe()


#Creamos un boxplot para observar diferencias.
sns.boxplot(data=df_entrenamiento, x='churn', y='total_rech_num')
plt.title('Distribución de total_rech_num por churn')
plt.xlabel('Churn (0 = No, 1 = Sí)')
plt.ylabel('Recargas mensuales')
plt.show()


#Para observar mejor el fenómeno, eliminaremos valores muy desviados

# Calcular IQR
q1 = df_entrenamiento['total_rech_num'].quantile(0.25)
q3 = df_entrenamiento['total_rech_num'].quantile(0.75)
iqr = q3 - q1

# Definir límites sin outliers
limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr

# Filtrar dataset sin valores extremos
df_sin_outliers = df_entrenamiento[
    (df_entrenamiento['total_rech_num'] >= limite_inferior) &
    (df_entrenamiento['total_rech_num'] <= limite_superior)
]

# Crear boxplot
plt.figure(figsize=(8, 5))
sns.boxplot(data=df_sin_outliers, x='churn', y='total_rech_num')
plt.title('N° recargas (sin outliers)')
plt.xlabel('Churn')
plt.ylabel('Total recargas')
plt.grid(True)
plt.tight_layout()
plt.show()




###############################################################################################################################

                                    ####Parte 2####


                                    ###6. Modelo para predicción de churn###

#Se utilizará una regresión logistica entre la variable churn y total_rech_num

#######Sin limpieza de outliers#######
# Seleccionar variable independiente y dependiente
X = df_entrenamiento[['total_rech_num']]
y = df_entrenamiento['churn']

# Agregar constante para el intercepto
X = sm.add_constant(X)

# Ajustar modelo de regresión logística
modelo = sm.Logit(y, X).fit()

# Resumen del modelo
print(modelo.summary())

########Con limpieza de outliers######

# Seleccionar variable independiente y dependiente
X = df_sin_outliers[['total_rech_num']]
y = df_sin_outliers['churn']

# Agregar constante para el intercepto
X = sm.add_constant(X)

# Ajustar modelo de regresión logística
modelo = sm.Logit(y, X).fit()

# Resumen del modelo
print(modelo.summary())

