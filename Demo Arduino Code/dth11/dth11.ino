#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define DHTPIN D2
#define DHTTYPE DHT11

const char* ssid = "--Your SSID--";
const char* password = "--Your Wifi Password--";
const char* server_ip = "--Your Local IP Address(same as SPLDAEMON value in conf.json)--";
const int server_port = 8080;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.println("DHT11 Sensor Reading...");
  dht.begin();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Error reading data from DHT11 sensor!");
    delay(10000);
    return;
  }
  String Message = "Normal conditions";
  if(temperature > 26 || humidity > 36){
      Message = "Temperature or Humidity exceeded beyond limit";
  }
  String log_data = "{\"humidity\": " + String(humidity) + ", \"temperature\": " + String(temperature) +", \"Message\":\""+Message+"\", \"ip\": \"" + WiFi.localIP().toString() + "\"}";
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    String server_url = String("http://") + server_ip + ":" + server_port;
    Serial.println("Sending data to URL: " + server_url);
    http.begin(client, server_url);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(log_data);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response from server: " + response);
    } else {
      Serial.println("Error on sending POST: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print("%, Temperature: ");
  Serial.print(temperature);
  Serial.println("°C");

  delay(8000);
}
