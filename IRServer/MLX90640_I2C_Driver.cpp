/**
   @copyright (C) 2017 Melexis N.V.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

*/


#include <Wire.h>
#include<Arduino.h>
#include "MLX90640_I2C_Driver.h"

void MLX90640_I2CInit()
{

}

int MLX90640_I2CRead(uint8_t _deviceAddress, unsigned int startAddress, unsigned int nWordsRead, uint16_t *data)
{
  // nWordsRead must be <= 32767
    Wire.beginTransmission(_deviceAddress);
    Wire.write(startAddress >> 8); //MSB
    Wire.write(startAddress & 0xFF); //LSB
    Wire.endTransmission(false);
    i2c_err_t error = Wire.readTransmission(_deviceAddress, (uint8_t*) data, nWordsRead*2);
    if(error != 0){//problems
        Serial.printf("Block read from sensor(0x%02X) at address=%d of %d uint16_t's failed=%d(%s)\n",
        _deviceAddress,startAddress,nWordsRead,error,Wire.getErrorText(error));
    }
    else { // reverse byte order, sensor Big Endian, ESP32 Little Endian
        for(auto a = 0; a<nWordsRead; a++){
            data[a] = ((data[a] & 0xff)<<8) | (( data[a]>>8)&0xff);
        }
    }
    return 0;
}

//Set I2C Freq, in kHz
//MLX90640_I2CFreqSet(1000) sets frequency to 1MHz
void MLX90640_I2CFreqSet(int freq)
{
  //i2c.frequency(1000 * freq);
  Wire.setClock((long)1000 * freq);
}

//Write two bytes to a two byte address
int MLX90640_I2CWrite(uint8_t _deviceAddress, unsigned int writeAddress, uint16_t data)
{
  Wire.beginTransmission((uint8_t)_deviceAddress);
  Wire.write(writeAddress >> 8); //MSB
  Wire.write(writeAddress & 0xFF); //LSB
  Wire.write(data >> 8); //MSB
  Wire.write(data & 0xFF); //LSB
  if (Wire.endTransmission() != 0)
  {
    //Sensor did not ACK
    Serial.println("Error: Sensor did not ack");
    return (-1);
  }

  uint16_t dataCheck;
  MLX90640_I2CRead(_deviceAddress, writeAddress, 1, &dataCheck);
  if (dataCheck != data)
  {
    //Serial.println("The write request didn't stick");
    return -2;
  }

  return (0); //Success
}
