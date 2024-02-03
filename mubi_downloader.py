import requests
import json
import os
import sys
import re
import base64
import shutil
from iso639 import Lang

############################################ Settings ###########################################

# add the authorization token here
bearer = 'Bearer ADDHERE'
# add your encoded headers, starts with "ey"
dt_custom_data = 'dt-custom-data: ADDHERE'

###################################################################################################


download_dir = ""
decryption_dir = ""
project = ""
name = ""


def prepareFolders(folder_path):
    global project, download_dir, decryption_dir

    print("Creating Folders in: " + folder_path)
    download_dir = os.path.join(folder_path, project, "download")
    decryption_dir = os.path.join(folder_path, project, "decrypted")
    final_dir = folder_path

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if not os.path.exists(decryption_dir):
        os.makedirs(decryption_dir)
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)


def downloadFiles(filmId):
    global download_dir, project, name
    # Define headers to be sent with the HTTP request
    headers = {
        'authority': 'api.mubi.com',
        'accept': '*/*',
        'accept-language': 'en',
        'authorization': bearer,  # add the authorization token here
        'client': 'web',
        'client-accept-audio-codecs': 'aac',
        'client-accept-video-codecs': 'h265,vp9,h264',
        'client-country': 'US',
        'dnt': '1',
        'origin': 'https://mubi.com',
        'referer': 'https://mubi.com/',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }

    # Make a GET request to the specified URL with the given headers, and load the response JSON into a dictionary
    response = requests.get(f'https://api.mubi.com/v3/films/{filmId}/viewing/secure_url', headers=headers)  # mubi movie ID goes here
    mubi = json.loads(response.text)

    # Extract the video title and secure URL from the response
    name = mubi['mux']['video_title']
    print(name)
    mubi = mubi['url']

    # Retrieve the encryption key from the secure URL using a regular expression
    kid = requests.get(mubi)
    result = re.search(r'cenc:default_KID="(\w{8}-(?:\w{4}-){3}\w{12})">', str(kid.text))

    # Define a function for generating the PSSH box, which contains information about the encryption key
    def get_pssh(keyId):
        array_of_bytes = bytearray(b'\x00\x00\x002pssh\x00\x00\x00\x00')
        array_of_bytes.extend(bytes.fromhex("edef8ba979d64acea3c827dcd51d21ed"))
        array_of_bytes.extend(b'\x00\x00\x00\x12\x12\x10')
        array_of_bytes.extend(bytes.fromhex(keyId.replace("-", "")))
        return base64.b64encode(bytes.fromhex(array_of_bytes.hex()))

    # Extract the encryption key ID from the regular expression match and generate the PSSH box
    kid = result.group(1).replace('-', '')
    assert len(kid) == 32 and not isinstance(kid, bytes), "wrong KID length"
    pssh = format(get_pssh(kid).decode('utf-8'))
    # Set the headers for the request
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://cdrm-project.com',
        'Referer': 'https://cdrm-project.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',  # Set the user agent for the request
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # Set the JSON data for the request
    json_data = {
        'license': 'https://lic.drmtoday.com/license-proxy-widevine/cenc/?specConform=true',
        'headers': dt_custom_data,
        'pssh': f'{pssh}',
        'buildInfo': '',
        'proxy': '',
        'cache': False,
    }

    # Send a POST request with the headers and JSON data to the specified URL
    response = requests.post('https://cdrm-project.com/wv', headers=headers, json=json_data)

    # Search for a decryption key pattern in the response text
    result = re.search(r"[a-z0-9]{16,}:[a-z0-9]{16,}", str(response.text))

    # Get the decryption key and format it properly
    decryption_key = result.group()
    print("decryptionkey: " + decryption_key)
    decryption_key = f'key_id={decryption_key}'
    decryption_key = decryption_key.replace(":", ":key=")
    # Download the video using N_m3u8DL-RE
    os.system(fr'N_m3u8DL-RE "{mubi}" --auto-select --save-name "{project}" --auto-select --save-dir {download_dir} --tmp-dir {os.path.join(download_dir, "temp")}')

    return decryption_key


def decryptFiles(key):
    global project, download_dir, decryption_dir

    # Run shaka-packager to decrypt the video file
    print("Run shaka-packager to decrypt the video file")
    os.system(fr'shaka-packager in="{os.path.join(download_dir, f"{project}.mp4")}",stream=video,output="{os.path.join(decryption_dir, f"{project}.decrypted-video.mp4")}" --enable_raw_key_decryption --keys {key}')
    os.remove(f'{os.path.join(download_dir, f"{project}.mp4")}')

    # Define a regex pattern to match the audio file names
    regex_pattern = re.escape(project) + r"\.[a-z]{2,}\.m4a"
    # Loop through all files in the download_dir directory
    for filename in os.listdir(download_dir):
        if filename.endswith(".srt") and project in filename:
            source_path = os.path.join(download_dir, filename)
            dest_path = os.path.join(decryption_dir, filename)
            shutil.move(source_path, dest_path)
        # If the file name matches the regex pattern
        if re.match(regex_pattern, filename):
            # Extract the language code from the file name
            letters = re.search(re.escape(project) + r"\.([a-zA-Z]{2,})\.m4a", filename).group(1)
            # Run shaka-packager to decrypt the audio file
            print("Run shaka-packager to decrypt the audio file")
            os.system(
                fr'shaka-packager in="{os.path.join(download_dir, f"{project}.{letters}.m4a")}",stream=audio,output="{os.path.join(decryption_dir, f"{project}.decrypted-audio.{letters}.m4a")}" --enable_raw_key_decryption --keys {key}')


