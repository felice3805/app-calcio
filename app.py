# ==========================================================
#  LE MIE PRESTAZIONI - Tracker calcio amatoriale (versione 1)
#  Scritto in Python con Streamlit.
#  Ogni sezione è commentata per farti capire cosa fa.
# ==========================================================

import streamlit as st      # la libreria che crea l'interfaccia web
import pandas as pd         # ci serve per gestire e calcolare i dati (come una tabella Excel)
import os                   # per controllare se il file dei dati esiste già
from datetime import date   # per gestire la data della partita

# File dove salviamo tutte le partite. È un semplice file di testo (CSV),
# lo stesso formato che apri con Excel. Così i dati non spariscono quando chiudi.
FILE_DATI = "partite.csv"

# Le colonne del nostro archivio: sono i 5 dati che avevamo deciso.
COLONNE = ["Data", "Avversario", "Minuti", "Gol", "Assist", "Voto"]


# ---------- FUNZIONI CHE GESTISCONO I DATI ----------
# Le teniamo separate dall'interfaccia: è più ordinato e più facile da modificare.

def carica_partite():
    """Legge le partite salvate. Se il file non esiste ancora, restituisce una tabella vuota."""
    if os.path.exists(FILE_DATI):
        return pd.read_csv(FILE_DATI)
    return pd.DataFrame(columns=COLONNE)


def salva_partita(nuova_partita):
    """Aggiunge una partita all'archivio e riscrive il file salvato."""
    partite = carica_partite()
    partite = pd.concat([partite, pd.DataFrame([nuova_partita])], ignore_index=True)
    partite.to_csv(FILE_DATI, index=False)
    return partite


def calcola_statistiche(partite):
    """Calcola i numeri riassuntivi dalle partite. Restituisce None se non c'è ancora nulla."""
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


# ---------- INTERFACCIA (quello che vedi sullo schermo) ----------
# Questa parte gira solo quando lanci l'app con "streamlit run app.py".
# Il controllo qui sotto ci permette anche di testare le funzioni qui sopra separatamente.

def main():
    st.set_page_config(page_title="Le mie prestazioni", page_icon="⚽")
    st.title("⚽ Le mie prestazioni")

    # ----- SEZIONE 1: inserimento di una nuova partita -----
    st.header("Aggiungi una partita")

    data_partita = st.date_input("Data", value=date.today())
    avversario = st.text_input("Avversario")
    minuti = st.number_input("Minuti giocati", min_value=0, max_value=120, value=90, step=1)
    gol = st.number_input("Gol", min_value=0, value=0, step=1)
    assist = st.number_input("Assist", min_value=0, value=0, step=1)
    voto = st.slider("Come ti sei sentito in campo (1-10)", min_value=1, max_value=10, value=6)

    # Quando premi il bottone, salviamo la partita.
    if st.button("Salva partita"):
        if avversario.strip() == "":
            st.warning("Scrivi il nome dell'avversario prima di salvare.")
        else:
            nuova = {
                "Data": data_partita.strftime("%Y-%m-%d"),
                "Avversario": avversario,
                "Minuti": minuti,
                "Gol": gol,
                "Assist": assist,
                "Voto": voto,
            }
            salva_partita(nuova)
            st.success("Partita salvata! 🎉")

    # ----- SEZIONE 2: statistiche e storico -----
    partite = carica_partite()
    stats = calcola_statistiche(partite)

    if stats is None:
        st.info("Non hai ancora inserito nessuna partita. Comincia da qui sopra! 👆")
    else:
        st.header("Le tue statistiche")
        # st.metric mostra un numero grande con l'etichetta. Le colonne li mettono in fila.
        c1, c2, c3 = st.columns(3)
        c1.metric("Partite giocate", stats["partite_totali"])
        c2.metric("Gol totali", stats["gol_totali"])
        c3.metric("Assist totali", stats["assist_totali"])

        c4, c5, c6 = st.columns(3)
        c4.metric("Media gol", stats["media_gol"])
        c5.metric("Media minuti", stats["media_minuti"])
        c6.metric("Voto medio", stats["media_voto"])

        # Un grafico dell'andamento del tuo voto partita dopo partita.
        st.header("Andamento del tuo voto")
        st.line_chart(partite.set_index("Data")["Voto"])

        # La lista di tutte le partite, con le più recenti in cima.
        st.header("Storico partite")
        st.dataframe(partite.iloc[::-1], use_container_width=True)


# Questo significa: "esegui main() solo se lanci direttamente questo file".
# Streamlit fa esattamente questo, quindi l'app parte normalmente.
if __name__ == "__main__":
    main()
