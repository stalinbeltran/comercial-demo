# Visualizaciones por Reporte — ERP Comercial

## Catálogo de Tipos de Gráfico

| Código | Tipo | Cuándo usarlo |
|---|---|---|
| L | Línea | Tendencias en el tiempo |
| LB | Línea con banda | Tendencia + media móvil como contexto |
| BV | Barras verticales | Comparar períodos o categorías discretas |
| BH | Barras horizontales | Rankings, etiquetas largas |
| BA | Barras apiladas | Composición de un total |
| B100 | Barras 100% apiladas | Participación porcentual en el tiempo |
| BD | Barras divergentes | Valores positivos y negativos |
| WF | Waterfall | Efecto acumulado, desglose de un total |
| CD | Candlestick | Rangos de precio en un período |
| SC | Scatter / burbuja | Relación entre dos variables + volumen |
| PI | Pie | Participación (máx. 6 segmentos) |
| DO | Dona | Igual que Pie, con KPI en el centro |
| TM | Treemap | Jerarquía + volumen |
| GA | Gauge | KPI único vs meta |
| RA | Radar | Comparar múltiples dimensiones |
| HM | Heatmap | Patrones por dos dimensiones |
| GT | Gantt | Timeline de eventos |
| TS | Tabla semáforo | Alertas operacionales |

---

## 1. VENTAS Y FACTURACIÓN

| Reporte | Visualizaciones recomendadas |
|---|---|
| 1.1 Resumen consolidado | BV (por país/sucursal) · L (tendencia diaria) · KPI cards |
| 1.2 Comparativo sucursales | BV agrupadas (mes actual vs anterior) · BH ranking · BD variación % |
| 1.3 Ventas por producto/categoría | TM (tamaño=monto, color=crecimiento) · BH ranking · DO participación |
| 1.4 Ventas por cliente | BH ranking · DO (top 10 vs resto) · SC (frecuencia vs ticket promedio) |
| 1.5 Efectividad precios especiales | BA apiladas (oficial vs especial) · BD impacto margen · L tendencia descuento |
| 1.6 Impacto promociones | BV (unidades bajo promo) · WF (ingreso bruto→descuentos→neto) · DO participación |
| 1.7 Pedidos por estado | DO estados · L evolución diaria por estado · TS tabla operativa |
| 1.8 Facturas por estado | DO estados · BV por mes · TS vencimientos críticos |

---

## 2. INVENTARIO Y BODEGAS

| Reporte | Visualizaciones recomendadas |
|---|---|
| 2.1 Stock actual por bodega | TS tabla semáforo · BH disponible vs reservado · HM (bodega × producto) |
| 2.2 Stock consolidado por producto | TM (valor stock) · BH ranking disponibilidad · TS alertas |
| 2.3 Stock crítico | BH días de cobertura · TS semáforo rojo · KPI cards |
| 2.4 Sin movimiento | TM (capital inmovilizado) · BH días sin movimiento · TS |
| 2.5 Rotación de inventario | BH índice rotación · SC (rotación vs cobertura) · HM (producto × mes) |
| 2.6 Trazabilidad movimientos | L evolución stock · TS historial · BA entradas vs salidas |
| 2.7 Ajustes de inventario | BV cantidad de ajustes · BD positivos vs negativos · L tendencia mensual |
| 2.8 Traslados entre bodegas | BH volumen por ruta · HM (origen × destino) · L frecuencia |

---

## 3. TRANSPORTE Y LOGÍSTICA

| Reporte | Visualizaciones recomendadas |
|---|---|
| 3.1 Recorridos activos | TS tabla en tiempo real · GA % completado por camión · mapa de ruta |
| 3.2 Cumplimiento entregas | BH % a tiempo por conductor · GA meta de puntualidad · L tendencia |
| 3.3 Rendimiento por camión | BH km recorridos · BV entregas realizadas · SC (km vs ocupación) |
| 3.4 Rendimiento por conductor | RA multidimensional · BH ranking puntualidad · TS comparativa |
| 3.5 Eficiencia de rutas | BD tiempo real vs estimado · SC (distancia vs tiempo) · BH por ruta |
| 3.6 Entregas fallidas | DO motivos de fallo · L tendencia semanal · BH por zona |
| 3.7 Ocupación de flota | GA % ocupación promedio · BH por camión · L evolución diaria |
| 3.8 Costo por entrega | BH costo por cliente/zona · L evolución · SC (volumen vs costo) |

---

## 4. CLIENTES Y CARTERA

| Reporte | Visualizaciones recomendadas |
|---|---|
| 4.1 Activos / inactivos | DO segmentos · BV evolución mensual · TS con días última compra |
| 4.2 Pareto 80/20 | L acumulada (curva de Pareto) · BH ranking facturado · DO top vs resto |
| 4.3 Clientes por grupo | RA multidimensional por grupo · BV ticket promedio · HM (grupo × mes) |
| 4.4 Cuentas vencidas | BH días de mora · TS semáforo · L mora acumulada en el tiempo |
| 4.5 Límites de crédito | BH % crédito usado · TS con alerta >80% · GA crédito disponible total |
| 4.6 Nuevos clientes | BV nuevos por mes · L tendencia de adquisición · DO por país/sucursal |
| 4.7 Retención y churn | L activos/perdidos/recuperados · BA composición · SC (antigüedad vs valor) |

