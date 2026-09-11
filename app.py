# ==========================================================
#  LE MIE PRESTAZIONI - Tracker calcio amatoriale (versione 2.1)
#  Correzione: passiamo esplicitamente il link del foglio (letto dai secrets)
#  alle funzioni di lettura e scrittura, come richiede la libreria.
# ==========================================================

import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection   # collega Streamlit a Google Sheets

# Nome della scheda (la "linguetta" in basso) dentro il tuo foglio Google.
NOME_FOGLIO = "partite"

# Le colonne del foglio. "Giocatore" è quella che tiene separati i dati delle persone.
COLONNE = ["Giocatore", "Data", "Avversario", "Minuti", "Gol", "Assist", "Voto"]


def get_conn():
    """Crea la connessione al foglio Google (le credenziali stanno nei secrets)."""
    return st.connection("gsheets", type=GSheetsConnection)


def url_foglio():
    """Legge il link del foglio dai secrets, sezione [connections.gsheets] -> spreadsheet."""
    return st.secrets["connections"]["gsheets"]["spreadsheet"]


# ---------- FUNZIONI CHE GESTISCONO I DATI ----------

def carica_tutte():
    """Legge TUTTE le partite dal foglio. Ora passiamo anche spreadsheet=... (il link)."""
    conn = get_conn()
    df = conn.read(spreadsheet=url_foglio(), worksheet=NOME_FOGLIO, ttl=0)
    df = df.dropna(how="all")   # elimina le righe completamente vuote in fondo
    for col in ["Minuti", "Gol", "Assist", "Voto"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def salva_partita(nuova):
    """Aggiunge una partita: legge tutto, aggiunge la riga, riscrive il foglio."""
    conn = get_conn()
    df = carica_tutte()
    df = pd.concat([df, pd.DataFrame([nuova])], ignore_index=True)
    conn.update(spreadsheet=url_foglio(), worksheet=NOME_FOGLIO, data=df)


def calcola_statistiche(partite):
    """Calcola i numeri riassuntivi. Restituisce None se non ci sono partite."""
    if partite.empty:
        return None
    return {
        "partite_totali": len(partite),
        "gol_totali": int(partite["Gol"].sum()),
        "assist_totali": int(partite["Assist"].sum()),
        "media_gol": round(partite["Gol"].mean(), 2),
        "media_minuti": round(partite["Minuti"].mean(), 1),
        "media_voto": round(partite["Voto"].mean(), 1),
    }


# ---------- INTERFACCIA ----------

def main():
    st.set_page_config(page_title="Le mie prestazioni", page_icon="⚽")
    st.title("⚽ Le mie prestazioni")

    nome = st.text_input("Il tuo nome (scrivilo sempre uguale ogni volta!)").strip()
    if nome == "":
        st.info("Scrivi il tuo nome qui sopra per iniziare. 👆")
        st.stop()

    st.caption(f"Stai guardando i dati di: **{nome}**")

    st.header("Aggiungi una partita")
    data_partita = st.date_input("Data", value=date.today())
    avversario = st.text_input("Avversario")
    minuti = st.number_input("Minuti giocati", min_value=0, max_value=120, value=90, step=1)
    gol = st.number_input("Gol", min_value=0, value=0, step=1)
    assist = st.number_input("Assist", min_value=0, value=0, step=1)
    voto = st.slider("Come ti sei sentito in campo (1-10)", 1, 10, 6)

    if st.button("Salva partita"):
        if avversario.strip() == "":
            st.warning("Scrivi il nome dell'avversario prima di salvare.")
        else:
            nuova = {
                "Giocatore": nome,
                "Data": data_partita.strftime("%Y-%m-%d"),
                "Avversario": avversario.strip(),
                "Minuti": minuti,
                "Gol": gol,
                "Assist": assist,
                "Voto": voto,
            }
            salva_partita(nuova)
            st.success("Partita salvata! 🎉")

    tutte = carica_tutte()
    if "Giocatore" in tutte.columns:
        mie = tutte[tutte["Giocatore"] == nome]
    else:
        mie = tutte.iloc[0:0]

    stats = calcola_statistiche(mie)

    if stats is None:
        st.info("Non hai ancora inserito nessuna partita. Comincia da qui sopra!")
    else:
        st.header("Le tue statistiche")
        c1, c2, c3 = st.columns(3)
        c1.metric("Partite giocate", stats["partite_totali"])
        c2.metric("Gol totali", stats["gol_totali"])
        c3.metric("Assist totali", stats["assist_totali"])
        c4, c5, c6 = st.columns(3)
        c4.metric("Media gol", stats["media_gol"])
        c5.metric("Media minuti", stats["media_minuti"])
        c6.metric("Voto medio", stats["media_voto"])

        st.header("Andamento del tuo voto")
        st.line_chart(mie.set_index("Data")["Voto"])

        st.header("Storico partite")
        st.dataframe(mie.iloc[::-1], use_container_width=True)


if __name__ == "__main__":
    main()
