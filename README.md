# Examen P2: Pipeline Hadoop + PostgreSQL + API (Docker)

**Matrícula:** 125052506
**Pregunta asignada (último dígito 6):** Top 10 productos por ingreso total en todo el año (ingreso = cantidad × precio_unitario).

## Cómo reproducir

1. Clonar y preparar variables:

```bash
git clone https://github.com/Alejandro-Jimenez-Reyes/examen-p2-125052506.git
cd examen-p2-125052506
cp .env.example .env     # editar POSTGRES_PASSWORD
```

2. Generar el dataset (no se sube al repo):

```bash
cd data && python3 generar_dataset.py 125052506 && cd ..
```

3. Levantar el ambiente:

```bash
docker compose up --build -d
docker compose exec hadoop hadoop version
```

4. Ejecutar el job de MapReduce (Hadoop Streaming, modo standalone):

```bash
docker compose exec hadoop bash -c "rm -rf /salida/job_top10 && time hadoop jar \$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \
  -D mapreduce.framework.name=local -D fs.defaultFS=file:/// \
  -files /mapreduce/mapper.py,/mapreduce/reducer.py \
  -mapper 'python3 mapper.py' -reducer 'python3 reducer.py' \
  -input file:///data/input/ventas_125052506.csv -output file:///salida/job_top10"
```

5. Cargar resultados (lee `part-00000`, ordena y se queda con el top 10) y consultar la API:

```bash
docker compose exec api python /scripts/cargar_resultados.py
curl -s localhost:8000/resultados
curl -s localhost:8000/resultados/BEB-0012
```

6. Versión secuencial para comparar:

```bash
time python3 mapreduce/secuencial.py data/ventas_125052506.csv
```

## Arquitectura

- `hadoop`: Debian bullseye-slim + OpenJDK 11 + Python 3 + Hadoop 3.3.6 (standalone) + OpenSSH Server. El dataset se monta de solo lectura en `/data/input`.
- `db`: PostgreSQL 16 con volumen nombrado `pgdata` y credenciales en `.env`.
- `api`: FastAPI, se conecta a `db` por nombre de servicio. Depende de `db` (`depends_on` con healthcheck).
- Los tres servicios están en la red `datamart`.

## Endpoints

| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| GET | `/` | Estado |
| GET | `/resultados` | Todos los registros |
| GET | `/top` | Top 10 por ingreso |
| GET | `/resultados/{clave}` | Ingreso de un producto |
| POST | `/resultados` | Inserta o actualiza un producto |
| PUT | `/resultados/{clave}` | Actualiza el ingreso |
| DELETE | `/resultados/{clave}` | Elimina un producto |

## SSH (sin contraseña)

El contenedor `hadoop` ejecuta `sshd` con `PasswordAuthentication no`. Las llaves se generan al arrancar (`hadoop/start.sh`) y se comparten por el volumen `sshkeys`, por lo que no hay contraseñas ni llaves en el repositorio ni en la imagen.

```bash
docker compose exec hadoop ssh localhost hostname
docker compose exec api ssh -o StrictHostKeyChecking=no -i /keys/id_rsa root@hadoop hostname
```

## Tiempos medidos (5 millones de registros, 336 MB)

| Método | Tiempo |
| ------ | ------ |
| Secuencial (Python) | 4.6 s |
| Hadoop Streaming (local, en Docker) | 13.2 s |

Ambos dan el mismo resultado (1.º BEB-0012 con 126095353.78).

**Explicación:** en una sola máquina Hadoop es más lento porque paga el arranque de la JVM, la ejecución de mapper y reducer como procesos externos, la serialización, el shuffle/sort y la escritura de archivos intermedios. Su ventaja aparece al escalar a muchos nodos con datos que no caben en un solo equipo. Con 336 MB, el script secuencial es más eficiente.

## Evidencias

![hadoop version](evidencias/01_hadoop_version.png)
![ssh localhost](evidencias/02_ssh_localhost.png)
![ssh entre contenedores](evidencias/03_ssh_entre_contenedores.png)
![secuencial](evidencias/04_secuencial.png)
![salida del job](evidencias/05_salida_job.png)
![top 10 hadoop](evidencias/05b_top10_hadoop.png)
![respuesta API](evidencias/06_respuesta_api.png)
![persistencia](evidencias/07_persistencia.png)

## Parte E. Teoría

**1. Modos de Hadoop.** En *standalone* todo corre en un solo proceso Java, sin demonios y sin HDFS (usa el sistema de archivos local). En *pseudo-distribuido* corren todos los demonios (NameNode, DataNode, ResourceManager, NodeManager) en una sola máquina, cada uno en su propio proceso, para simular un clúster. En *totalmente distribuido* los demonios están repartidos en varios nodos físicos. HDFS se usa en el pseudo-distribuido y en el distribuido; en standalone no.

**2. Volumen en lugar de COPY.** (a) El dataset pesa cientos de MB; con `COPY` la imagen se infla y tarda en construirse. (b) Los datos son distintos por alumno y cambian entre ejecuciones; con `COPY` habría que reconstruir la imagen cada vez. (c) Con un volumen `:ro` los datos no se pueden modificar desde el contenedor. (d) Se evita subir el CSV al repositorio o a un registry.

**3. `down` vs `down -v`.** `docker compose down` elimina contenedores y redes pero conserva los volúmenes nombrados, así que los datos de PostgreSQL siguen ahí al hacer `up`. `docker compose down -v` también elimina los volúmenes nombrados, y se pierde toda la base de datos.

**4. MapReduce vs secuencial.** Con 400 MB un solo equipo lee el archivo rápido. MapReduce paga costos fijos: arranque de la JVM, mapper y reducer como procesos externos, shuffle/sort y archivos intermedios (aquí 13.2 s contra 4.6 s). Conviene cuando los datos no caben en la memoria o el disco de una máquina (decenas de GB o TB), cuando hay un clúster que paralelice el trabajo y cuando el procesamiento es lo bastante pesado como para amortizar el overhead.

**5. CMD vs ENTRYPOINT; COPY vs ADD.** ENTRYPOINT define el ejecutable fijo del contenedor; CMD da el comando o argumentos por defecto y se sobrescribe con `docker run imagen comando`. Si hay ambos, CMD se pasa como argumentos de ENTRYPOINT. COPY solo copia archivos locales; ADD además descomprime tar locales y puede descargar URLs, por eso se prefiere COPY.