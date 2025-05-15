# evaluacion-ds-b2c
Prueba técnica de habilidades de programación y manejo de datos.

#Adjuntaré respuestas escritas por acá
4. Al revisar las columnas, eliminaría además la columna "std_og_t2c_mou", pues todas las filas tienen valor "0" o null, nulos menores al 75% del total.
  La columna de  



6. En primer lugar, se utilizará una regresión logistica entre Churn y el número de recargas.

6.1 DF sin limpieza de datos (con outliers): Al observar los resultados, podemos determinar que existe una relación significativa y negativa entre el número de recargas y la posibilidad de churn. 
En este caso, el P-valor es menor al nivel de significancia, por lo que se descarta la hipótesis nula de que el número de recargas no afecta la posibilidad de churn.

   Optimization terminated successfully.
         Current function value: 0.065331
         Iterations 10
                           Logit Regression Results                           
==============================================================================
Dep. Variable:                  churn   No. Observations:               199397
Model:                          Logit   Df Residuals:                   199395
Method:                           MLE   Df Model:                            1
Date:               jue, 15 may. 2025   Pseudo R-squ.:                 0.04593
Time:                        14:53:49   Log-Likelihood:                -13027.
converged:                       True   LL-Null:                       -13654.
Covariance Type:            nonrobust   LLR p-value:                9.961e-275
==================================================================================
                     coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------
const             -3.2895      0.035    -93.590      0.000      -3.358      -3.221
total_rech_num    -0.1959      0.007    -28.079      0.000      -0.210      -0.182
==================================================================================



6.2 DF CON limpieza de datos (sin outliers): En este caso, es más sólida la hipótesis de que el número de recargas afecta negativamente la posibilidad de que un cliente haga churn. En primer lugar, el coeficiente de total_rech_num aumenta al limpiar los datos, lo que indicaría que es aún más fuerte la correlación negativa entre ambos si no se cuentan los valores extremos.
  Al mismo tiempo, el valor de Z aumenta aún más en valor absoluto y se aleja mas del 0, por lo que hay mayor evidencia de un coeficiente significativo.

Optimization terminated successfully.
         Current function value: 0.066020
         Iterations 10
                           Logit Regression Results                           
==============================================================================
Dep. Variable:                  churn   No. Observations:               189297
Model:                          Logit   Df Residuals:                   189295
Method:                           MLE   Df Model:                            1
Date:               jue, 15 may. 2025   Pseudo R-squ.:                 0.06072
Time:                        15:16:22   Log-Likelihood:                -12497.
converged:                       True   LL-Null:                       -13305.
Covariance Type:            nonrobust   LLR p-value:                     0.000
==================================================================================
                     coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------
const             -3.0004      0.036    -83.085      0.000      -3.071      -2.930
total_rech_num    -0.2760      0.008    -33.166      0.000      -0.292      -0.260
==================================================================================



6.3 Haría un random forest para determinar el churn, sin embargo, me he quedado sin tiempo.
