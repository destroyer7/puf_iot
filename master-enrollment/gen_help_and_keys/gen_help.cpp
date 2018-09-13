#include <stdio.h>
#include "Tools.h"
#include "BCH.h"
#include <fstream>
#include <string>
#include <stdint.h>
#include <iostream>
#include <bitset>
#include <iomanip>

uint8_t puf_binary_new[8*37];
uint8_t key_256[32];
uint8_t key_per_row[37];
uint8_t helper_data_new[7*37];

BCH bch;
Tools tools;

void get_response(int j){
    memset(puf_binary_new, 0, sizeof(puf_binary_new));
    uint8_t result;

    // read
    int index = 0, i=0;
    string name = "r";
    name += to_string(j);
    name += ".txt";

    int bit = 0;
    ifstream myFile(name);
    if (myFile) {
        cout << "File " << name << " open successfull" << endl;
        for ( int count = 0; count < 2331; count ++) 
        {
            string a;
            getline(myFile, a);
            bit = int(a[0]) - 48;
            //cout<<bit<<endl 
            if((bit))
            puf_binary_new[index] = puf_binary_new[index] | 0x1;
            if ((i+1)%8==0)
            {
                index++;
            } 
            else
            {
                puf_binary_new[index] = puf_binary_new[index] << 1;
            }
            i++;
        }
        cout << "Response file read successful" <<endl;
        myFile.close();
    }
    else  cout << "Error Opening File" << endl;
}

void gen_key_per_row(uint8_t *keys, uint8_t *result) {
    int index_result = 0, index_key = 0;
    uint8_t shift;
    for (int i = 0; i < 256; i++) {
        shift = 7 - (i % 8);
        if ((keys[index_key] >> shift) & 0x1) {
            result[index_result] = result[index_result] | 0x1;
        }
        if ((i + 1) % 7 == 0) {
            result[index_result] = result[index_result] << 1;
            index_result++;
        } else {
            result[index_result] = result[index_result] << 1;
        }
        if ((i + 1) % 8 == 0) {
            index_key++;
        }
    }
    result[index_result] = result[index_result] << 3;
}

void gen_helper_data(int h){
    
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

    string name = "h";
    name += to_string(h);
    name += ".txt";
    ofstream myFile(name);

    if (myFile.is_open())
    {  
        cout<<"File "<<name<<" create successfull"<<endl; 
        for (int i = 0; i < 37*7;i++){
        myFile <<helper_data_new[i]<<endl;
        }
        myFile.close();
        cout<<"File "<<name<<" write successfull"<<endl;
    }
    else cout<<"File "<<name<<" open error"<<endl;
}

// void readHelperDatafromMicroSD() {
//     memset(helper_data_new, 0, sizeof(puf_binary_new));
//     uint8_t result;

//     // read
//     int index = 0, i = 0;

//     string name = "r";
//     name += to_string(j);
//     name += ".txt";
//     string a, b;
//     long thisItem;
//     ifstream myFile(name);
//     if (myFile) {
//         while (myFile) {
//             getline(myFile, a);
//             b = convertString(a);
//             if (isValidNumber(b)) {
//             thisItem = b.toInt();
//             helper_data_new[i] = thisItem;
//             i++;
//             }
//         }
//         } else {
//         Serial.println("error ");
//     }
// }

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

void print_key(uint8_t* key, uint8_t length) {
  for (int i = 0; i < length; i++) {
    cout<<"0123456789abcdef"[key[i] >> 4];
    cout<<"0123456789abcdef"[key[i] & 0xf];
  }
  cout<<endl;
}

void print_array(uint8_t* arr,int length){
    for (int i = 0; i < length; i++){
        uint8_t a = arr[i];
        uint8_t b = a & 0xF0;
        uint8_t c = a << 4;
        cout<<hex<<a<<hex<<b;      
    }
}

 using namespace std;

int main()
{
    int no_of_keys = 10;
    for( int i = 0; i < no_of_keys; i++ )
    {
        get_response(i);
        //cout<<"PUF_BINARY_NEW:"<<endl;
        print_array(puf_binary_new,296);
        
        memset(key_256, 0, 32 * sizeof(uint8_t));
        memcpy(&key_256, &puf_binary_new, 32 * sizeof(uint8_t));
        
        tools.gen_key_per_row(key_256, key_per_row);
        //cout<<"KEY_PER_ROW:"<<endl;
        print_array(key_per_row,37);
       
        gen_helper_data(i);
        //cout<<"HELPER_DATA_NEW:"<<endl;
        print_array(helper_data_new,259);

        //For Generating Final 256 bit Key
        uint8_t key_32[32]; 
        memset(key_32, 0, sizeof(key_32));

        /**
            START DECODING - USE THE ERROR CORRECTION - TO CREATE THE PUF KEY
        */
        //Problem is here
        decode(key_32);
        cout<<endl<<"PUF key \t: ";
        print_array(key_32,32);
        //print_key(key_32, 32);
    }

}
