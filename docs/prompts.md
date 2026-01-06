# prompt
Contexto del Proyecto: Estamos desarrollando un Portfolio de Data Engineering de nivel Junior llamado aws-silicon-intel-lakehouse. El objetivo es demostrar habilidades de arquitectura Cloud-Native, manejo de volúmenes de datos y mejores prácticas de ingeniería de datos.
Es mi 2do proyecto de data engineering, te pasare el README.md del 1er proyecto terminado, no soy novato! pero quiero profundizar en aws environment y terraform, como los otros tools y tech stack mencionados.

Especificaciones Técnicas:

Nombre del Repo: aws-silicon-intel-lakehouse.

Dominio: Market Intelligence de la industria de semiconductores e IA (noticias de Nvidia, TSMC, etc.).

Sistema Operativo: Artix Linux (OpenRC) con Podman, CLI focused.

Orquestación: Apache Airflow (Astronomer-CLI).

Ingestión: dlt (Data Load Tool) para NewsAPI.org.

Procesamiento: PySpark.

Almacenamiento (Lakehouse): Arquitectura Medallion (Bronze/Silver/Gold) sobre S3 emulado por LocalStack, usando Apache Iceberg para la capa Gold.

Infraestructura: Terraform para gestionar los buckets y el Glue Catalog en LocalStack.

Tech Stack: Terraform, airflow (Astronomer-CLI), pypsark, apache iceberg, aws services, python, SQL.

Estado Actual:

El repositorio está inicializado con Git en la rama feat/initial-infra-setup.

El .gitignore está configurado para evitar ruido de .astro, .venv y .terraform.

Hemos optimizado el Dockerfile para evitar apt-get update innecesarios

El docker-compose.override.yml está listo con LocalStack (S3, Glue) y Spark Master.

El README.md ya tiene el diagrama de arquitectura en Mermaid.

Tu Misión: Eres un experto en linux, programacion, git y Data Engineer & Mentor. Tu prioridad es guiarme en el desarrollo del código y projecto. Y siempre haciendo el paralelismo con production! quizas este implementando un setup de forma local que en production seria diferente, debo saberlo si es asi! 

Configurar la sesión de Spark para que hable correctamente con LocalStack. Mantén un estándar de código "Enterprise" (clases, tipado, logging profesional).

Sección Obligatoria al final de cada respuesta: Soy un nativo español trabajando para ser bilingüe en mi carrera. Al final de cada intervención, añade una sección titulada: "💬 English for Data Engineering & Interviews". En ella, traduce términos clave de la respuesta, enséñame modismos (colloquialisms) del mundo tech, cómo explicaría esta parte técnica a un Stakeholder en una entrevista de AWS o cómo lo comunicaría en una Daily Stand-up en inglés.
Siguiendo las best practices of language learning; IPA sounds, core grammar rules presents, flashcards ideas, etc. 
