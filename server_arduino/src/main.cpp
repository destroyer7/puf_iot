#include <Arduino.h>
#include <stdio.h>
#include <Tools.h>
#include <BCH.h>
#include <SRAM_CY62256N.h>
#include <SPI.h>
#include <SD.h>
#include <Crypto.h>
#include <SHA3.h>
#include <string.h>
#include <AES.h>

#define PIN_POWER_ANALOG A8
#define PIN_POWER 9

BCH bch;
Tools tools;

SRAM_CY62256N sram;

uint8_t helper_data_new[7 * 37];
uint8_t puf_binary_new[8 * 37];
uint8_t key_per_row[37];
uint8_t key_256[32];
uint8_t key_32[32];

boolean readBit(long location) {
  uint8_t result = sram.read(floor(location / 8));
  return result >> (7 - (location % 8)) & 0x1 == 1;
}

void set() {
  bch = BCH();
  tools = Tools();
  bch.initialize();               /* Read m */  
}

void gen_key256(){
  memset(key_256, 0, 32 * sizeof(uint8_t));
  memcpy(&key_256, &puf_binary_new, 32 * sizeof(uint8_t));
}

void gen_helper_data(){
  gen_key256();

  tools.gen_key_per_row(key_256, key_per_row);

  uint8_t encoded_new[8*37];
  uint8_t xor_enroll_new[8*37];

  int row = 37;
  int n = bch.get_n();
  int k = bch.get_key_length();
  int index, shift, ii;

  /******************** ASSERT ENCODED **********************/
  for (int i = 0; i < row; i++) {
      bch.encode_bch(&key_per_row[i], &encoded_new[i * 8]);
  }

  /******************** ASSERT XOR ENROLL **********************/
  for (int i = 0; i < row; i++) {
      for (int j = 0; j < 8; j++) {
        xor_enroll_new[i*8 + j] = encoded_new[i*8 + j] ^ puf_binary_new[i*8 + j];
      }
  }

  /******************** ASSERT HELPER DATA **********************/
  for (int i = 0; i < 37; i++) {
      memcpy(&helper_data_new[i * 7], &xor_enroll_new[i * 8], 7 * sizeof(uint8_t));
  }

  File myFile = SD.open("h.txt", O_WRITE | O_CREAT | O_TRUNC);
  if (myFile) {
    for (int i = 0; i < 37*7;i++){
      myFile.println(helper_data_new[i]);
    }
    myFile.close();
  }
}

void decode(uint8_t *key_32) {
  BCH bch;
  Tools tools;
  bch.initialize();

  uint8_t helper_data_padded_new[8 * 37];
  uint8_t xor_reproduction_new[8 * 37];
  uint8_t reconstructed_key_new[37];

  memset(helper_data_padded_new, 0, sizeof(helper_data_padded_new));
  memset(xor_reproduction_new, 0, sizeof(xor_reproduction_new));
  memset(reconstructed_key_new, 0, sizeof(reconstructed_key_new));

  int row = 37;
  int n = bch.get_n();
  int k = bch.get_key_length();

  int k_length_bit = row;//tools.ceil(k*row,8);
  int n_length_bit = row * 8;//tools.ceil(n*row,8);

  long thisItem[7];

  /************************************
   ****** REPRODUCTION PROCEDURE ******
   ************************************/
  /******************** ASSERT HELPER DATA PADDED**********************/
  for (int i = 0; i < row; i++) {
    memcpy(&helper_data_padded_new[i * 8], &helper_data_new[i * 7], 7 * sizeof(uint8_t));
  }

  /******************** ASSERT XOR REPRODUCTION **********************/
  for (int i = 0; i < row; i++) {
    for (int j = 0; j < 8; j++) {
      xor_reproduction_new[i * 8 + j] = puf_binary_new[i * 8 + j] ^ helper_data_padded_new[i * 8 + j];
    }
  }

  /******************** ASSERT RECONSTRUCTED KEY **********************/
  for (int i = 0; i < row; i++) {
    bch.decode_bch(&xor_reproduction_new[i * 8], &reconstructed_key_new[i]);
  }

  tools.convert_key_back(reconstructed_key_new, key_32);
}

void initializeSD() {
  Serial.print("Initializing SD card...");

  if (!SD.begin(53)) {
    Serial.println("initialization failed!");
    delay(2000);
    exit(0);
  }
  Serial.println("initialization done.");
}

boolean isValidNumber(String str) {
  if (str.length() == 0)
    return false;
  for (byte i = 0; i < str.length(); i++)
  {
    if (!isDigit(str.charAt(i)))
      return false;
  }
  return true;
}

String convertString(String a) {
  String s;
  boolean isNum;
  for (byte i = 0; i < a.length(); i++)
  {
    isNum = isDigit(a.charAt(i));
    if (isNum)
      s += a.charAt(i);
  }
  return s;
}

void readResponefromMicroSD() {
  memset(puf_binary_new, 0, sizeof(puf_binary_new));
  int i = 0;

  String name = "R.TXT";
  String a, b;
  long thisItem;
  File myFile = SD.open(name);
  if (myFile) {
    while (myFile.available()) {
      a = myFile.readStringUntil('\n');
      b = convertString(a);
      if (isValidNumber(b)) {
        thisItem = b.toInt();
        puf_binary_new[i] = thisItem;
        i++;
      }
    }
    myFile.close();
  } else {
    Serial.println("error opening R.TXT ");
  }
}

void readHelperDatafromMicroSD() {
  memset(helper_data_new, 0, sizeof(helper_data_new));
  // read
  int i = 0;

  String name = "H.TXT";
  String a, b;
  long thisItem;
  File myFile = SD.open(name);
  if (myFile) {
    while (myFile.available()) {
      a = myFile.readStringUntil('\n');
      b = convertString(a);
      if (isValidNumber(b)) {
        thisItem = b.toInt();
        helper_data_new[i] = thisItem;
        i++;
      }
    }
    myFile.close();
  } else {
    Serial.println("error opening H.TXT ");
  }
}

void write_key(){
  File myFile = SD.open("K.TXT", O_WRITE | O_CREAT | O_TRUNC);
  if (myFile) {
    for (int i = 0; i < 32;i++){
      myFile.println(key_32[i]);
    }
    myFile.close();
  }
}

void print_key(uint8_t* key, uint8_t length) {
  for (int i = 0; i < length; i++) {
    Serial.print("0123456789abcdef"[key[i] >> 4]);
    Serial.print("0123456789abcdef"[key[i] & 0xf]);
  }
  Serial.println();
}

void setup(void)
{ 
  //**************All files in caps: R.TXT, C.TXT, H.TXT *******************************
  Serial.begin(115200);
  set(); 
  initializeSD();  
  delay(1000);
  memset(key_32, 0, sizeof(key_32));

  readResponefromMicroSD();
  gen_helper_data();
  
  decode(key_32);
  Serial.println();
  Serial.print("PUF key \t: ");
  print_key(key_32, 32);
  write_key();
}

void loop() {
  delay(1000);
  exit(0);
}
