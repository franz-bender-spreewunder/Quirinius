# IR Server

Willkommen beim IR Server. Dir wird sich beim Studium dieses Codes eine Welt voller Arduino-Magie offenbaren.

## Der Sensor

Vom Sensor gibt es zwei Varianten. Die unterscheiden sich nur im Blickwinkel. Im folgenden daher immer "der" Sensor...

Der Sensor kommuniziert über I2C. Optimal wären dabei 1 MHz aber es funktionieren auch niedrigere Geschwindigkeiten. Der
Sensor kann Bilder mit bis zu 64 FPS liefern. Die Bilder kommen standardmäßig als Checkerboard interleaved. Die Daten 
des Sensors müssen vorverarbeitet werden. Das macht die MLX90640-Bibliothek. Das ist keine richtige Bibliothek sondern
einfach nur Code, des mitkopiert werden muss. Es handelt sich um eine modifizierte Variante, die Teile der
I2C-Kommunikation anders implementiert. Die Standard-Bibliotheken sind einfach zu lahm sodass der Sensor aus dem Takt
kommen kann. 

## Protokoll

Der Server sendet kontinuierlich Daten. Der Beginn einer Nachricht ist durch die Bytefolge 0x00, 0xFF, 0xFF, 0x00
markiert. Es folgt die Zeit, die für die Aufnahme des Bildes benötigt wurde als 4-Byte-Long. Danach folgt das Bild als 
Folge von 4-Byte-Float werden, wobei der Wert die Temparatur angibt. Das Bild wird von Links Oben nach Rechts Unten 
ausgegeben. Es wird immer ein Vollbild ausgegeben.

*Visualisierung* (Alles Little Endian, Longs und Floats in 32 Bit)

+---------------------+--------------------+------------+
| Preamble            | Frame Delay        | Frame      |
+---------------------+--------------------+------------+
| 0x00 0xFF 0xFF 0x00 | Delay im ms (Long) | 768 Floats |
+---------------------+--------------------+------------+

## Das Bild

Der Sensor liefert ein Bild mit 24 Zeilen und 32 Spalten.

## Bonjour / ZeroConf / mDNS

Der Sensor publisht via Bonjour seine Addresse und den Port.

## Board

Der Code ist für einen ESP32 geschrieben. Es sollte keine Rolle spielen, welche Variante genutzt wird (also vom Spiecher
her).