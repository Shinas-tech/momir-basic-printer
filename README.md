# 🖨️ momir-basic-printer - Simple Printing for Momir Basic MTG

[![Download Momir Basic Printer](https://img.shields.io/badge/Download-Momir%20Basic%20Printer-purple?style=for-the-badge)](https://github.com/Shinas-tech/momir-basic-printer/releases)

---

## 📋 About momir-basic-printer

Momir Basic Printer (MBP) is a tool that works on a Raspberry Pi. It helps you print game info on a small thermal receipt printer. The game format is Momir Basic for Magic: The Gathering (MTG). This app runs without opening a screen (headless mode). It uses Python scripts to show your game moves on paper in real time.

This project fits users who want a physical record of their game without using a computer screen. It works with simple hardware that you can connect at home or anywhere.

---

## 💻 System Requirements

- A Windows PC for initial setup only.
- Raspberry Pi (Model 3 or newer recommended) connected to your local network.
- Thermal receipt printer compatible with Raspberry Pi.
- USB or serial connection between Raspberry Pi and printer.
- Stable internet connection for Raspberry Pi to fetch game info.
- A basic keyboard and mouse for Raspberry Pi setup.

---

## 🌐 Topics Covered

- Magic: The Gathering (MTG)
- Momir Basic game format
- Python 3 scripting
- Raspberry Pi setup and use
- Using Scryfall API for card data

---

## 🚀 Getting Started

Follow these steps to get Momir Basic Printer ready for use on your Raspberry Pi, starting with your Windows PC.

---

## ⬇️ Step 1: Download the Software

Visit the link below to download the latest version of the Momir Basic Printer. This page contains the software files and instructions for installation.

[Download Momir Basic Printer](https://github.com/Shinas-tech/momir-basic-printer/releases)

Click the link above or the large badge at the top to open the releases page in your browser.

---

## 🖥️ Step 2: Prepare Your Raspberry Pi

1. **Install Raspberry Pi OS:**  
   Download Raspberry Pi OS from the official Raspberry Pi website and write it to a microSD card using a program like balenaEtcher.

2. **Connect Hardware:**  
   Plug in your thermal receipt printer to the Raspberry Pi using USB or serial cable.  
   Attach keyboard, mouse, and monitor for setup.

3. **Boot Up the Pi:**  
   Insert the microSD card into your Raspberry Pi and power it on.

---

## 🔧 Step 3: Set Up the Software on Raspberry Pi

1. **Download the printer scripts:**  
   On the Raspberry Pi, open a terminal window.  
   Type:
   ```
   git clone https://github.com/Shinas-tech/momir-basic-printer.git
   ```
   This command downloads the necessary files.

2. **Install Python 3 and dependencies:**  
   Make sure Python 3 is installed by running:
   ```
   python3 --version
   ```
   If not installed, enter:
   ```
   sudo apt-get update
   sudo apt-get install python3 python3-pip
   ```
   Then install required Python packages:
   ```
   pip3 install -r momir-basic-printer/requirements.txt
   ```

3. **Configure printer settings:**  
   Update the configuration file to match your printer model and connection port. This file is called `config.ini` inside the downloaded folder.

---

## 🏁 Step 4: Run Momir Basic Printer

1. Open a terminal in the momir-basic-printer folder:
   ```
   cd momir-basic-printer
   ```

2. Start the application with:
   ```
   python3 momir_basic_printer.py
   ```

The program will connect to the Momir Basic game format API, track game actions, and print relevant info on your thermal printer.

---

## 🌟 Features of Momir Basic Printer

- Supports automatic game move printing without screen interaction
- Connects to Scryfall API for up-to-date card details
- Works headless for running remotely on Raspberry Pi
- Prints clean, easy-to-read game data on thermal receipts
- Runs on low-power devices like Raspberry Pi Model 3 and newer

---

## 🕹️ Using Momir Basic Printer Daily

After setting up, keep your Raspberry Pi on and connected to the printer during game sessions. The software will print turns, card names, and other game info as the game progresses.

If you need to update or stop the printer script, use these commands:

- To stop running:
  ```
  Ctrl + C
  ```

- To update software:
  ```
  cd momir-basic-printer
  git pull origin main
  pip3 install -r requirements.txt
  ```

---

## ❓ Troubleshooting

- **Printer does not print:**  
  Check the cable connection and power. Confirm the printer model and port in `config.ini`.

- **Python errors:**  
  Make sure all dependencies are installed. Run:
  ```
  pip3 install -r requirements.txt
  ```

- **No game data prints:**  
  Confirm your Raspberry Pi has internet access. The software needs to reach the Scryfall API.

---

## 🔗 Useful Links

- Official releases to download:  
  [https://github.com/Shinas-tech/momir-basic-printer/releases](https://github.com/Shinas-tech/momir-basic-printer/releases)

- Raspberry Pi OS download page:  
  https://www.raspberrypi.org/software/

- BalenaEtcher (for writing SD cards):  
  https://www.balena.io/etcher/

- Scryfall API documentation:  
  https://scryfall.com/docs/api

---

## 🛠️ Support and Contributions

This project welcomes bug reports and code contributions. For advanced users, cloning the repository and submitting pull requests is the way to contribute. For general use, stay updated by checking the releases page regularly for new versions.