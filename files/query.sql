-- Ingresos vs Salidas - últimos 12 meses (agrupado por mes)
SELECT
    meses.mes_anio,
    COALESCE(ing.total_ingresos, 0)  AS ingresos,
    COALESCE(sal.total_salidas,  0)  AS salidas
FROM (
    -- Genera los 12 meses del período
    SELECT DATE_FORMAT(
               DATE_SUB(LAST_DAY(NOW()), INTERVAL n MONTH), '%Y-%m'
           ) AS mes_anio
    FROM (
        SELECT 0 n UNION SELECT 1 UNION SELECT 2  UNION SELECT 3
        UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7
        UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
    ) nums
) meses

LEFT JOIN (
    -- INGRESOS: fecha en que se registró el negocio
    SELECT
        DATE_FORMAT(fecha_hora_registro, '%Y-%m') AS mes_anio,
        COUNT(*)                                   AS total_ingresos
    FROM negocio
    WHERE fecha_hora_registro >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
    GROUP BY DATE_FORMAT(fecha_hora_registro, '%Y-%m')
) ing ON ing.mes_anio = meses.mes_anio

LEFT JOIN (
    -- SALIDAS: fecha en que se le dio salida al negocio
    SELECT
        DATE_FORMAT(fecha_salida, '%Y-%m') AS mes_anio,
        COUNT(*)                            AS total_salidas
    FROM negocio
    WHERE fecha_salida >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY DATE_FORMAT(fecha_salida, '%Y-%m')
) sal ON sal.mes_anio = meses.mes_anio

ORDER BY meses.mes_anio asc limit 10;