/**
 * Server for IR Cam
 */

const char* ssid = "Spreewunder";
const char* password = "02053063312159240827";
int port = 1234;

/**
 * Code
 */

#include "WiFi.h"
#include "AsyncTCP.h"
#include <Wire.h>
#include <ESPmDNS.h>
#include "MLX90640_API.h"
#include "MLX90640_I2C_Driver.h"

#define MIN(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a < _b ? _a : _b; })

const byte MLX90640_address = 0x33;
#define TA_SHIFT 8
float mlx90640To[768];
paramsMLX90640 mlx90640;
byte sendbuffer[3079];

static std::vector<AsyncClient*> clients;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(1000000);
  WiFi.mode(WIFI_STA);
  
  WiFi.begin(ssid, password);
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("connecting");
    delay(5000);
    WiFi.begin(ssid, password);
  }

  while (isConnected() == false) {
    Serial.println("IR Sensor not detected");
    delay(1000);
  }

  setupIR();

  if (!MDNS.begin("com.spreewunder.ircam")) {
    Serial.println("Error setting up MDNS responder!");
  }
  MDNS.addService("irstream", "tcp", port);

  AsyncServer* server = new AsyncServer(IPAddress(0,0,0,0), 1234); // start listening on tcp port 7050
  server->onClient(&handleNewClient, server);
  server->begin();
  Serial.print("Sending Updates");
}

static void handleNewClient(void* arg, AsyncClient* client) {
  Serial.printf("\n new client has been connected to server, ip: %s", client->remoteIP().toString().c_str());
  clients.push_back(client);
  client->onDisconnect(&handleDisconnect, client);
}

static void handleDisconnect(void* arg, AsyncClient* client) {
  Serial.printf("\n client has been disconnected from server, ip: %s", client->remoteIP().toString().c_str());
  clients.erase(std::remove(clients.begin(), clients.end(), client), clients.end());
}

byte x = 0;

void loop() {
      int s = millis();
      getFrame();
      size_t frameSize = sizeof(sendbuffer);
      size_t sliceSize = 256;

      int alreadySend = 0;
      for (int i = 0; i < frameSize; i += sliceSize) {
        for(int j = 0; j < clients.size(); j++) {
          if (clients[j]->canSend()) {
            clients[j]->write((const char *)(sendbuffer + i), MIN(sliceSize, frameSize-alreadySend));
          }
        }
        alreadySend += sliceSize;
      }
      int st = millis();
}

void getFrame () {
  uint16_t mlx90640Frame[834];
  int status = MLX90640_GetFrameData(MLX90640_address, mlx90640Frame);

  float vdd = MLX90640_GetVdd(mlx90640Frame, &mlx90640);
  float Ta = MLX90640_GetTa(mlx90640Frame, &mlx90640);

  float tr = Ta - TA_SHIFT;
  float emissivity = 0.95;

  MLX90640_CalculateTo(mlx90640Frame, &mlx90640, emissivity, tr, mlx90640To);

  memcpy(sendbuffer+7, mlx90640To, 3072);
  sendbuffer[3] = millis();
}

void setupIR () {
  int status;
  uint16_t eeMLX90640[832];
  status = MLX90640_DumpEE(MLX90640_address, eeMLX90640);
  if (status != 0)
    Serial.println("Failed to load system parameters");

  status = MLX90640_ExtractParameters(eeMLX90640, &mlx90640);
  if (status != 0)
    Serial.println("Parameter extraction failed");
  
  MLX90640_SetRefreshRate(MLX90640_address, 0x05);

  sendbuffer[0] = 0x00;
  sendbuffer[1] = 0xFF;
  sendbuffer[2] = 0x00;
}

bool isConnected() {
  Wire.beginTransmission((uint8_t) MLX90640_address);
  if (Wire.endTransmission() != 0) {
    return false;
  } else {
    return true;
  }
}