---

## 5. SUCURSALES Y OPERACIONES

| Reporte | Visualizaciones recomendadas |
|---|---|
| 5.1 Dashboard operativo | KPI cards · TS semáforo · BV pedidos por estado |
| 5.2 Comparativo sucursales | BV agrupadas · HM (sucursal × KPI) · RA multidimensional |
| 5.3 Desempeño por país | TM (monto facturado) · BH ranking · L tendencia por país |
| 5.4 Capacidad bodegas | GA ocupación · BH por bodega · L evolución semanal |
| 5.5 Pedidos cancelados/anulados | BV por sucursal · DO motivos · L tendencia |

---

## 6. PRODUCTOS Y CATÁLOGO

| Reporte | Visualizaciones recomendadas |
|---|---|
| 6.1 Más vendidos | BH unidades · TM monto · L tendencia top 10 |
| 6.2 Menos vendidos | BH · TS candidatos a descontinuar · SC (rotación vs stock) |
| 6.3 Análisis de precios | BV rango (min/max precio especial) · SC precio oficial vs especial · CD por semana |
| 6.4 Promociones activas | GT gantt de vigencias · TS días restantes · BH rendimiento por promo |
| 6.5 Margen por producto | BH margen bruto · BD vs benchmark · TM (margen × volumen) |

---

## 7. EJECUTIVOS CONSOLIDADOS

| Reporte | Visualizaciones recomendadas |
|---|---|
| 7.1 Dashboard CEO | KPI cards · GA metas · BV tendencia 30 días · TS alertas críticas |
| 7.2 Informe mensual | BV comparativo · L tendencias · TM productos · DO clientes |
| 7.3 Cierre contable | BV facturado/cobrado/pendiente · WF desglose · TS por país |
| 7.4 Proyección demanda | L histórico + proyección · BV por categoría · HM estacionalidad |
| 7.5 Riesgos operacionales | TS priorizada · GA por área de riesgo · BH top 10 alertas |
| 7.6 Presupuesto vs ejecución | BD variación % · BV agrupadas real vs meta · GA avance global |

---

## Reportes de sec_promo_precios_diario

### Por módulo de análisis

| Reporte | Visualizaciones recomendadas |
|---|---|
| Efectividad de promociones activas | BH ranking uplift · L línea dual ventas vs baseline · GA uplift vs meta · HM producto×semana |
| Costo total de descuentos | BA apiladas costo vs ingreso incremental · L área acumulado diario · DO por promoción · WF ingreso bruto→neto |
| Ciclo de vida de promociones | BV progreso (pct_vida_promo) · L ventas diarias desde inicio · GT gantt de promos · HM intensidad ventas |
| Promos próximas a vencer | BH días restantes · TS semáforo verde/amarillo/rojo · DO ventas últimos 7 días |
| Comparativa entre promociones | BV agrupadas · RA multidimensional · L evolución paralela · TS comparativa |
| Dispersión de precios | BV rango min/max · CD rango semanal · TM volumen+dispersión · TS mayor brecha |
| Evolución precio oficial | L con anotaciones en cambios · BV variación 7d/30d · L área precio+promo+especial superpuestos |
| Descuento máx por categoría | TM descuento vs volumen · BH ranking · PI participación descuentos · L evolución |
| Precio especial vs oficial | BD divergente · SC precio oficial vs especial · L dual · TS ranking brecha |
| Tendencia diaria de ventas | LB con bandas 7d/30d · BA+L combo unidades+monto · B100 composición · HM calendario |
| Ventas acumuladas vs mes anterior | L dual acumulado · BV semana a semana · GA % avance · BD variación por día |
| Comparativa entre períodos | L múltiples · BV agrupadas · SC período actual vs anterior · TS pivote |
| Participación bajo promo vs precio normal | B100 diario · DO del período · BA semanal/mensual · L dependencia de descuentos |
| Rendimiento por categoría | TM jerárquico · BV uplift por categoría · RA multidimensional · L evolución |
| Alta dependencia de descuentos | BH ranking pct_precio_oficial · SC precio vs % bajo promo · TS semáforo |
| Promos sin uplift positivo | BD uplift pos/neg · SC costo vs ingreso incremental con línea break-even · TS peor ROI |
| Cambios de precio no planificados | BV variación con umbral · TS semáforo · L historial con marcadores en cambios |

### Por granularidad

| Granularidad | GROUP BY en query | Mejor para |
|---|---|---|
| Día exacto | `fecha` | Seguimiento operativo, análisis de un evento |
| Día de semana | `dia_semana` | Estacionalidad semanal (¿qué día vende más?) |
| Fin de semana | `es_fin_de_semana` | Comparativa semana vs fin de semana |
| Semana ISO | `anio_semana` | Tendencias semanales, comparar semana a semana |
| Mes | `anio_mes` | Cierres mensuales, KPIs ejecutivos |
| Trimestre | `anio_trimestre` | Presentaciones de junta, objetivos trimestrales |
| Año | `anio` | Comparativas interanuales, presupuesto |