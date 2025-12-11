import streamlit as st
import anthropic
import os
from datetime import datetime
import json

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

# Titre et description
st.title("🗣️ English Conversation Practice")
st.markdown("### Pratiquez votre anglais avec une conversation naturelle")

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    # Clé API Anthropic
    api_key = st.text_input(
        "Clé API Anthropic",
        type="password",
        help="Entrez votre clé API Anthropic (commençant par sk-ant-)"
    )
    
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
        st.rerun()

# Vérification de la clé API
if not api_key:
    st.warning("⚠️ Veuillez entrer votre clé API Anthropic dans la barre latérale pour commencer.")
    st.info("""
    **Comment obtenir votre clé API:**
    1. Allez sur [console.anthropic.com](https://console.anthropic.com)
    2. Créez un compte ou connectez-vous
    3. Générez une clé API dans les paramètres
    4. Copiez-la et collez-la dans le champ à gauche
    """)
    st.stop()

# Initialisation du client Anthropic
client = anthropic.Anthropic(api_key=api_key)

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

# Fonction pour analyser les corrections
def extract_corrections(response_text):
    if "💡" in response_text or "correction" in response_text.lower():
        lines = response_text.split("\n")
        for line in lines:
            if "💡" in line or "correction" in line.lower():
                return line.strip()
    return None

# Zone de conversation
st.subheader("💬 Conversation")

# Afficher l'historique des messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Zone de saisie
user_input = st.chat_input("Tapez votre message en anglais...")

if user_input:
    # Ajouter le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_count += 1
    
    with st.chat_message("user"):
        st.write(user_input)
    
    # Préparer les messages pour l'API
    api_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]
    
    # Obtenir la réponse de Claude
    with st.chat_message("assistant"):
        with st.spinner("💭 En train de réfléchir..."):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    system=get_system_prompt(level, selected_topic),
                    messages=api_messages
                )
                
                assistant_message = response.content[0].text
                st.write(assistant_message)
                
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
                
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

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
    
    1. **Soyez naturel**: Écrivez comme vous parleriez normalement
    2. **Ne vous inquiétez pas des erreurs**: C'est en faisant des erreurs qu'on apprend !
    3. **Utilisez les sujets suggérés**: Ils vous aident à démarrer une conversation
    4. **Relisez les corrections**: Elles sont sauvegardées dans la section "Corrections récentes"
    5. **Pratiquez régulièrement**: 10-15 minutes par jour font une grande différence
    
    **Fonctionnalités:**
    - ✅ Conversations naturelles en anglais
    - ✅ Corrections grammaticales douces
    - ✅ Questions pour maintenir la conversation
    - ✅ Adaptation à votre niveau
    - ✅ Sujets variés du quotidien
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "💡 Astuce: Pour obtenir le meilleur résultat, essayez d'écrire 2-3 phrases par message"
    "</div>",
    unsafe_allow_html=True
)
