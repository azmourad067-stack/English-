
import streamlit as st
import speech_recognition as sr
import pyttsx3
import openai
from gtts import gTTS
import io
import pygame
import tempfile
import os
import threading
import time
from datetime import datetime
import json
import random

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Mon Assistant Anglais 🗣️",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .conversation-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #e3f2fd;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
    
    .correction {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #ff9800;
        font-size: 0.9rem;
    }
    
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
def initialize_session_state():
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = "conversation libre"
    if 'corrections_count' not in st.session_state:
        st.session_state.corrections_count = 0
    if 'words_spoken' not in st.session_state:
        st.session_state.words_spoken = 0
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()

# Sujets de conversation prédéfinis
CONVERSATION_TOPICS = {
    "daily_routine": {
        "name": "Routine quotidienne",
        "questions": [
            "What time do you usually wake up?",
            "What's your typical morning routine?",
            "How do you like to spend your evenings?",
            "What's your favorite meal of the day?"
        ]
    },
    "hobbies": {
        "name": "Loisirs et passions",
        "questions": [
            "What do you like to do in your free time?",
            "Do you have any creative hobbies?",
            "What's a skill you'd like to learn?",
            "How do you like to relax after work?"
        ]
    },
    "travel": {
        "name": "Voyages",
        "questions": [
            "Where would you like to travel next?",
            "What's the most interesting place you've visited?",
            "Do you prefer beach or mountain vacations?",
            "What's your dream destination?"
        ]
    },
    "food": {
        "name": "Nourriture et cuisine",
        "questions": [
            "What's your favorite cuisine?",
            "Do you enjoy cooking?",
            "What's a dish you'd like to learn to make?",
            "What's your comfort food?"
        ]
    },
    "work_study": {
        "name": "Travail et études",
        "questions": [
            "What do you do for work/study?",
            "What's the most interesting part of your job?",
            "What are your career goals?",
            "How do you stay motivated?"
        ]
    },
    "technology": {
        "name": "Technologie",
        "questions": [
            "How has technology changed your daily life?",
            "What's your favorite app or website?",
            "Do you think AI will change our future?",
            "What tech gadget couldn't you live without?"
        ]
    }
}

class EnglishConversationAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Ajustement du microphone
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def listen_to_speech(self):
        """Écoute et transcrit la parole de l'utilisateur"""
        try:
            with self.microphone as source:
                st.info("🎤 Je vous écoute... Parlez maintenant !")
                # Timeout plus court pour une meilleure expérience utilisateur
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                
            st.info("🔄 Traitement de votre parole...")
            # Utilisation de Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='en-US')
            return text.strip()
            
        except sr.WaitTimeoutError:
            st.error("⏱️ Temps d'écoute dépassé. Veuillez réessayer.")
            return None
        except sr.UnknownValueError:
            st.error("❓ Je n'ai pas pu comprendre votre parole. Pouvez-vous répéter ?")
            return None
        except sr.RequestError as e:
            st.error(f"🚫 Erreur du service de reconnaissance vocale : {e}")
            return None
        except Exception as e:
            st.error(f"❌ Erreur inattendue : {e}")
            return None
    
    def analyze_and_correct_text(self, text):
        """Analyse le texte et propose des corrections"""
        corrections = []
        
        # Corrections de grammaire simples (peut être étendu avec une API plus sophistiquée)
        common_corrections = {
            # Verbe être
            "i am go": "I am going",
            "i go to": "I'm going to",
            "he go": "he goes",
            "she go": "she goes",
            
            # Articles
            "i have car": "I have a car",
            "i like music": "I like music",
            
            # Temps
            "yesterday i go": "yesterday I went",
            "tomorrow i go": "tomorrow I will go",
            
            # Pluriels
            "two book": "two books",
            "many person": "many people",
        }
        
        text_lower = text.lower()
        corrected_text = text
        
        for error, correction in common_corrections.items():
            if error in text_lower:
                corrected_text = text.replace(error, correction)
                corrections.append({
                    "original": error,
                    "corrected": correction,
                    "explanation": f"Correction grammaticale recommandée"
                })
        
        # Vérification de la capitalisation
        if text and not text[0].isupper():
            corrected_text = corrected_text.capitalize()
            corrections.append({
                "original": text[0],
                "corrected": corrected_text[0],
                "explanation": "Les phrases commencent par une majuscule"
            })
        
        return corrected_text, corrections
    
    def generate_response(self, user_input, topic):
        """Génère une réponse conversationnelle"""
        
        # Réponses contextuelles basées sur le sujet
        responses = {
            "daily_routine": [
                "That sounds like a nice routine! How long have you been following this schedule?",
                "Interesting! Do you find this routine helps you stay productive?",
                "That's great! What's your favorite part of your daily routine?"
            ],
            "hobbies": [
                "That's a wonderful hobby! How did you get started with it?",
                "Sounds exciting! What do you enjoy most about it?",
                "That's cool! Have you been doing this for a long time?"
            ],
            "travel": [
                "That sounds amazing! What attracts you most about that place?",
                "Wonderful choice! Have you done any research about it yet?",
                "That would be an incredible experience! What would you want to do there?"
            ],
            "food": [
                "That sounds delicious! Is there a special way you like it prepared?",
                "Yummy! Do you have a favorite restaurant that makes it well?",
                "Great choice! Have you ever tried cooking it yourself?"
            ],
            "work_study": [
                "That sounds interesting! What do you find most challenging about it?",
                "That's great! What skills have you developed recently?",
                "Fascinating! What motivates you in your work/studies?"
            ],
            "technology": [
                "That's a good point! How do you think it will evolve in the future?",
                "Interesting perspective! Do you see any downsides to this technology?",
                "That's true! How has it personally impacted your life?"
            ]
        }
        
        # Réponses génériques amicales
        general_responses = [
            "That's really interesting! Can you tell me more about it?",
            "I see! What made you think about that?",
            "That's a great point! How do you feel about it?",
            "Fascinating! What's your experience with that?",
            "That sounds wonderful! What do you like most about it?",
            "I understand! Have you always felt that way?",
            "That's cool! What got you interested in that?",
            "Great! What would you recommend to someone new to this?"
        ]
        
        # Choix de la réponse
        if topic in responses:
            response_list = responses[topic] + general_responses
        else:
            response_list = general_responses
        
        return random.choice(response_list)
    
    def get_topic_question(self, topic_key):
        """Récupère une question aléatoire pour un sujet donné"""
        if topic_key in CONVERSATION_TOPICS:
            return random.choice(CONVERSATION_TOPICS[topic_key]["questions"])
        return "What would you like to talk about today?"

