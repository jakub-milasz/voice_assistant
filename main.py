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
import nltk
# nltk.download('stopwords')


def listen_for_command():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for commands...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        com = r.recognize_google(audio)
        return com
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again")
        return None
    except sr.RequestError:
        print("Unable to access the Google Speech Recognition API")
        return None


def assistant_response(text):
    print(text)
    tts = gTTS(text=text, lang="en")
    tts.save("welcome.mp3")
    sound = AudioSegment.from_mp3("welcome.mp3")
    sound.export("response.wav", format="wav")
    winsound.PlaySound("response.wav", winsound.SND_FILENAME)


def print_tasks(task_list):
    for index, key in enumerate(task_list):
        print(f'{index+1}. {key}')


def bag_processing():
    dataset = pd.read_csv('classified_phrases.csv')
    corpus = []
    for i in range(dataset.shape[0]):
        review = re.sub('[^a-zA-Z]', ' ', dataset['Zwrot'][i])
        review = review.lower()
        review = review.split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        review = [ps.stem(word) for word in review if not word in set(all_stopwords)]
        review = ' '.join(review)
        corpus.append(review)
    cv = CountVectorizer(max_features=1500)
    X = cv.fit_transform(corpus).toarray()
    y = dataset.iloc[:, -1].values
    classifier = GaussianNB()
    classifier.fit(X, y)
    return cv, classifier


def predict_new_command(new_command, cv):
    new_command = re.sub('[^a-zA-Z]', ' ', new_command)
    new_command = new_command.lower()
    new_command = new_command.split()
    ps = PorterStemmer()
    all_stopwords = stopwords.words('english')
    all_stopwords.remove('not')
    new_command = [ps.stem(word) for word in new_command if not word in set(all_stopwords)]
    new_command = ' '.join(new_command)
    new_corpus = [new_command]
    new_X_test = cv.transform(new_corpus).toarray()
    new_y_pred = classifier.predict(new_X_test)
    return new_y_pred


if __name__ == "__main__":
    tasks = []
    thanks_responses = ["You're welcome!", "Always at your service!", "No problem!"]
    cv, classifier = bag_processing()
    while True:
        command = listen_for_command()
        if command:
            num = predict_new_command(command, cv)
            if num == 1:
                assistant_response("Hello, how can I help you?")
            elif num == 2:
                screenshot = ImageGrab.grab()
                screenshot.save("screenshot.png")
                screenshot.close()
                assistant_response("I have taken a screenshot.")
            elif num == 3:
                assistant_response("What task would you like to add?")
                task = listen_for_command()
                if task is not None:
                    tasks.append(task)
                    assistant_response("I have added the task '{}' successfully.".format(task))
            elif num == 4:
                print_tasks(tasks)
                assistant_response("I have printed a list of tasks.")
            elif num == 5:
                assistant_response(thanks_responses[random.randint(0, len(thanks_responses)-1)])
            elif num == 6:
                assistant_response("Goodbye!")
                break
            elif num == 7:
                assistant_response("Which task would you like to remove?")
                task = listen_for_command()
                if task in tasks:
                    tasks.remove(task)
                    assistant_response("I have removed the task '{}' successfully.".format(task))
                else:
                    assistant_response("There is no such task.")
