#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "esp_log.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "esp_http_client.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

#define WIFI_SSID "192.168.0.162"        // Replace with your Wi-Fi SSID
#define WIFI_PASS "pshcso01"    // Replace with your Wi-Fi password
#define TAG "UART_HTTP"

// UART Parameters
#define UART_TXD_PIN 43
#define UART_RXD_PIN 44
#define UART_BAUD_RATE 115200
#define UART_PORT UART_NUM_0
#define BUF_SIZE 1024

// HTTP Server URL
#define SERVER_URL "http://127.0.0.1:5000/charts"

// Global Variables for Data
static int latest_channel1 = 0;
static int latest_channel2 = 0;
static int latest_channel3 = 0;
static int latest_channel4 = 0;

// Wi-Fi Initialization
void wifi_init_sta() {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
        },
    };
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Connecting to Wi-Fi...");
    ESP_ERROR_CHECK(esp_wifi_connect());
    ESP_LOGI(TAG, "Connected to Wi-Fi.");
}

// Function to Send Data to the Server
static void send_data_to_server(int channel_1, int channel_2, int channel_3, int channel_4) {
    char post_data[128];
    snprintf(post_data, sizeof(post_data),
             "{\"channel_1\": %d, \"channel_2\": %d, \"channel_3\": %d, \"channel_4\": %d}", channel_1, channel_2, channel_3, channel_4);

    esp_http_client_config_t config = {
        .url = SERVER_URL,
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);

    esp_http_client_set_method(client, HTTP_METHOD_POST);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, post_data, strlen(post_data));

    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Data sent successfully: HTTP Status = %d",
                 esp_http_client_get_status_code(client));
    } else {
        ESP_LOGE(TAG, "Failed to send data: %s", esp_err_to_name(err));
    }

    esp_http_client_cleanup(client);
}

// UART Task for Reading Sensor Data
static void echo_task_uart(void *arg) {
    uart_config_t uart_config = {
        .baud_rate = UART_BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    ESP_ERROR_CHECK(uart_driver_install(UART_PORT, BUF_SIZE * 2, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_PORT, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(UART_PORT, UART_TXD_PIN, UART_RXD_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));

    char *data = (char *)malloc(BUF_SIZE);
    if (!data) {
        ESP_LOGE(TAG, "Failed to allocate memory for UART data");
        vTaskDelete(NULL);
    }

    while (1) {
        int len = uart_read_bytes(UART_PORT, data, (BUF_SIZE - 1), 20 / portTICK_PERIOD_MS);
        if (len > 0) {
            data[len] = '\0'; // Null-terminate the string

            int channel_1_val, channel_2_val, channel_3_val, channel_4_val;
            if (sscanf(data, "%d %d %d %d", &channel_1_val, &channel_2_val, &channel_3_val, &channel_4_val) == 4) {
                ESP_LOGI(TAG, "UART Data: channel_1=%d,channel_2_val=%d,channel_3_val=%d, channel_4_val = %d", channel_1_val, channel_2_val, channel_3_val, channel_4_val);

                // Update Global Variables
                latest_channel1 = channel_1_val;
                latest_channel2 = channel_2_val;
                latest_channel3 = channel_3_val;
                latest_channel4 = channel_4_val;

                // Send Data to the Server
                send_data_to_server(latest_channel1, latest_channel2, latest_channel3, latest_channel4);
            } else {
                ESP_LOGW(TAG, "Invalid UART data format: %s", data);
            }
        }
        vTaskDelay(500 / portTICK_PERIOD_MS);
    }

    free(data);
    vTaskDelete(NULL);
}

// Main Application
void app_main(void) {
    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Initialize Wi-Fi
    wifi_init_sta();

    // Start UART Task
    xTaskCreate(echo_task_uart, "uart_receive_task", 4096, NULL, 10, NULL);
}
