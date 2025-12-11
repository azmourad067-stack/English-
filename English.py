import streamlit as st
import requests
import json
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
import io
import base64

# Configuration de la page
st.set_page_config(
    page_title="English Conversation Practice",
    page_icon="🗣️",
    layout="wide"
)

# Initialisation de la session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "corrections" not in st.session_state:
    st.session_state.corrections = []
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0
if "audio_processed" not in st.session_state:
    st.session_state.audio_processed = False

# Titre et description
st.title("🗣️ English Conversation Practice")
st.markdown("### Pratiquez votre anglais avec une conversation naturelle - 100% GRATUIT")

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    # Choix du service gratuit
    service = st.radio(
        "Service d'IA (gratuit)",
        ["Groq (Recommandé)", "Hugging Face"],
        help="Groq est plus rapide et performant"
    )
    
    # Clé API selon le service
    if service == "Groq (Recommandé)":
        st.info("🎉 Groq offre une API gratuite avec 14,400 requêtes/jour !")
        api_key = st.text_input(
            "Clé API Groq (gratuite)",
            type="password",
            help="Obtenez votre clé sur console.groq.com"
        )
        st.markdown("[📝 Obtenir une clé Groq gratuite](https://console.groq.com)")
    else:
        st.info("🤗 Hugging Face offre une API gratuite !")
        api_key = st.text_input(
            "Clé API Hugging Face (gratuite)",
            type="password",
            help="Obtenez votre clé sur huggingface.co"
        )
        st.markdown("[📝 Obtenir une clé HF gratuite](https://huggingface.co/settings/tokens)")
    
    # Niveau d'anglais
    level = st.selectbox(
        "Votre niveau d'anglais",
        ["Débutant (A1-A2)", "Intermédiaire (B1-B2)", "Avancé (C1-C2)"]
    )
    
    # Sujets de conversation
    st.subheader("📚 Sujets suggérés")
    topics = [
        "Daily routines", "Hobbies", "Travel", "Food & Cooking",
        "Movies & TV", "Work & Career", "Family & Friends",
        "Weather", "Technology", "Sports"
    ]
    selected_topic = st.selectbox("Choisir un sujet", ["Libre"] + topics)
    
    # Statistiques
    st.subheader("📊 Statistiques")
    st.metric("Messages envoyés", st.session_state.conversation_count)
    st.metric("Corrections reçues", len(st.session_state.corrections))
    
    # Bouton pour réinitialiser
    if st.button("🔄 Nouvelle conversation"):
        st.session_state.messages = []
        st.session_state.corrections = []
        st.session_state.audio_processed = False
        st.rerun()

