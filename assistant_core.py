import speech_recognition as sr
from gtts import gTTS
from PIL import ImageGrab
import winsound
from pydub import AudioSegment
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
import random
import pandas as pd
import re


def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None


def assistant_response(text):
    """Zamienia tekst na mowę i odtwarza"""
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    sound.export("response.wav", format="wav")
    winsound.PlaySound("response.wav", winsound.SND_FILENAME)


def bag_processing():
    dataset = pd.read_csv('data/classified_phrases.csv')
    corpus = []
    for i in range(dataset.shape[0]):
        review = re.sub('[^a-zA-Z]', ' ', dataset['Zwrot'][i]).lower().split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        if 'not' in all_stopwords:
            all_stopwords.remove('not')
        review = [ps.stem(w) for w in review if w not in set(all_stopwords)]
        corpus.append(' '.join(review))

    cv = CountVectorizer(max_features=1500)
    X = cv.fit_transform(corpus).toarray()
    y = dataset.iloc[:, -1].values
    classifier = GaussianNB()
    classifier.fit(X, y)
    return cv, classifier


def predict_new_command(new_command, cv, classifier):
    ps = PorterStemmer()
    all_stopwords = stopwords.words('english')
    if 'not' in all_stopwords:
        all_stopwords.remove('not')

    new_command = re.sub('[^a-zA-Z]', ' ', new_command).lower().split()
    new_command = [ps.stem(w) for w in new_command if w not in set(all_stopwords)]
    new_command = [' '.join(new_command)]
    new_X = cv.transform(new_command).toarray()
    return classifier.predict(new_X)[0]
