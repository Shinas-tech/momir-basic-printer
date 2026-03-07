# Momir Basic Printer (MBP)

Momir Basic Printer (MBP) is a set of Python scripts designed to run headless on a Raspberry Pi connected to a thermal receipt printer for playing the [Momir Basic](https://magic.wizards.com/en/formats/momir-basic) MTG format.

> [!NOTE]
> This project is a work in progress and is not yet fully functional. Please check back for updates as I continue to work on this project!

## TODO

- [x] Update Scryfall refresh to only download new cards instead of re-downloading the entire database every time
- [ ] Document configuration in README
- [ ] Enhance CLI for better user experience and error handling
- [ ] Add thermal printer integration
- [ ] Add OLED display integration
- [ ] Add rotary encoder and button input
- [ ] Create pinout diagram

## Table of Contents

- [About](#about)
- [Examples](#examples)
- [Hardware](#hardware)
  - [Components](#components)
  - [Pinout](#pinout)
- [Installation](#installation)
- [Configuration](#configuration)
- [Service Management](#service-management)
- [Momir Basic Rules](#momir-basic-rules)
- [Disclaimer](#disclaimer)

## About

Downloads card data from the [Scryfall API](https://scryfall.com/docs/api), including card art which is dithered to monochrome on-device, and prints a random card within a set CMC value on demand via thermal printer. All settings are configurable via [config.ini](src/config.ini), and the software can run as a background service on any Linux-based SBC with GPIO. The complete hardware setup is designed to be compact and portable, with all components housed in a waterproof case.

## Examples

| Physical Card                                           | Printed Card                                              |
| ------------------------------------------------------- | --------------------------------------------------------- |
| ![Physical Chrome Courier](img/chrome_courier_card.jpg) | ![Printed Chrome Courier](img/chrome_courier_receipt.jpg) |

## Hardware

### Components

- [Raspberry Pi 3 Model B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/)
- [Adafruit T-Cobbler Plus GPIO Breakout](https://a.co/d/0fnKGt3A)
- [Maikrt MC206H Thermal Printer](https://a.co/d/06qIKsng)
- [PAPRMA 57mm x 30mm Thermal Paper](https://a.co/d/04u2Gb2j)
- [MakerFocus 20200330-SD8V OLED Display](https://a.co/d/06Y7V5Uj)
- [KY-040 Rotary Encoder Module](https://a.co/d/0hN4SBto)
- [Nilight 12V 20A SPST Rocker Toggle Switch](https://a.co/d/02VcvtcQ)
- [EG STARTS 24mm Arcade Push Buttons](https://a.co/d/0jlW1BSk)
- [SHNITPWR 60W Universal Power Supply](https://a.co/d/0bKNzwey)
- [LM2596 Buck Converter](https://a.co/d/070NjEDp)
- [KeeYees 4 Channel IIC I2C Logic Level Converter](https://a.co/d/0ecOK7n6)

### Pinout

```mermaid
flowchart TB
  subgraph IO["I/O"]
    direction LR
    subgraph OLEDS["OLED Displays"]
      direction TB
      subgraph OLED_B["OLED Display #2"]
        direction LR
        OLED_B1["SDA"]
        OLED_B2["SCL"]
        OLED_B3["VCC"]
        OLED_B4["GND"]
      end

      subgraph OLED_A["OLED Display #1"]
        direction LR
        OLED_A1["SDA"]
        OLED_A2["SCL"]
        OLED_A3["VCC"]
        OLED_A4["GND"]
      end
    end

    subgraph TP["Thermal Printer"]
      direction LR
      subgraph PP["Power Port"]
        direction TB
        PP1["VCC"]
        PP2["GND"]
      end

      subgraph USB["USB"]
        direction TB
        USB1["GND"]
        USB2["D+"]
        USB3["D-"]
        USB4["5V"]
      end

      subgraph TTL["TTL"]
        direction TB
        TTL1["GND"]
        TTL2["RX"]
        TTL3["TX"]
        TTL4["DTR"]
      end
    end
  end

  subgraph PI["Raspberry Pi 3B+ GPIO"]
    direction TB
    subgraph RIGHT["Right Column"]
      direction LR
      P2["2: 5V"]
      P4["4: 5V"]
      P6["6: GND"]
      P8["8: GPIO14/TXD"]
      P10["10: GPIO15/RXD"]
      P12["12: GPIO18"]
      P14["14: GND"]
      P16["16: GPIO23"]
      P18["18: GPIO24"]
      P20["20: GND"]
      P22["22: GPIO25"]
      P24["24: GPIO8"]
      P26["26: GPIO7"]
      P28["28: GPIO1/ID_SC"]
      P30["30: GND"]
      P32["32: GPIO12"]
      P34["34: GND"]
      P36["36: GPIO16"]
      P38["38: GPIO20"]
      P40["40: GPIO21"]
    end

    subgraph LEFT["Left Column"]
      direction LR
      P1["1: 3.3V"]
      P3["3: GPIO2/SDA"]
      P5["5: GPIO3/SCL"]
      P7["7: GPIO4"]
      P9["9: GND"]
      P11["11: GPIO17"]
      P13["13: GPIO27"]
      P15["15: GPIO22"]
      P17["17: 3.3V"]
      P19["19: GPIO10"]
      P21["21: GPIO9"]
      P23["23: GPIO11"]
      P25["25: GND"]
      P27["27: GPIO0/ID_SD"]
      P29["29: GPIO5"]
      P31["31: GPIO6"]
      P33["33: GPIO13"]
      P35["35: GPIO19"]
      P37["37: GPIO26"]
      P39["39: GND"]
    end
  end
```

## Installation

1. Clone this repository and navigate to the project directory.

```shell
git clone https://github.com/MoritzHayden/momir-basic-printer.git
cd momir-basic-printer
```

2. Open [src/config.ini](src/config.ini) in a text editor and update the configuration variables to add your specific settings (like printer connection details, GPIO pins, and other hardware settings) before proceeding.

```shell
nano src/config.ini
```

3. Make the setup script executable and run it. This will automatically install dependencies and configure the systemd background service.

```shell
chmod +x setup.sh
./setup.sh
```

> [!TIP]
> If you are running a minimal setup and explicitly require the service to run as root, you can bypass the safety check by running: `sudo ./setup.sh --allow-root`

## Configuration

All configuration variables are stored in [src/config.ini](src/config.ini). Update the values in this file to match your specific hardware setup and preferences. After making changes to the configuration, restart the service for the changes to take effect.

| **Section**  | **Variable**             | **Type** | **Description** |
| ------------ | ------------------------ | -------- | --------------- |
| `FILESYSTEM` | `cards_path`             | ...      | ...             |
| `FILESYSTEM` | `art_path`               | ...      | ...             |
| `FILESYSTEM` | `default_card_art_path`  | ...      | ...             |
| `FILESYSTEM` | `access_rights`          | ...      | ...             |
| `LOGGING`    | `log_level`              | ...      | ...             |
| `LOGGING`    | `log_format`             | ...      | ...             |
| `PRINTER`    | `paper_width_mm`         | ...      | ...             |
| `PRINTER`    | `paper_width_chars`      | ...      | ...             |
| `PRINTER`    | `card_art_enabled`       | ...      | ...             |
| `PRINTER`    | `qr_code_enabled`        | ...      | ...             |
| `PRINTER`    | `qr_code_size`           | ...      | ...             |
| `PRINTER`    | `dpi`                    | ...      | ...             |
| `PRINTER`    | `vendor_id`              | ...      | ...             |
| `PRINTER`    | `product_id`             | ...      | ...             |
| `SCRYFALL`   | `base_url`               | ...      | ...             |
| `SCRYFALL`   | `bulk_data_endpoint`     | ...      | ...             |
| `SCRYFALL`   | `header_accept`          | ...      | ...             |
| `SCRYFALL`   | `header_user_agent`      | ...      | ...             |
| `SCRYFALL`   | `header_accept_encoding` | ...      | ...             |
| `SCRYFALL`   | `request_delay_seconds`  | ...      | ...             |
| `SCRYFALL`   | `max_retries`            | ...      | ...             |
| `SCRYFALL`   | `art_width_px`           | ...      | ...             |
| `SCRYFALL`   | `excluded_sets`          | ...      | ...             |
| `SCRYFALL`   | `excluded_layouts`       | ...      | ...             |

## Service Management

View live logs and print statements:

```shell
sudo journalctl -u momir-basic-printer.service -f
```

Check the current status of the service:

```shell
sudo systemctl status momir-basic-printer.service
```

Restart the service (required after making code changes):

```shell
sudo systemctl restart momir-basic-printer.service
```

Stop the service:

```shell
sudo systemctl stop momir-basic-printer.service
```

## Momir Basic Rules

- Number of Players: 2
- Starting Life Total: 24
- Game Duration: 10 minutes
- Deck Size: 60+ basic lands

Each turn players discard a basic land to activate Momir Vig's ability and get a random creature from throughout Magic's history!

![Momir Vig, Simic Visionary](img/momir_vig.jpg)

## Disclaimer

Neither this project nor its contributors are associated with Hasbro, Wizards of the Coast, or _Magic: The Gathering_ in any way whatsoever.

<div align="center">
  <p>Copyright &copy; 2026 Hayden Moritz</p>
</div>
