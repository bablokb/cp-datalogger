LoRa
====

Introduction
------------


LoRa Quality-of-Service Configuration
-------------------------------------



  * LORA_SF, LORA_CR, LORA_BW, LORA_QOS = 0...x
    siehe: https://www.rfwireless-world.com/calculators/lora-data-rate-calculator
           (verwendet CR1-4 statt 5-8)

    Zeit für 80 Bytes:

    0: SF7,CR5,BW125k   5469 bps  (684 B/s: 0.12s)
    1: SF7,CR7,BW125k   3906 bps  (488 B/s: 0.17s)
    2: SF8,CR7,BW125k   2232 bps  (279 B/s: 0.29s)
    3: SF9,CR7,BW125k   1256 bps  (157 B/s: 0.51s)
    4: SF10,CR5,BW125k   977 bps  (122 B/s: 0.66s)
    5: SF11,CR5,BW125k   537 bps  ( 67 B/s: 1.20s)
    6: SF11,CR8,BW125k   336 bps  ( 42 B/s: 1.91s)
    7: SF12,CR6,BW125k   244 bps  ( 30 B/s: 2.67s)

    R(b) = 1000*sf*(4/cr)*bw/2**sf


LoRa-Datalogger-Protocol
------------------------

  * Message-Typen:
    T -> wie bisher
    B -> wie bisher
    S -> single, Antwort mit len(content)
    MS -> Start Multi, keine Antwort
    M -> multi, keine Antwort, Satznummer im Header
    ME -> End Multi: Anzahl Sätze
          Antwort: Anzahl M-Sätze, 
                   Gesamtlänge content bzw. fehlende Sätze?


T,2                                    -> 1765797080
S,2025-12-15T11:02:19,098_2,4.93,18.7  -> 35
B,2025-12-15T11:12:42,098_2,6,2        -> 10,8.0,-70
