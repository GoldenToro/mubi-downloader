<img src="https://mubi.com/MUBI-logo.png" alt="Mubi Logo" width="200"/>

## Mubi Downloader

"Mubi Downloader" is a Python script that allows users to download movies from the Mubi streaming service. It uses the Mubi API to extract the video URL and decryption key, and then decrypts it using shaka-packager. <br>
<b>Updated:</b> The program can now be launched from the command line (once the settings have been adjusted).

## Table of Contents
- [Introduction](#Introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Legal Notice](#legal-notice)

## Introduction
Mubi is a streaming service that offers a carefully curated selection of movies from around the world. However, the platform restricts users from downloading the movies to their devices. Fortunately, this script bypasses that restriction and allows users to download movies from MUBI for offline viewing.

## Installation
1. Clone the repository or download the zip file.
2. Install the required libraries using one of the following methods:
    * Run the 'install_requirements.bat'
    * Manually install each library specified in 'requirements.txt'.
    * Run 'pip install -r requirements.txt'
3. Install [shaka-packager](https://github.com/shaka-project/shaka-packager/releases/tag/v2.6.1) and [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE/releases)
4. Copy the .exe files for shaka-packager and N_m3u8DL-RE into the same folder that contains the mubi_downloader.py file.

## Usage

1. Open the `mubi_downloader.py` file in a text editor.
2. Replace all the 'ADDHERE' in the "SETTINGS" at the beginning of the file with the relevant data, which can be obtained by watching your network traffic when streaming a movie from MUBI. Most of these elements can be obtained from a single URL. 
   - For example, to get the movie ID (in the URL) and the Authorization Bearer (in the headers), filter for the word "viewing" in your network traffic manager. 
   - Then, search for "cenc" to get the value for the header "dt-custom-data:". Copy this value and paste it into the corresponding one in the script.
3. Steps 1 & 2 only need to be performed the first time you use the script. For each subsequent movie, only the Movie ID is required.
4. Open your terminal and navigate to the directory containing the `mubi_downloader.py` file. (or add it to PATH)
5. Run the following command in your terminal:

    ```
    python mubi_downloader.py MovieID
    ```
   
   or 

    ```
    python mubi_downloader.py "MovieID1,MovieID2" PATH:\TO\OUTPUT\FOLDER
    ```
   
6. If you entered all the details correctly, your movie will start downloading.

## Legal Notice
- This program is intended solely for educational and informational purposes. The authors and contributors of this program do not condone or encourage any illegal or unethical activities. Any misuse of this program for unlawful or unethical purposes is strictly prohibited.
- Users must agree to use this program only for lawful purposes and in compliance with all applicable laws and regulations. The authors and contributors of this program will not be held responsible for any misuse or illegal activity undertaken by users.
- The use of this program is at the sole discretion of the user. The authors and contributors of this program are not responsible for any damages, direct or indirect, that may occur from using this program. Users agree to indemnify and hold harmless the authors and contributors of this program from any and all claims, damages, and expenses, including attorney's fees, arising from the use of this program.
- This program is provided "as is" without warranty of any kind, either express or implied, including but not limited to the implied warranties of merchantability, fitness for a particular purpose, or non-infringement. The authors and contributors of this program shall not be liable for any damages, including but not limited to direct, indirect, incidental, consequential, or punitive damages arising from the use of this program or any information contained therein.