def combineFiles(dir):
    global name

    def find_files():
        global decryption_dir

        mp4_file = None
        srt_files = []
        m4a_files = []

        for filename in os.listdir(decryption_dir):

            if filename.endswith('.mp4'):
                mp4_file = os.path.join(decryption_dir, filename)
            elif filename.endswith('.srt'):
                srt_files.append(os.path.join(decryption_dir, filename))
            elif filename.endswith('.m4a'):
                m4a_files.append(os.path.join(decryption_dir, filename))

        return mp4_file, srt_files, m4a_files

    def startFFMPEG(path, mp4_file, srt_files, m4a_files):

        def checkLanguageExceptions(code):

            # Some weird (Sub?)-Languages run in Errors
            # just replace them with their language family#

            # Example: Replace 'Norwegian Bokmål' with 'Norwegian'
            if code == "nb":
                code = "no"

            return code

        def iso_lang_code(original_code):

            original_code = checkLanguageExceptions(original_code)

            language = Lang(original_code)

            return language.pt2t

        def iso_long_code(original_code):

            original_code = checkLanguageExceptions(original_code)

            language = Lang(original_code)

            return language.name

        output_file = os.path.join(path, f"{name}.mp4")

        # add Video
        print("add video")
        ffmpeg_command = f'ffmpeg -i "{mp4_file}" '

        map = "-map 0:v "
        metadata = ""

        i_map = 0
        i_meta = 0
        for m4a_file in m4a_files:
            i_map += 1
            language_code = re.search(r"\.([a-zA-Z]{2})\.[a-zA-Z]*\.?m4a", m4a_file).group(1)
            print(f"add audio: {i_map}:{i_meta} lang: {language_code}:{iso_lang_code(language_code)}:{iso_long_code(language_code)}")
            ffmpeg_command += f'-i "{m4a_file}" '
            map += f"-map {i_map}:a "
            metadata += f'-metadata:s:a:{i_meta} language={iso_lang_code(language_code)} -metadata:s:a:{i_meta} title="{iso_long_code(language_code)}" '
            i_meta += 1

        i_meta = 0
        for srt_file in srt_files:
            i_map += 1
            language_code = re.search(r"\.([a-zA-Z]{2})\.[a-zA-Z]*\.?srt", srt_file).group(1)
            print(f"add subtitles: {i_map}:{i_meta} lang: {language_code}:{iso_lang_code(language_code)}:{iso_long_code(language_code)}")
            ffmpeg_command += f'-i "{srt_file}" '
            map += f"-map {i_map}:s "
            metadata += f'-metadata:s:s:{i_meta} language={iso_lang_code(language_code)} -metadata:s:s:{i_meta} handler_name={iso_long_code(language_code)} -metadata:s:s:{i_meta} title="{iso_long_code(language_code)}" '
            i_meta += 1

        ffmpeg_command += map
        ffmpeg_command += metadata

        # add last commands and output file
        ffmpeg_command += (
            '-c:v copy '
            '-c:a aac '
            '-c:s mov_text '
            f'-y "{output_file}"'
        )

        # print("--> Full command:")
        # print(ffmpeg_command)

        print("--> Start Command:")
        os.system(ffmpeg_command)

    def cleanUp(dir):
        global project, download_dir, decryption_dir

        # Clean the mess
        if os.path.exists(download_dir):

            temp = os.path.join(download_dir, "temp")
            if os.path.exists(temp):

                for filename in os.listdir(temp):
                    os.remove(f'{os.path.join(temp, filename)}')

                os.rmdir(temp)

            for filename in os.listdir(download_dir):
                os.remove(f'{os.path.join(download_dir, filename)}')

            os.rmdir(download_dir)

        if os.path.exists(decryption_dir):

            for filename in os.listdir(decryption_dir):
                os.remove(f'{os.path.join(decryption_dir, filename)}')

            os.rmdir(decryption_dir)

        os.rmdir(os.path.join(dir, project))

    mp4_file, srt_files, m4a_files = find_files()

    print("--> Files found:")
    print(mp4_file)
    for file in srt_files:
        print(file)
    for file in m4a_files:
        print(file)

    if mp4_file and m4a_files:

        startFFMPEG(dir, mp4_file, srt_files, m4a_files)

        cleanUp(dir)

        print("Video successfully combined. Can be found under:\n" + dir + "\\" + name)


    else:
        print("Not enough files to create a video file.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mubi_downloader.py FilmId(s) [Optional OutputPath]")
        print("Example: python mubi_downloader.py 1234")
        print('Example: python mubi_downloader.py "1234,0002" C:\\Users\\User1\\Download')
        sys.exit(1)

    project_counter = 0
    filmIds = sys.argv[1].split(',')

    folder_path = os.path.dirname(os.path.abspath(__file__))

    withSound = False

    if len(sys.argv) > 2:
        folder_path = sys.argv[2]

    for filmId in filmIds:
        name = "Not Found"
        try:
            project = str(project_counter)
            prepareFolders(folder_path)
            key = downloadFiles(filmId)
            decryptFiles(key)
            combineFiles(folder_path)
        except Exception as e:
            print(f"Error while Downloading {filmId} ({name}):")
            print(e)

        project_counter += 1
