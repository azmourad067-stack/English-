import streamlit as st
import requests
from gtts import gTTS
import io
import base64
import json
import random
from datetime import datetime
import tempfile
import os

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
    
    .audio-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
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
            "What's your favorite meal of the day?",
            "Do you exercise regularly? When?",
            "How do you prepare for work or school?",
            "What's your bedtime routine?",
            "How do you organize your daily tasks?"
        ]
    },
    "hobbies": {
        "name": "Loisirs et passions",
        "questions": [
            "What do you like to do in your free time?",
            "Do you have any creative hobbies?",
            "What's a skill you'd like to learn?",
            "How do you like to relax after work?",
            "Do you play any sports or games?",
            "What books or movies do you enjoy?",
            "Do you like outdoor activities?",
            "Have you ever tried learning a musical instrument?"
        ]
    },
    "travel": {
        "name": "Voyages",
        "questions": [
            "Where would you like to travel next?",
            "What's the most interesting place you've visited?",
            "Do you prefer beach or mountain vacations?",
            "What's your dream destination?",
            "How do you usually plan your trips?",
            "Do you prefer traveling alone or with others?",
            "What's the best travel experience you've had?",
            "Which country's culture interests you most?"
        ]
    },
    "food": {
        "name": "Nourriture et cuisine",
        "questions": [
            "What's your favorite cuisine?",
            "Do you enjoy cooking?",
            "What's a dish you'd like to learn to make?",
            "What's your comfort food?",
            "Do you have any dietary restrictions?",
            "What's the most exotic food you've tried?",
            "Do you prefer eating out or cooking at home?",
            "What's a typical meal in your country?"
        ]
    },
    "work_study": {
        "name": "Travail et études",
        "questions": [
            "What do you do for work/study?",
            "What's the most interesting part of your job?",
            "What are your career goals?",
            "How do you stay motivated?",
            "What skills are important in your field?",
            "Do you enjoy working in a team?",
            "What's challenging about your work?",
            "How do you balance work and personal life?"
        ]
    },
    "technology": {
        "name": "Technologie",
        "questions": [
            "How has technology changed your daily life?",
            "What's your favorite app or website?",
            "Do you think AI will change our future?",
            "What tech gadget couldn't you live without?",
            "How do you stay updated with new technology?",
            "Do you prefer online or offline activities?",
            "What are the pros and cons of social media?",
            "How do you protect your privacy online?"
        ]
    }
}

