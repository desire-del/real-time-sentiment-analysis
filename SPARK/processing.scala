import org.apache.spark.sql.{SparkSession}
import org.apache.spark.sql.functions._

object KafkaSparkConsumer {
  def main(args: Array[String]): Unit = {

    // Créez la session Spark
    val spark = SparkSession.builder
      .appName("KafkaSparkConsumer")
      .config("spark.mongodb.read.connection.uri", "mongodb://192.168.1.6/tweetDB.tweetCollection")
      .config("spark.mongodb.write.connection.uri", "mongodb://192.168.1.6/tweetDB.tweetCollection")
      .getOrCreate()

    // Paramètres pour consommer depuis Kafka
    val kafkaBrokers = "kafka:9092" // Adresse du broker Kafka
    val topic = "tweet_topic"      // Nom du topic Kafka

    // Lecture de Kafka
    val kafkaStream = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", kafkaBrokers)
      .option("subscribe", topic)
      .load()

    // Le Kafka stream contient les données sous forme de bytes
    // Nous devons les convertir en String
    val messageStream = kafkaStream.selectExpr("CAST(value AS STRING) as message")

    // Extraction et affichage des tweets
    val tweetStream = messageStream
      .select(get_json_object(col("message"), "$.text").alias("tweet"))
      .filter(col("tweet").isNotNull) // Filtre pour éviter les lignes sans contenu

    // Affichage des tweets sur la console
    val query = tweetStream.writeStream
      .outputMode("append")
      .format("mongodb")
      .option("checkpointLocation", "/tmp/mongo_checkpoint")
      .start()

    // Attendre que le stream se termine
    query.awaitTermination()
  }
}
