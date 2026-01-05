🧱 Ultra-Prompt: AWS Lakehouse Development (Continuidad)
Contexto del Proyecto: "Actúa como un Senior Data Engineer & Platform Architect. Estamos desarrollando un Lakehouse moderno en AWS (simulado localmente y listo para nube) que procesa datos financieros de alta frecuencia. El objetivo es evolucionar el proyecto anterior hacia un stack basado en Intel/Silicon, optimizado para cómputo pesado.

Estado de la Infraestructura y Troubleshooting realizado:

Entorno de Ejecución: Usamos Astro CLI sobre Podman.

Red (Crítico): Se identificó y resolvió un cuello de botella de red donde el MTU por defecto de la interfaz de Podman (65,000) causaba fragmentación de paquetes en llamadas a APIs externas. Hemos estandarizado a MTU 1500 en redes personalizadas.

Docker & Java: El runtime de Airflow (basado en Debian Bookworm) ha sido personalizado exitosamente. Instalamos OpenJDK 17 headless y configuramos el entorno para que PySpark 3.5.0 pueda ejecutarse dentro de los workers de Airflow sin conflictos de dependencias, gestionando todo mediante UV para una resolución de paquetes ultrarrápida.

Bloqueo Actual: Estamos lidiando con un error de manifest unknown al levantar el cluster de Spark en el docker-compose.override.yml. Estamos migrando a imágenes verificadas de Bitnami (Spark 3.5.0) para asegurar compatibilidad.

Arquitectura de Datos (Medallion & Lakehouse):

Storage: Implementación de RustFS (S3-compatible) para emular el Data Lake de AWS.

Engine: Dualidad técnica. Usamos Polars para transformaciones rápidas de memoria (Silver Layer) aprovechando Apache Arrow, y Spark para el procesamiento distribuido de grandes volúmenes.

Modeling: Esquema en estrella (Star Schema) en la capa Gold, gestionado por dbt.

Orchestration: Airflow mediante Data-Aware Scheduling (Datasets) para desacoplar la ingesta de la transformación.

Tu Misión para esta sesión:

Fix de Infraestructura: Revisar el docker-compose.override.yml para mapear correctamente las imágenes de bitnami/spark:3.5.0 y asegurar que el Master y el Worker se comuniquen en la misma red que Airflow.

Ingesta Pro (Bronze): Diseñar un DAG de Airflow que use Dynamic Task Mapping para procesar múltiples tickers de acciones en paralelo, persistiendo el JSON crudo en el bucket de RustFS.

Diseño de la Capa Silver: Crear el template de transformación con Polars. Necesito que el código maneje la serialización Arrow para pasar datos de la extracción al procesamiento sin el overhead de Pandas.

Validación de Calidad: Configurar los primeros tests de dbt-expectations para asegurar que no entren nulos en las columnas de precios ajustados.

Documentación técnica de referencia:

Engine: Spark 3.5.0 / Python 3.13.11 / Polars (Rust-backed).

Storage: S3 API / Parquet format.

Networking: Podman Custom Bridge (MTU 1500).

¿Cuál es la estrategia más eficiente para configurar el SparkSubmitOperator en Airflow de modo que reconozca los nodos del cluster externo que estamos levantando en el override?"