def text_to_speech(text, lang='en'):
    """Convertit le texte en parole"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"Erreur lors de la génération audio : {e}")
        return None

def play_audio(audio_file):
    """Joue un fichier audio"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Attendre que l'audio soit terminé
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Nettoyer
        pygame.mixer.quit()
        os.unlink(audio_file)
    except Exception as e:
        st.error(f"Erreur lors de la lecture audio : {e}")

def main():
    initialize_session_state()
    
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🗣️ Mon Assistant Anglais Personnel</h1>
        <p>Améliorez votre anglais à travers des conversations naturelles !</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar avec les contrôles
    with st.sidebar:
        st.header("🎯 Configuration")
        
        # Sélection du sujet
        selected_topic_key = st.selectbox(
            "Choisissez un sujet de conversation :",
            options=list(CONVERSATION_TOPICS.keys()) + ["free_conversation"],
            format_func=lambda x: CONVERSATION_TOPICS[x]["name"] if x in CONVERSATION_TOPICS else "Conversation libre",
            key="topic_selector"
        )
        
        st.session_state.current_topic = selected_topic_key
        
        st.markdown("---")
        
        # Statistiques de session
        st.subheader("📊 Statistiques")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h3>{}</h3>
                <p>Messages</p>
            </div>
            """.format(len(st.session_state.conversation_history)), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h3>{}</h3>
                <p>Corrections</p>
            </div>
            """.format(st.session_state.corrections_count), unsafe_allow_html=True)
        
        # Temps de session
        session_duration = datetime.now() - st.session_state.session_start
        minutes = int(session_duration.total_seconds() // 60)
        st.info(f"⏱️ Session : {minutes} minutes")
        
        st.markdown("---")
        
        # Contrôles
        if st.button("🔄 Nouvelle conversation", type="secondary"):
            st.session_state.conversation_history = []
            st.session_state.corrections_count = 0
            st.session_state.words_spoken = 0
            st.session_state.session_start = datetime.now()
            st.rerun()
        
        if st.button("💾 Sauvegarder conversation"):
            if st.session_state.conversation_history:
                conversation_data = {
                    "date": datetime.now().isoformat(),
                    "topic": st.session_state.current_topic,
                    "messages": st.session_state.conversation_history,
                    "stats": {
                        "corrections": st.session_state.corrections_count,
                        "words_spoken": st.session_state.words_spoken
                    }
                }
                
                # Créer un fichier de sauvegarde
                filename = f"/mnt/user-data/outputs/conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                os.makedirs("/mnt/user-data/outputs", exist_ok=True)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(conversation_data, f, ensure_ascii=False, indent=2)
                
                st.success(f"✅ Conversation sauvegardée !")
                st.markdown(f"[📥 Télécharger la conversation](computer://{filename})")
    
    # Zone principale de conversation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Conversation")
        
        # Affichage de l'historique de conversation
        if st.session_state.conversation_history:
            for message in st.session_state.conversation_history:
                if message["type"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>Vous :</strong> {message["text"]}
                        <br><small>🕒 {message["timestamp"]}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Afficher les corrections s'il y en a
                    if "corrections" in message and message["corrections"]:
                        for correction in message["corrections"]:
                            st.markdown(f"""
                            <div class="correction">
                                <strong>💡 Correction :</strong> "{correction['original']}" → "{correction['corrected']}"<br>
                                <em>{correction['explanation']}</em>
                            </div>
                            """, unsafe_allow_html=True)
                
                elif message["type"] == "assistant":
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>Assistant :</strong> {message["text"]}
                        <br><small>🕒 {message["timestamp"]}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Message de bienvenue
            welcome_msg = f"""
            <div class="conversation-container">
                <h3>👋 Bienvenue !</h3>
                <p>Je suis votre assistant anglais personnel. Je suis là pour vous aider à pratiquer l'anglais à travers des conversations naturelles.</p>
                
                <p><strong>Sujet actuel :</strong> {CONVERSATION_TOPICS.get(selected_topic_key, {}).get('name', 'Conversation libre')}</p>
                
                <p>🎤 Cliquez sur "Parler" pour commencer une conversation orale<br>
                ✍️ Ou utilisez la zone de texte ci-dessous pour écrire</p>
            </div>
            """
            st.markdown(welcome_msg, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎮 Contrôles")
        
        # Initialiser l'assistant
        if 'assistant' not in st.session_state:
            st.session_state.assistant = EnglishConversationAssistant()
        
        assistant = st.session_state.assistant
        
        # Bouton pour reconnaissance vocale
        if st.button("🎤 Parler", type="primary", use_container_width=True):
            with st.spinner("Écoute en cours..."):
                user_speech = assistant.listen_to_speech()
                
                if user_speech:
                    # Traitement du texte reconnu
                    corrected_text, corrections = assistant.analyze_and_correct_text(user_speech)
                    
                    # Ajouter le message de l'utilisateur
                    user_message = {
                        "type": "user",
                        "text": corrected_text,
                        "original": user_speech,
                        "corrections": corrections,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.conversation_history.append(user_message)
                    
                    # Compter les corrections
                    if corrections:
                        st.session_state.corrections_count += len(corrections)
                    
                    # Compter les mots
                    st.session_state.words_spoken += len(user_speech.split())
                    
                    # Générer une réponse
                    response_text = assistant.generate_response(corrected_text, selected_topic_key)
                    
                    assistant_message = {
                        "type": "assistant",
                        "text": response_text,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.conversation_history.append(assistant_message)
                    
                    # Générer et jouer l'audio de la réponse
                    audio_file = text_to_speech(response_text)
                    if audio_file:
                        threading.Thread(target=play_audio, args=(audio_file,)).start()
                    
                    st.rerun()
        
        st.markdown("---")
        
        # Zone de texte pour la saisie manuelle
        st.subheader("✍️ Écrire")
        user_input = st.text_area("Tapez votre message ici :", height=100, key="text_input")
        
        if st.button("📤 Envoyer", use_container_width=True):
            if user_input.strip():
                # Traitement du texte saisi
                corrected_text, corrections = assistant.analyze_and_correct_text(user_input)
                
                # Ajouter le message de l'utilisateur
                user_message = {
                    "type": "user",
                    "text": corrected_text,
                    "original": user_input,
                    "corrections": corrections,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.conversation_history.append(user_message)
                
                # Compter les corrections
                if corrections:
                    st.session_state.corrections_count += len(corrections)
                
                # Générer une réponse
                response_text = assistant.generate_response(corrected_text, selected_topic_key)
                
                assistant_message = {
                    "type": "assistant",
                    "text": response_text,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.conversation_history.append(assistant_message)
                
                # Nettoyer le champ de texte et rafraîchir
                st.session_state.text_input = ""
                st.rerun()
        
        st.markdown("---")
        
        # Suggestion de question
        if st.button("💡 Poser une question", use_container_width=True):
            question = assistant.get_topic_question(selected_topic_key)
            
            assistant_message = {
                "type": "assistant", 
                "text": question,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.conversation_history.append(assistant_message)
            
            # Générer l'audio pour la question
            audio_file = text_to_speech(question)
            if audio_file:
                threading.Thread(target=play_audio, args=(audio_file,)).start()
            
            st.rerun()

if __name__ == "__main__":
    main()
