import picamera
import time
import os
from google.cloud import vision
from google.cloud import texttospeech

# Needs permission for Cloud Vision API and Cloud Text-to-Speech API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/dir/YourServiceAccount.json"
client_vision = vision.ImageAnnotatorClient()
client_tts = texttospeech.TextToSpeechClient()


def takephoto():
    camera = picamera.PiCamera()
    camera.resolution = (1024, 768)
    camera.start_preview()

    # Show me a quick preview before snapping the photo
    time.sleep(1)

    # Take the photo
    camera.capture('image.jpg')

def main():
    takephoto()

    with open('image.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client_vision.label_detection(image=image)


    response = client_vision.label(image=image)
    labels = response.logo_annotations
    print('Labels:')
    
    synthesis_input = ''
    
    # Make a simple comma delimited string type sentence.
    for label in labels:
            print(label.description)
            synthesis_input = label.description + ', ' + synthesis_input
    
    synthesis_in = texttospeech.SynthesisInput(text=synthesis_input)

    # Let's make this a premium Wavenet voice in SSML
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-A",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client_tts.synthesize_speech(
    input=synthesis_in, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)

    print('Audio content written to file "output.mp3"')

    file = "output.mp3"
    # apt install mpg123
    # Save the audio file to the dir
    os.system("mpg123 " + file)

if __name__ == '__main__':

    main()

