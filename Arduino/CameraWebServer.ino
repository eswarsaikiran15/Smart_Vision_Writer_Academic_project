#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "board_config.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// ── WiFi ──────────────────────────────────────────────
const char* ssid     = "S23";
const char* password = "12345678";

// ── YOUR LAPTOP IP ────────────────────────────────────
const char* python_server_url = "http://10.250.49.110:5000/trigger";

// ── PIR PIN ───────────────────────────────────────────
#define PIR_PIN 13  // Digital signal from PIR sensor

// ── SHARED STATE ──────────────────────────────────────
volatile bool motionDetected = false;
unsigned long lastTriggerTime = 0;
const int     COOLDOWN_MS     = 10000;

void startCameraServer();
void setupLedFlash();

// ════════════════════════════════════════════════════════
// PIR TASK — runs independently on Core 0
// ════════════════════════════════════════════════════════
void pirTask(void* pvParameters) {
  pinMode(PIR_PIN, INPUT);
  Serial.println("PIR monitor task started on Core 0");

  for (;;) {
    int sensorSignal = digitalRead(PIR_PIN);
    
    // This print proves the sensor is electrically active
    if (sensorSignal == HIGH) {
      Serial.println(">>> HARDWARE: PIR SIGNAL HIGH <<<");
      motionDetected = true;
    }
    
    vTaskDelay(pdMS_TO_TICKS(200));
  }
}
// ════════════════════════════════════════════════════════
// SETUP
// ════════════════════════════════════════════════════════
void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println("\n=== Smart Vision Writer (PIR Mode) ===");

  // ── Camera init ─────────────────────────────────────
  camera_config_t config;
  config.ledc_channel  = LEDC_CHANNEL_0;
  config.ledc_timer    = LEDC_TIMER_0;
  config.pin_d0        = Y2_GPIO_NUM;
  config.pin_d1        = Y3_GPIO_NUM;
  config.pin_d2        = Y4_GPIO_NUM;
  config.pin_d3        = Y5_GPIO_NUM;
  config.pin_d4        = Y6_GPIO_NUM;
  config.pin_d5        = Y7_GPIO_NUM;
  config.pin_d6        = Y8_GPIO_NUM;
  config.pin_d7        = Y9_GPIO_NUM;
  config.pin_xclk      = XCLK_GPIO_NUM;
  config.pin_pclk      = PCLK_GPIO_NUM;
  config.pin_vsync     = VSYNC_GPIO_NUM;
  config.pin_href      = HREF_GPIO_NUM;
  config.pin_sccb_sda  = SIOD_GPIO_NUM;
  config.pin_sccb_scl  = SIOC_GPIO_NUM;
  config.pin_pwdn      = PWDN_GPIO_NUM;
  config.pin_reset     = RESET_GPIO_NUM;
  config.xclk_freq_hz  = 20000000;
  config.frame_size    = FRAMESIZE_UXGA;
  config.pixel_format  = PIXFORMAT_JPEG;
  config.grab_mode     = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location   = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality  = 12;
  config.fb_count      = 1;

  if (psramFound()) {
    config.jpeg_quality = 10;
    config.fb_count     = 2;
    config.grab_mode    = CAMERA_GRAB_LATEST;
  } else {
    config.frame_size  = FRAMESIZE_SVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init FAILED: 0x%x\n", err);
    return;
  }

  sensor_t* s = esp_camera_sensor_get();
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  Serial.println("Camera OK");

  // ── WiFi ────────────────────────────────────────────
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP: http://");
  Serial.println(WiFi.localIP());

  // ── Camera server ───────────────────────────────────
  startCameraServer();
  Serial.println("Camera server started on Core 1");

  // ── Start PIR monitor on Core 0 ─────────────────────
  xTaskCreatePinnedToCore(
    pirTask,
    "PIR_Monitor",
    4096,
    NULL,
    2,
    NULL,
    0
  );

  Serial.println("=== System Ready ===");
}

// ════════════════════════════════════════════════════════
// LOOP — triggers Flask server
// ════════════════════════════════════════════════════════
void loop() {
  unsigned long now = millis();
  bool cooldownOver = (now - lastTriggerTime) > COOLDOWN_MS;

  if (motionDetected && cooldownOver) {
    motionDetected = false; 
    lastTriggerTime = now;

    Serial.println("Event: Cooldown over. Triggering Flask server...");

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(python_server_url);
      http.setTimeout(10000);
      int code = http.GET();

      if (code == 200) {
        Serial.println("Response: Flask Server accepted the trigger.");
      } else {
        Serial.printf("Response: Server error code %d\n", code);
      }
      http.end();
    } else {
      Serial.println("Network: WiFi lost. Attempting reconnect.");
      WiFi.reconnect();
    }
  }

  delay(100);
}
