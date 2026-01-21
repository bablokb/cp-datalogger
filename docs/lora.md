LoRa
====

Introduction
------------

This document describes the technical aspects of the LoRa-communication
between the dataloggers and the gateway.


Operation Modes
---------------

There are two types of operation:

  - **normal mode**: The dataloggers send data (usually after readout
    of the sensors), and the gateway acknowledges the receipt by
    sending back the content-length of the received package as a very
    minimal quality check. A more formal checking using CRCs is possible,
    but the integrity of the data is already checked on the transport
    level by hardware.
  - **broadcast mode**: Here the dataloggers sends data continuously,
    and the gateway echos packet-number and technical infos e.g. SNR
    (signal-to-noise ratio) and RSSI (received signal strength
    indicator). This mode is useful for optimizing the physical setup
    of antennas.


Data Protocol
-------------

Currently, the system supports three types of request "message-types":

  - **S**: This type of messages ("Single record") are used during
    normal operation mode.
  - **T**: "Time-request" messages query the current time of the
    gateway. At the
    beginning of the broadcast-mode, the datalogger sends a T-message
    and synchronizes
    it's time with the time of the gateway.
  - **B**: Payloads of type "Broadcast message" are used during
    broadcast-mode.

Requests are always sent from the dataloggers to the gateway. The
gateway will always answer with a response.

The payload of a request is always a string and is converted to bytes
during transfers.  Responses in contrast can be string or bytes. The
maximum length of a message is 252 bytes.


S-Message Format
----------------

The format of a S-message is:

    S,<csv-record>

The format of the response is a single byte with the length of the
csv-record:

    len(<csv-record>).to_bytes(1,'little')


T-Message Format
----------------

The format of a T-message is:

    T

The format of the response are four bytes with the current time of the
gateway:

    struct.pack("i",time.time())


B-Message Format
----------------

The format of a B-message is:

    B,<hex-coded timestamp>,<logger-id>,<package-nr>

The format of the response is:

    <package-nr>,<snr>,<rssi>

During broadcast mode, the datalogger increments the package-nr for
every message sent.  The SNR and RSSI are the values measured at the
gateway.


LoRa Quality-of-Service Configuration
-------------------------------------

LoRa supports a number of parameters to tune the physical
communication:

  - **spreading factor**: The SF is between 7 and 12. The higher the
    SF, the lower the data-transmission rate is. The value is
    logarithmic, so a spreading factor increase of one cuts the
    transmission rate by about a factor of 2 (see below for the exact
    formula).
  - **bandwidth**: The data-rate is linear in bandwidth. For technical
    reasons, the bandwidth is fixed at 125K.
  - **coding-rate**: The coding-rate is the amount of error-correction
    bits used for four bits of data. Coding rates range from 5 to 8,
    i.e. four bits and one to four correction-bits.

The application bit-rate is calculated as:

    bit-rate = SF*(4/CR)*BW/2**SF

The datalogger-software uses eight predefined combinations of SF/CR/BW
(configuration variable `LORA_QOS`). The following table lists the
settings, the bitrate, byte-rate and the theoretical transmission time
for 80 bytes:

| QOS| Settings        | Bit-rate | Byte-rate |  t/80 |
|----|-----------------|----------|-----------|-------|
|   0| SF7, CR5,BW125k | 5469 bps |   684 B/s | 0.12s |
|   1| SF7, CR7,BW125k | 3906 bps |   488 B/s | 0.17s |
|   2| SF8, CR7,BW125k | 2232 bps |   279 B/s | 0.29s |
|   3| SF9, CR7,BW125k | 1256 bps |   157 B/s | 0.51s |
|   4| SF10,CR5,BW125k |  977 bps |   122 B/s | 0.66s |
|   5| SF11,CR5,BW125k |  537 bps |    67 B/s | 1.20s |
|   6| SF11,CR8,BW125k |  336 bps |    42 B/s | 1.91s |
|   7| SF12,CR6,BW125k |  244 bps |    30 B/s | 2.67s |

The default value for `LORA_QOS` is `2`.


Measuring Signal Quality
------------------------

When in broadcast-mode, the system returns two values: "SNR" and
"RSSI" that describe signal quality.

"SNR" is the "Signal to Noise Ratio" and is the difference of the
signal compared to the background noise on a logarithmic scale. A SNR
above zero means that the signal is stronger than the noise. If the
signal is weaker than the noise, the signal is below the "noise floor"
and the SNR is below zero.

LoRa can demodulate signals below the noise floor:

| SNR    | Quality
|--------|------------------
| +10 dB | Excellent
|   0 dB | Just OK
| -10 dB | Weak and noisy
| -20 dB | Likely corrupted


"RSSI" in contrast is the "Receive Signal Strengh Indicator" and
measures the strength of the incoming signal. The RSSI-values are
always smaller than zero. Higher values (i.e. nearer to zero) are
better:


| RSSI    | Quality
|---------|-----------------
| -30 dBm | Extremely strong
| -70 dBm | Good
| -90 dBm | Fair
|-120 dBm | Very weak
|-127 dBm | Barely detectable

In a lab-environment, a SNR of about 6.5dB and a RSSI of -65dBm is
typical. For practical setups, SNR and RSSI depend on many factors,
mainly on distance and a clear line-of-sight.


LoRaWAN Regional Parameters
---------------------------

Although the dataloggers don't use the LoRaWAN stack, the regional
parameters (especially available ISM bands) are of interest.

The most current version is available from
<https://resources.lora-alliance.org/technical-specifications>. The
current version as of this writing is
[RP002-1.0.5](https://resources.lora-alliance.org/technical-specifications/rp002-1-0-5-lorawan-regional-parameters).

