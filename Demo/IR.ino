//#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
/**
#define DHTPIN D2
#define DHTTYPE DHT11
**/
const char* ssid = "Moto G73";
const char* password = "Rahil@30";
const char* server_ip = "192.168.234.127";
const int server_port = 8080;
const int sensorPin = D1;     // IR Obstacle Sensor output pin
const int ledPin = D2;        // LED pin for obstacle indication
String log_data;
//DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
//  Serial.println("DHT11 Sensor Reading...");
//  dht.begin();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // IR Obstacle Sensor reading
  int sensorValue = digitalRead(sensorPin);
  /**if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Error reading data from DHT11 sensor!");
    delay(10000);
    return;
  }**/
  if (sensorValue == 0)
  {
    log_data = "{\"Sensor Output\": " + String(sensorValue) + ", \"Message\": \"Object Detected.\", \"ip\": \"" + WiFi.localIP().toString() + "\"}";
  }
  else
  {
    log_data = "{\"Sensor Output\": " + String(sensorValue) + ", \"Message\": \"There is no object.\", \"ip\": \"" + WiFi.localIP().toString() + "\"}";
  }
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
  /**
  Serial.print("Humidity: ");
  Serial.print(sensorValue);
  Serial.print("%, Temperature: ");
  Serial.print(sensorValue);
  Serial.println("°C");
  **/
  Serial.println(log_data);
  delay(8000);
}