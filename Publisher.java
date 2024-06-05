import javax.jms.Session;
import javax.jms.TextMessage;
import org.apache.activemq.ActiveMQConnectionFactory;
public class Publisher {
public static void main(String[] args) {
 try {
 ConnectionFactory connectionFactory = new
ActiveMQConnectionFactory("tcp://localhost:61616");
 Connection connection = connectionFactory.createConnection();
connection.start();
Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
MessageProducer producer = session.createProducer(session.createTopic("MyTopic"));
producer.setDeliveryMode(DeliveryMode.NON_PERSISTENT);
for (int i = 0; i < 10; i++) {
 TextMessage message = session.createTextMessage("Message " + i);
producer.send(message);
System.out.println("Sent message: " + message.getText());
 }
connection.close();
 } catch (Exception e) {
 e.printStackTrace();
 }
}
}