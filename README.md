## Exécution du Projet
1. **Lance les contenaires**
    ```bash
    cd <project_directory>
    docker-compose up -d
    ```
1. **Démarrer le Producteur Kafka** :
   Configurez un producteur Kafka pour diffuser les tweets vers le topic `tweet_topic`. 
   ```bash
   cd KAFKA
   python kafka-producer.py
   ```
2. **Ajouter le fichier Jar de SPARK dans le docker master**
    ```bash
    cd <project_directory>
    docker cp .\SPARK\spark_2.12-0.1.jar spark_master:/opt/bitnami/spark
    ```
2. **Lancer l'Application Spark Streaming** :
   Soumettez l'application Spark au cluster :
    ```bash
    docker exec -it spark_master /bin/bash 
    spark-submit \
        --master spark://spark-master:7077 \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.mongodb.spark:mongo-spark-connector_2.12:10.2.1 \
        --class KafkaSparkConsumer \
        spark_2.12-0.1.jar
    ```

3. **Surveiller les Résultats** :
   - Les tweets traités seront enregistrés dans la collection MongoDB `tweetCollection`.
   - Se connecter à mongodb
    ```bash
    cd <project_directory>
    docker exec -it mongodb mongosh
    ```
   - Vérifiez en vous connectant à MongoDB et en interrogeant la collection :
     ```bash
     use tweetDB
     db.tweetCollection.find()
     ```

