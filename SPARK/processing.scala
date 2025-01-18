import org.apache.spark.sql.{SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.StreamingQuery
import org.apache.spark.sql.expressions.UserDefinedFunction
import java.io.DataOutputStream  // Import ajouté
import scala.io.Source
import java.net.{URL, HttpURLConnection}

object KafkaSparkConsumer {
  def main(args: Array[String]): Unit = {

    // Créez la session Spark
    val spark = SparkSession.builder
      .appName("KafkaSparkConsumer")
      .config("spark.mongodb.read.connection.uri", "mongodb://192.168.1.6/tweetDB.tweetCollection")
      .config("spark.mongodb.write.connection.uri", "mongodb://192.168.1.6/tweetDB.tweetCollection")
      .getOrCreate()

    // Paramètres pour consommer depuis Kafka
    val kafkaBrokers = "kafka:9092" 
    val topic = "tweet_topic"

    // Lecture de Kafka
    val kafkaStream = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", kafkaBrokers)
      .option("subscribe", topic)
      .load()

    // Le Kafka stream contient les données sous forme de bytes
    // Nous devons les convertir en String
    val messageStream = kafkaStream.selectExpr("CAST(value AS STRING) as message")

    // Extraction des tweets JSON
    val tweetStream = messageStream
      .select(get_json_object(col("message"), "$.tweet").alias("tweet"),
              get_json_object(col("message"), "$.created_at").alias("created_at"),
              get_json_object(col("message"), "$.followers_count").alias("followers_count"),
              get_json_object(col("message"), "$.retweet_count").alias("retweet_count"),
              get_json_object(col("message"), "$.favorite_count").alias("favorite_count"),
              get_json_object(col("message"), "$.user").alias("user"))
      .filter(col("tweet").isNotNull)

    // Définir l'UDF pour nettoyer un tweet
    val cleanTweetUdf: UserDefinedFunction = udf((tweet: String) => {
      if (tweet != null) {
        tweet.toLowerCase()
          .replaceAll("http\\S+|www\\S+|https\\S+", "") // supprimer les URL
          .replaceAll("@\\w+|#", "") // supprimer les mentions et hashtags
          .replaceAll("\\d+", "") // supprimer les nombres
          .replaceAll("<.*?>", "") // supprimer les balises HTML
          .replaceAll("[^\\w\\s]", "") // supprimer la ponctuation
          .replaceAll("\\s+", " ") // supprimer les espaces superflus
          .trim() // supprimer les espaces en début et fin
      } else {
        ""
      }
    })

    // Définir l'UDF pour extraire les hashtags
    val extractHashtagsUdf: UserDefinedFunction = udf((tweet: String) => {
      if (tweet != null) {
        tweet.split(" ").filter(word => word.startsWith("#")).toSeq
      } else {
        Seq.empty[String]
      }
    })

    // Nettoyage du tweet
    val cleanedTweetStream = tweetStream
      .select(cleanTweetUdf(col("tweet")).alias("cleaned_tweet"),
              col("followers_count"),
              col("retweet_count"),
              col("favorite_count"),
              col("user"),
              col("created_at"))

    // Extraction du sentiment
    val tweetWithSentimentStream = cleanedTweetStream
      .withColumn("sentiment", udf(getSentiment _).apply(col("cleaned_tweet")))

    // Extraction des hashtags
    val tweetWithHashtagsStream = tweetWithSentimentStream
      .withColumn("hashtags", extractHashtagsUdf(col("cleaned_tweet")))

    // Calcul des statistiques d'engagement
    val tweetWithEngagementStream = tweetWithHashtagsStream
      .withColumn("engagement", col("followers_count") * 
                                  (col("sentiment") === "positive").cast("int") * 
                                  (col("favorite_count") + col("retweet_count")))

    // Enregistrement des résultats dans MongoDB
    val query: StreamingQuery = tweetWithEngagementStream.writeStream
      .outputMode("append")
      .format("mongodb")
      .option("checkpointLocation", "/tmp/mongo_checkpoint")
      .start()

    query.awaitTermination()
  }

  // Fonction pour appeler l'API de sentiment
  def getSentiment(tweet: String): String = {
    try {
      val apiUrl = "http://sentiment-api:5000/analyze"
      val connection = new URL(apiUrl).openConnection().asInstanceOf[HttpURLConnection]
      connection.setRequestMethod("POST")
      connection.setDoOutput(true)
      connection.setRequestProperty("Content-Type", "application/json")
      val jsonTweet = s"""{"tweet": "$tweet"}"""

      val out = new DataOutputStream(connection.getOutputStream)  // Ajout de la ligne DataOutputStream
      out.writeBytes(jsonTweet)  
      out.flush()

      // Lire la réponse de l'API
      val response = Source.fromInputStream(connection.getInputStream).mkString

      // Retourner le sentiment en fonction de la réponse
      response.toUpperCase match {
        case r if r.contains("POSITIVE") => "positive"
        case r if r.contains("NEGATIVE") => "negative"
        case r if r.contains("NEUTRAL")  => "neutral"
        case _ => "unknown"
      }
    } catch {
      case e: Exception => 
        println(s"Erreur d'API: ${e.getMessage}")
        "unknown"
    }
  } 
}