# Vérification de la clé API
if not api_key:
    st.warning("⚠️ Veuillez entrer votre clé API gratuite dans la barre latérale pour commencer.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("### 🚀 Option 1: Groq (Recommandé)")
        st.markdown("""
        **Avantages:**
        - ✅ Très rapide
        - ✅ 14,400 requêtes/jour GRATUITES
        - ✅ Meilleure qualité de réponse
        - ✅ Facile à configurer
        
        **Comment faire:**
        1. Allez sur [console.groq.com](https://console.groq.com)
        2. Créez un compte gratuit
        3. Allez dans "API Keys"
        4. Créez une nouvelle clé
        5. Copiez-la dans la barre latérale
        """)
    
    with col2:
        st.info("### 🤗 Option 2: Hugging Face")
        st.markdown("""
        **Avantages:**
        - ✅ Totalement gratuit
        - ✅ Pas de limite stricte
        - ✅ Beaucoup de modèles disponibles
        
        **Comment faire:**
        1. Allez sur [huggingface.co](https://huggingface.co)
        2. Créez un compte gratuit
        3. Allez dans Settings > Access Tokens
        4. Créez un nouveau token
        5. Copiez-le dans la barre latérale
        """)
    
    st.stop()

# Système de prompt pour l'IA
def get_system_prompt(level, topic):
    level_instructions = {
        "Débutant (A1-A2)": "Use simple vocabulary and short sentences. Speak slowly and clearly.",
        "Intermédiaire (B1-B2)": "Use everyday vocabulary with some idioms. Encourage natural conversation.",
        "Avancé (C1-C2)": "Use advanced vocabulary and complex structures. Challenge the learner."
    }
    
    topic_instruction = f" Focus the conversation on {topic}." if topic != "Libre" else ""
    
    return f"""You are a friendly English conversation partner helping a French speaker practice English.

Level: {level}
Instructions: {level_instructions[level]}{topic_instruction}

Your role:
1. Have natural, friendly conversations like a friend would
2. Ask follow-up questions to keep the conversation flowing
3. If the user makes grammatical errors, gently correct them by:
   - First responding naturally to their message
   - Then adding a helpful note like "💡 Petite correction: instead of 'I go yesterday', say 'I went yesterday'"
4. Encourage the user and be supportive
5. Keep responses concise (2-4 sentences typically)
6. Use casual, friendly language
7. Show interest in what they say

Remember: You're a conversation partner, not a strict teacher. Make it fun and natural!"""

# Fonction pour transcrire l'audio avec Groq Whisper
def transcribe_audio_groq(audio_bytes, api_key):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    files = {
        "file": ("audio.wav", audio_bytes, "audio/wav"),
        "model": (None, "whisper-large-v3"),
        "language": (None, "en")
    }
    
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()["text"]

# Fonction pour appeler l'API Groq
def call_groq_api(messages, api_key, system_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(messages)
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": api_messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Fonction pour appeler l'API Hugging Face
def call_huggingface_api(messages, api_key, system_prompt):
    url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    full_prompt = system_prompt + "\n\n"
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"{role}: {msg['content']}\n"
    full_prompt += "Assistant:"
    
    data = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "")
    return ""

# Fonction pour analyser les corrections
def extract_corrections(response_text):
    if "💡" in response_text or "correction" in response_text.lower():
        lines = response_text.split("\n")
        for line in lines:
            if "💡" in line or "correction" in line.lower():
                return line.strip()
    return None

# Fonction pour traiter un message (texte ou audio)
def process_message(user_input):
    if not user_input or user_input.strip() == "":
        return
    
    # Ajouter le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_count += 1
    
    # Préparer les messages pour l'API
    api_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]
    
    # Obtenir la réponse de l'IA
    try:
        system_prompt = get_system_prompt(level, selected_topic)
        
        if service == "Groq (Recommandé)":
            assistant_message = call_groq_api(api_messages, api_key, system_prompt)
        else:
            assistant_message = call_huggingface_api(api_messages, api_key, system_prompt)
        
        # Sauvegarder la réponse
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Extraire et sauvegarder les corrections
        correction = extract_corrections(assistant_message)
        if correction:
            st.session_state.corrections.append({
                "timestamp": datetime.now().strftime("%H:%M"),
                "user_message": user_input,
                "correction": correction
            })
        
        return True
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("❌ Clé API invalide. Vérifiez votre clé dans la barre latérale.")
        elif e.response.status_code == 429:
            st.error("⏳ Limite de taux atteinte. Attendez quelques secondes et réessayez.")
        else:
            st.error(f"❌ Erreur API: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return False

# Zone de conversation
st.subheader("💬 Conversation")

# Afficher l'historique des messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Section d'entrée avec micro et texte
col1, col2 = st.columns([3, 1])

with col1:
    user_input = st.chat_input("Tapez votre message en anglais...")
    
with col2:
    st.markdown("### 🎤")
    audio = mic_recorder(
        start_prompt="🎤 Parler",
        stop_prompt="⏹️ Stop",
        just_once=True,
        use_container_width=True,
        key='recorder'
    )

# Traiter l'entrée texte
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("💭 En train de réfléchir..."):
            if process_message(user_input):
                st.rerun()

# Traiter l'entrée audio
if audio and not st.session_state.audio_processed:
    with st.spinner("🎤 Transcription en cours..."):
        try:
            # Convertir l'audio en bytes
            audio_bytes = audio['bytes']
            
            # Transcrire l'audio avec Groq Whisper (gratuit aussi!)
            if service == "Groq (Recommandé)":
                transcription = transcribe_audio_groq(audio_bytes, api_key)
            else:
                st.warning("⚠️ La transcription audio nécessite Groq. Veuillez sélectionner Groq dans les paramètres.")
                transcription = None
            
            if transcription:
                st.session_state.audio_processed = True
                
                with st.chat_message("user"):
                    st.write(f"🎤 {transcription}")
                
                with st.chat_message("assistant"):
                    with st.spinner("💭 En train de réfléchir..."):
                        if process_message(transcription):
                            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erreur de transcription: {str(e)}")

# Réinitialiser le flag audio après traitement
if st.session_state.audio_processed:
    st.session_state.audio_processed = False

# Afficher les corrections récentes dans un expander
if st.session_state.corrections:
    with st.expander("📝 Corrections récentes"):
        for corr in reversed(st.session_state.corrections[-5:]):
            st.markdown(f"**[{corr['timestamp']}]** Vous: _{corr['user_message']}_")
            st.markdown(f"{corr['correction']}")
            st.divider()

# Section d'aide en bas
with st.expander("ℹ️ Comment utiliser cette application"):
    st.markdown("""
    **Conseils pour bien pratiquer:**
    
    1. **Soyez naturel**: Écrivez ou parlez comme vous le feriez normalement
    2. **Ne vous inquiétez pas des erreurs**: C'est en faisant des erreurs qu'on apprend !
    3. **Utilisez les sujets suggérés**: Ils vous aident à démarrer une conversation
    4. **Relisez les corrections**: Elles sont sauvegardées dans la section "Corrections récentes"
    5. **Pratiquez régulièrement**: 10-15 minutes par jour font une grande différence
    
    **Fonctionnalités:**
    - ✅ Conversations naturelles en anglais
    - ✅ 🎤 Reconnaissance vocale (parlez en anglais!)
    - ✅ Corrections grammaticales douces
    - ✅ Questions pour maintenir la conversation
    - ✅ Adaptation à votre niveau
    - ✅ Sujets variés du quotidien
    - ✅ 100% GRATUIT (Groq ou Hugging Face)
    
    **Utiliser le micro:**
    - Cliquez sur "🎤 Parler" pour commencer l'enregistrement
    - Parlez en anglais
    - Cliquez sur "⏹️ Stop" pour terminer
    - Votre parole sera transcrite et analysée automatiquement!
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "💡 Application 100% gratuite - Propulsée par Groq/Hugging Face 🚀<br>"
    "🎤 Reconnaissance vocale incluse avec Groq Whisper (gratuit)"
    "</div>",
    unsafe_allow_html=True
)