class EnglishConversationAssistant:
    def __init__(self):
        pass
    
    def analyze_and_correct_text(self, text):
        """Analyse le texte et propose des corrections"""
        corrections = []
        
        # Corrections de grammaire étendues
        common_corrections = {
            # Verbe être et avoir
            "i am go": "I am going",
            "i go to": "I'm going to",
            "he go": "he goes",
            "she go": "she goes",
            "it go": "it goes",
            "we go to": "we're going to",
            "they go to": "they're going to",
            "i have go": "I have to go",
            "he have": "he has",
            "she have": "she has",
            "it have": "it has",
            
            # Articles
            "i have car": "I have a car",
            "i need help": "I need help",
            "i want water": "I want some water",
            "he is teacher": "he is a teacher",
            "she is doctor": "she is a doctor",
            
            # Temps
            "yesterday i go": "yesterday I went",
            "tomorrow i go": "tomorrow I will go",
            "last week i go": "last week I went",
            "next year i go": "next year I will go",
            "i goed": "I went",
            "i eated": "I ate",
            "i drinked": "I drank",
            
            # Pluriels
            "two book": "two books",
            "three car": "three cars",
            "many person": "many people",
            "five year": "five years",
            "several friend": "several friends",
            
            # Prépositions
            "listen music": "listen to music",
            "look the": "look at the",
            "wait bus": "wait for the bus",
            "think about": "think about",
            
            # Contractions et formules courantes
            "i'm go": "I'm going",
            "i'll go": "I'll go",
            "how are you today?": "How are you today?",
            "very good": "very well",
            "i'm fine thank": "I'm fine, thank you",
        }
        
        text_lower = text.lower()
        corrected_text = text
        
        for error, correction in common_corrections.items():
            if error in text_lower:
                # Préserver la casse originale autant que possible
                corrected_text = corrected_text.lower().replace(error, correction)
                corrections.append({
                    "original": error,
                    "corrected": correction,
                    "explanation": "Correction grammaticale recommandée"
                })
        
        # Vérification de la capitalisation
        if corrected_text and not corrected_text[0].isupper():
            corrected_text = corrected_text.capitalize()
            corrections.append({
                "original": "minuscule",
                "corrected": "majuscule",
                "explanation": "Les phrases commencent par une majuscule"
            })
        
        # Vérification de la ponctuation
        if corrected_text and corrected_text[-1] not in '.!?':
            corrected_text += "."
            corrections.append({
                "original": "pas de ponctuation",
                "corrected": "point ajouté",
                "explanation": "Les phrases se terminent par une ponctuation"
            })
        
        return corrected_text, corrections
    
    def generate_response(self, user_input, topic):
        """Génère une réponse conversationnelle"""
        
        # Analyse de mots-clés pour des réponses plus contextuelles
        user_lower = user_input.lower()
        
        # Réponses spécifiques basées sur des mots-clés
        if any(word in user_lower for word in ['love', 'like', 'enjoy', 'favorite']):
            responses = [
                "That's wonderful! What do you love most about it?",
                "I can tell you're passionate about that! How long have you been interested in it?",
                "That sounds amazing! What got you started with that?",
                "Great choice! Have you always felt that way about it?"
            ]
        elif any(word in user_lower for word in ['difficult', 'hard', 'challenging', 'problem']):
            responses = [
                "That does sound challenging! How are you dealing with it?",
                "I understand that can be tough. What strategies have you tried?",
                "Many people find that difficult too. What's the hardest part for you?",
                "That's a common challenge. Have you found any solutions that help?"
            ]
        elif any(word in user_lower for word in ['want', 'hope', 'dream', 'wish']):
            responses = [
                "That's a great goal! What steps are you taking to achieve it?",
                "That sounds exciting! When do you hope to make that happen?",
                "I love that ambition! What's motivating you towards that goal?",
                "That would be incredible! What's your plan to get there?"
            ]
        else:
            # Réponses génériques par sujet
            topic_responses = {
                "daily_routine": [
                    "That sounds like a good routine! How long have you been following this schedule?",
                    "Interesting! Do you find this routine helps you stay productive?",
                    "That's great! What's your favorite part of your daily routine?",
                    "How does that routine make you feel throughout the day?"
                ],
                "hobbies": [
                    "That's a wonderful hobby! How did you get started with it?",
                    "Sounds exciting! What do you enjoy most about it?",
                    "That's cool! Have you been doing this for a long time?",
                    "What would you recommend to someone starting that hobby?"
                ],
                "travel": [
                    "That sounds amazing! What attracts you most about that place?",
                    "Wonderful choice! Have you done any research about it yet?",
                    "That would be an incredible experience! What would you want to do there?",
                    "How do you usually choose your travel destinations?"
                ],
                "food": [
                    "That sounds delicious! Is there a special way you like it prepared?",
                    "Yummy! Do you have a favorite restaurant that makes it well?",
                    "Great choice! Have you ever tried cooking it yourself?",
                    "What makes that dish special to you?"
                ],
                "work_study": [
                    "That sounds interesting! What do you find most challenging about it?",
                    "That's great! What skills have you developed recently?",
                    "Fascinating! What motivates you in your work/studies?",
                    "How did you get started in that field?"
                ],
                "technology": [
                    "That's a good point! How do you think it will evolve in the future?",
                    "Interesting perspective! Do you see any downsides to this technology?",
                    "That's true! How has it personally impacted your life?",
                    "What do you think is the most important tech development recently?"
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
                "Great! What advice would you give to others about this?"
            ]
            
            # Choix de la réponse
            if topic in topic_responses:
                responses = topic_responses[topic] + general_responses
            else:
                responses = general_responses
        
        return random.choice(responses)
    
    def get_topic_question(self, topic_key):
        """Récupère une question aléatoire pour un sujet donné"""
        if topic_key in CONVERSATION_TOPICS:
            return random.choice(CONVERSATION_TOPICS[topic_key]["questions"])
        return "What would you like to talk about today?"

def text_to_speech_cloud(text, lang='en'):
    """Version cloud-compatible de text-to-speech"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Utiliser BytesIO au lieu d'un fichier temporaire
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Encoder en base64 pour l'affichage dans Streamlit
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()
        
        return audio_base64
    except Exception as e:
        st.error(f"Erreur lors de la génération audio : {e}")
        return None

def display_audio_player(audio_base64):
    """Affiche un lecteur audio HTML5"""
    if audio_base64:
        audio_html = f"""
        <div class="audio-container">
            <p>🔊 Réponse audio :</p>
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
                Votre navigateur ne supporte pas l'audio HTML5.
            </audio>
        </div>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# Interface pour l'enregistrement audio (version simplifiée pour le cloud)
def audio_recorder_interface():
    """Interface d'enregistrement audio compatible cloud"""
    st.markdown("""
    <div class="audio-container">
        <h4>🎤 Enregistrement vocal</h4>
        <p>Pour utiliser la reconnaissance vocale sur Streamlit Cloud :</p>
        <ol>
            <li>Utilisez le navigateur Chrome ou Firefox</li>
            <li>Autorisez l'accès au microphone</li>
            <li>Parlez clairement en anglais</li>
        </ol>
        <p><em>Note : La reconnaissance vocale nécessite une extension ou peut être limitée sur Streamlit Cloud.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Alternative : zone de texte avec instructions
    st.info("💡 **Astuce** : Utilisez la zone de texte ci-dessous pour taper vos messages en attendant que la reconnaissance vocale soit configurée.")

def main():
    initialize_session_state()
    
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🗣️ Mon Assistant Anglais Personnel</h1>
        <p>Améliorez votre anglais à travers des conversations naturelles !</p>
        <small>Version optimisée pour Streamlit Cloud</small>
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
            st.markdown(f"""
            <div class="stats-card">
                <h3>{len(st.session_state.conversation_history)}</h3>
                <p>Messages</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <h3>{st.session_state.corrections_count}</h3>
                <p>Corrections</p>
            </div>
            """, unsafe_allow_html=True)
        
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
                
                # Créer un lien de téléchargement
                json_str = json.dumps(conversation_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 Télécharger la conversation",
                    data=json_str,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
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
                    
                    # Afficher le lecteur audio si disponible
                    if "audio" in message and message["audio"]:
                        display_audio_player(message["audio"])
        else:
            # Message de bienvenue
            welcome_msg = f"""
            <div class="conversation-container">
                <h3>👋 Bienvenue !</h3>
                <p>Je suis votre assistant anglais personnel. Je suis là pour vous aider à pratiquer l'anglais à travers des conversations naturelles.</p>
                
                <p><strong>Sujet actuel :</strong> {CONVERSATION_TOPICS.get(selected_topic_key, {}).get('name', 'Conversation libre')}</p>
                
                <p>✍️ Utilisez la zone de texte ci-contre pour commencer une conversation<br>
                🔊 Les réponses audio vous aideront avec la prononciation</p>
                
                <p><strong>💡 Conseil :</strong> Commencez par des phrases simples et n'hésitez pas à faire des erreurs - c'est ainsi qu'on apprend !</p>
            </div>
            """
            st.markdown(welcome_msg, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎮 Contrôles")
        
        # Initialiser l'assistant
        if 'assistant' not in st.session_state:
            st.session_state.assistant = EnglishConversationAssistant()
        
        assistant = st.session_state.assistant
        
        # Interface d'enregistrement audio (informative pour le cloud)
        with st.expander("🎤 Reconnaissance vocale", expanded=False):
            audio_recorder_interface()
        
        st.markdown("---")
        
        # Zone de texte pour la saisie manuelle
        st.subheader("✍️ Écrire votre message")
        user_input = st.text_area("Tapez votre message en anglais ici :", height=100, key="text_input", placeholder="Hello! How are you today?")
        
        col_send, col_question = st.columns(2)
        
        with col_send:
            if st.button("📤 Envoyer", use_container_width=True, type="primary"):
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
                    
                    # Compter les mots
                    st.session_state.words_spoken += len(user_input.split())
                    
                    # Générer une réponse
                    response_text = assistant.generate_response(corrected_text, selected_topic_key)
                    
                    # Générer l'audio de la réponse
                    audio_base64 = text_to_speech_cloud(response_text)
                    
                    assistant_message = {
                        "type": "assistant",
                        "text": response_text,
                        "audio": audio_base64,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.conversation_history.append(assistant_message)
                    
                    # Nettoyer le champ de texte et rafraîchir
                    st.rerun()
        
        with col_question:
            if st.button("💡 Question", use_container_width=True):
                question = assistant.get_topic_question(selected_topic_key)
                
                # Générer l'audio pour la question
                audio_base64 = text_to_speech_cloud(question)
                
                assistant_message = {
                    "type": "assistant", 
                    "text": question,
                    "audio": audio_base64,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.conversation_history.append(assistant_message)
                
                st.rerun()
        
        st.markdown("---")
        
        # Conseils d'utilisation
        st.subheader("💡 Conseils")
        tips = [
            "Utilisez des phrases complètes",
            "N'ayez pas peur de faire des erreurs", 
            "Variez vos sujets de conversation",
            "Écoutez les réponses audio pour la prononciation",
            "Sauvegardez vos conversations pour réviser"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")

    # Footer avec informations
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <p>🗣️ Assistant Anglais Personnel - Version Streamlit Cloud</p>
        <p>Développé pour vous aider à améliorer votre anglais de manière interactive !</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
