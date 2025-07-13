import streamlit as st
import numpy as np
import random
from itertools import combinations


st.set_page_config(
    page_title="Schatzsuche für Gangster",
    page_icon="🪙",
    layout="centered",
    initial_sidebar_state="expanded"
)



st.title("Schatzsuche für Gangster")



st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Caveat&display=swap" rel="stylesheet">
    <style>
    .handfont {
        font-family: 'Caveat', cursive;
        font-size: 28px;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

s=2**3-3
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Courier+Prime&display=swap" rel="stylesheet">
    <style>
    .schreibmaschine {
        font-family: 'Courier Prime', monospace;
        font-size: 20px;
        line-height: 1.2;
    }
    </style>
    <div class="schreibmaschine">
Finde alle Hinweise und entdecke das Geheimnis! Nur... welchen Modus sollst du wählen?

**Gamemaster-Modus:** Du musst ein bestimmtes Geheimnis für eine Aktion finden.

**Singleplayer-Modus:** Du möchtest dich alleine am Rätseln probieren. Für jedes Spiel wird ein neues Geheimnis erstellt!
</div>
""", unsafe_allow_html=True)

if "level_fixiert" not in st.session_state or not st.session_state.level_fixiert:
    level = st.selectbox("🧭 Modus wählen", ["Singleplayer Mini (6x6)", "Gamemaster Mini (6x6)", "Singleplayer Maxi (10x10)", "Gamemaster Maxi (10x10)"])
    if st.button("🚀 Spiel starten"):
        st.session_state.level = level
        st.session_state.level_fixiert = True
        st.rerun()
else:
    st.markdown(f"🧭 Gewählter Modus: **{st.session_state.level}**")


if "level" in st.session_state:
    level = st.session_state.level
    
else:
    st.warning("⚠️ Bitte zuerst einen Modus auswählen und das Spiel starten.")
    st.stop()  # verhindert weitere Ausführung bis Level gewählt wurde




if level == "Singleplayer Mini (6x6)":
    f = 6
    p = 7
    n = 6
    k = 4
    MAX_ZUEGE = 13
elif level == "Gamemaster Mini (6x6)":
    f = 6
    p = 7
    n = 6
    k=4
    MAX_ZUEGE = 13
elif level == "Singleplayer Maxi (10x10)":
    f = 10
    p = 11
    n = 10
    k=7
    MAX_ZUEGE = 40
else: 
    f=10
    p=11
    n=10
    k=7
    MAX_ZUEGE = 40
  


if level.startswith("Singleplayer"):
    if "geheimes_s" not in st.session_state:
        st.session_state.geheimes_s = random.randint(1, p - 1)
else:
     st.session_state.geheimes_s = s



s = st.session_state.geheimes_s

def generiere_funktion(s, k, p):
    
    koeff = [random.randint(1, p - 1)]  # Höchstkoeffizinet nicht 0
    koeff += [random.randint(0, p - 1) for _ in range(k - 2)] #alle anderen Koeffizineten mit Ausnahme des letzen dürfen 0 annehmen
    koeff.append(s) #letzter Koeffizient ist s
    return koeff

def anteile_generieren(s, k, n, p):
    
    koeff = generiere_funktion(s, k, p)
    x_werte = random.sample(range(1, p), n) #0 darf nicht vergeben werden, da f(0)=s
    #random.sample verhindert, dass x-Werte mehr als einmal vorkommen, was zu identischen Wertepaaren führen würde
    
    y_werte = []
    for x in x_werte:
        y = sum([koeff[i] * (x ** (k - 1 - i)) for i in range(k)]) % p
        y_werte.append(y)
    return list(zip(x_werte, y_werte))


anteile = anteile_generieren(s, k, n, p)


def platziere_anteilsfelder(spielfeld, anteile):
    size = len(spielfeld)
    for x, y in anteile:  # x = Spaltenindex (1–10), y = Anzahl Felder
        spalte = x - 1
        freie_zeilen = [r for r in range(size) if spielfeld[r][spalte] == 0]
        if len(freie_zeilen) < y:
            continue  # optional: Fehler/Warnung

        ausgewaehlt = random.sample(freie_zeilen, y)
        for r in ausgewaehlt:
            spielfeld[r][spalte] = 1  # 1 = Anteil-Feld
    
            

# --- Spielfeldfunktionen ---
def erstelle_spielfeld(size=f):
    return np.zeros((size, size), dtype=int)

#DEBUG = st.checkbox("🔍 Zeige Anteil-Felder", value=False)

# --- Grid-Anzeige als HTML-Tabelle ---
def zeige_spielfeld(versuche, wasser_marker, treffer_marker):
    buchstaben = "ABCDEFGHIJ"
    grid_html = "<table style='border-collapse: collapse;'>"
    grid_html += "<tr><th></th>" + "".join([f"<th style='padding: 4px'>{i+1}</th>" for i in range(f)]) + "</tr>"
    for zeile in range(f):
        grid_html += f"<tr><th style='padding: 4px'>{buchstaben[zeile]}</th>"
        for spalte in range(f):
            pos = (zeile, spalte)
            #if DEBUG and  st.session_state.spielfeld[zeile][spalte] == 1:
               # farbe = "#DAA520"
               # symbol = "🗝️"    
            if pos in treffer_marker:
                farbe = "#FFD700"
                symbol = "📌"
            elif pos in wasser_marker:
                farbe = "#DCDCDC"
                symbol = "❌"
            elif pos in versuche:
                farbe = "#ADD8E6"
                symbol = "🔍"
            else:
                farbe = "#ADD8E6"
                symbol = "💡"
            rahmen = "2px solid red" if aktive_felder and pos in aktive_felder else "1px solid #ccc"
            grid_html += f"<td style='width:24px;height:24px;text-align:center;background-color:{farbe};border:{rahmen}'>{symbol}</td>"

        grid_html += "</tr>"
    grid_html += "</table>"
    st.markdown(grid_html, unsafe_allow_html=True)
    
    
    
    
def parse_koordinaten(eingabe, zeilen_map, erlaubte_anzahl=None, label="Eingabe"):
    koordinaten = []
    fehler = None
    gesehen = set()
    
    punkte = [p.strip() for p in eingabe.split(";") if p.strip()]

    for punkt in punkte:
        if len(punkt) < 2:
            fehler = f"⚠️ Ungültige Koordinate '{punkt}' in {label} – zu kurz."
            break
        zeile = punkt[0].upper()
        spalte_str = punkt[1:]
        if zeile not in zeilen_map:
            fehler = f"⚠️ Ungültiger Zeilenbuchstabe '{zeile}' in '{punkt}' ({label})."
            break
        if not spalte_str.isdigit() or not (1 <= int(spalte_str) <= f):
            fehler = f"⚠️ Ungültige Spaltenzahl '{spalte_str}' in '{punkt}' ({label})."
            break
        koord = (zeilen_map[zeile], int(spalte_str) - 1)
        if erlaubte_anzahl == 2 and koord in gesehen:
            fehler = f"⚠️ Koordinate '{punkt}' wurde doppelt eingegeben ({label})."
            break
        gesehen.add(koord)
        koordinaten.append(koord)

    if not fehler and erlaubte_anzahl and len(koordinaten) != erlaubte_anzahl:
        fehler = f"⚠️ Du musst genau {erlaubte_anzahl} unterschiedliche Koordinaten eingeben ({label}) – aktuell: {len(koordinaten)}."

    return koordinaten, fehler    


#------------------------------------------


with st.sidebar:
    st.title("🗝️ Spielregeln")

    st.markdown(f"""
    **Ziel des Spiels:**  
    Finde genügend der versteckten Hinweise, um das Geheimnis zu rekonstruieren.

    **So funktioniert's:**  
    - Du hast **{MAX_ZUEGE} Züge**, um möglichst viele Hinweise zu finden.  
    - Wähle immer **vier Felder**.
    - Du erfährst die **Anzahl der Treffer**, aber **nicht, wo** diese erfolgt sind.  
    - Die Züge und deren Ergebnis werden im **Protokoll** vermerkt:
        - 🔴: 4 Treffer
        - 🟡: 3 Treffer
        - 🟢: 2 Treffer
        - 🔵: 1 Treffer
        - 🟣: 0 Treffer
    - Geprüfte Felder werden mit 🔍 gekennzeichent.
    - Du kannst **eigene Markierungen** setzten, wo du 
        - nichts ❌ oder
        - Treffer 📌 vermutest.
    - Sind alle Züge verbraucht, kannst du versuchen, das Geheimnis zu rekonstruieren.
    """)

    st.markdown("---")
    st.title("🗝️ Rekonstruktion")
    
    st. markdown(f"""
    **So funktioniert's:**             
    - Zähle in jeder **Spalte** die **Anzahl der (vermuteten) Treffer**.
    - Gib dann **Spalte, Trefferanzahl** in das Rekonstruktionsfeld.
        - (Wenn du in Spalte 5 drei Treffer vermutest: **5,3**)  
    - Du brauchst die **korrekte Trefferanzahl** von mindestens **{k}** Spalten, um das Geheimnis rekonstruieren zu können.     
                 
    """)


# --- Session-Setup ---

if "spielfeld" not in st.session_state:
    st.session_state.versuche = []
    st.session_state.zug_nr = 1
    st.session_state.phase = "spiel"
    st.session_state.spielfeld = erstelle_spielfeld(size=f)
    platziere_anteilsfelder(st.session_state.spielfeld, anteile)
    
# 📌 Initialisierung
if "cursor_pos" not in st.session_state:
    st.session_state.cursor_pos = (f // 2, f // 2)  # z. B. Mitte bei 10×10

if "radius" not in st.session_state:
    st.session_state.radius = 1  # Standardradius    

if "rate_abgeschlossen" not in st.session_state:
    st.session_state.rate_abgeschlossen = False
if "schussprotokoll" not in st.session_state:
    st.session_state.schussprotokoll = []
    

# 🔍 Funktion zur Ermittlung des Einschlagfelds
def einschlagfeld(r, c, radius):
    felder = []
    for dr in [0, -radius]:
        for dc in [0, -radius]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < f and 0 <= nc < f:
                felder.append((nr, nc))
    return felder
aktive_felder = einschlagfeld(*st.session_state.cursor_pos, radius=st.session_state.radius)
    

# --- Eingabe der Koordinaten ---



    
    
    


def lagrange_interpolation_mod(x_vals, y_vals, p, k):
    '''
    Bestimmt aus k Wertepaaren ein Polynom vom Grad k-1 mittels Lagrange_Interpolation.
    Liegen mehr als k Wertepaare vor, werden mithilfe von random.sample zufeallig k verschiedene Wertepaare ausgewaehlt.

    Parameters
    ----------
    x_vals (list): Die x-Werte der vergebenen Anteile
    y_vals (list): Die zu x zugehoerigen y-Werte der vergebenen Anteile
    p (int): naechsthoehere Primzahl passend zu s und n
    k (int): Anzahl der benoetigten tupels 

    Raises
    ------
    ValueError
    Da mindestens k Punkte noetig sind, um ein Polynom k-1-ten Grades zu bestimmen, wird ein Fehler ausgegeben,
    wenn weniger als k Werte vorliegen.

    Returns
    -------
    total (int): Rekonstruiertes s in modulo p
    '''
    if len(x_vals) < k:
        raise ValueError(f"Mindestens {k} Punkte nötig, aber nur {len(x_vals)} gegeben.")

    # Zufällige Auswahl von k Punkten
    indices = random.sample(range(len(x_vals)), k)
    x = [x_vals[i] for i in indices]
    y = [y_vals[i] for i in indices]

    total = 0
    for j in range(k):
        num = 1
        den = 1
        for m in range(k):
            if m != j:
                num = (num * -x[m]) % p
                den = (den * (x[j] - x[m])) % p
        inv_den = pow(den, -1, p)
        total = (total + y[j] * num * inv_den) % p

    return total

   


def konsistenzpruefung(punkte, k, p):
    '''
    Die Lagrange-Interpolation erstellt ein Polynom k-1-ten Grades zu k gegbenen Wertepaaren. Dabei kann ein fehlerhaftes
    Wertepaar zu einem falsch rekonstruierten s führen. Dies kann aber nicht erkannt werden.
    Sobald k+1 oder mehr Werte vorliegen, kann man erkennen, ob alle Punkte zusammenpassen, wenn auch die Werte, die nicht
    zu Bestimmung des Polynoms beigetragen haben, dessen Bedingungen erfuellen.
    
    "konsistenzpruefung" rekonstruiert s (mittels der Funktion lagrange_interpolation_mod(x_vals, y_vals, p, k))aus allen 
    k-großen Teilmengen der eingegebenen Wertepaare und zaehlt die Haeufigkeit der berechneten s. Stimmt diese mit der
    Anzahl der Wertepaare überein, gilt die Rekonstruktion als konsistent.
    
    Werden verschiedene s berechnet, wird deren Haeufigkeit gezaehlt und das s mit der groeßten Haeufigkeit als Vermutung ausgegeben.
    
    Je mehr zusaetzliche (nicht fehlerhafte) Wertepaare vorliegen, desto zuverlaessiger wird diese Vermutung.
    
    Parameters
    ----------
    punkte (list): die eingegebenen Wertepaare
    k (int): Anzahl der benoetigten tupels
    p (int): naechsthoehere Primzahl passend zu s und n

    Returns
    -------
    best_guess (int): das s, das beim Prüfen aller k-großen Teilmengen der eingegebenen Werte am haeufigsten vorkam
    konsistent (boolean): Wahrheitswert, "True", wenn alle k-großen Teilmengen zum gleichen s fuehren, "False" sonst.
    haeufigkeiten (dict[int, int]): Ein Dictionary, das für jedes rekonstruierte Geheimnis zaehlt, wie oft es bei den k-großen Teilmengen vorkam.
    '''
    geheime_kandidaten = []

    for subset in combinations(punkte, k):
        x_vals, y_vals = zip(*subset)
        s = lagrange_interpolation_mod(x_vals, y_vals, p, k)
        geheime_kandidaten.append(s % p)

    # Zähle, welches Ergebnis wie oft vorkommt
    haeufigkeiten = {}
    for s in geheime_kandidaten:
        haeufigkeiten[s] = haeufigkeiten.get(s, 0) + 1

    # Finde das häufigste Ergebnis
    best_guess = max(haeufigkeiten, key=haeufigkeiten.get)
    anzahl = haeufigkeiten[best_guess]

    konsistent = (anzahl == len(geheime_kandidaten))
    return best_guess, konsistent, haeufigkeiten


    
    
st.markdown(f"Du hast insgesamt {MAX_ZUEGE} Züge:")
buchstaben = "ABCDEFGHIJ"
zeilen_map = {buch: idx for idx, buch in enumerate(buchstaben)}

wasser_input = st.text_input("❌ Vermutlich nichts (z. B. A1;B3)")
ratio = 3 if f > 8 else 2
col1, col2 = st.columns([ratio, 1])


with col1:
    
    
    # --- Zusatz-Eingaben für Marker ---
    
    treffer_input = st.text_input("📌 Vermutete Treffer (z. B. C5;D7)")

    wasser_marker, fehler_wasser = parse_koordinaten(wasser_input, zeilen_map, label="Wasser-Markierung")
    treffer_marker, fehler_treffer = parse_koordinaten(treffer_input, zeilen_map, label="Treffer-Markierung")

    if fehler_wasser:
        st.warning(fehler_wasser)
    if fehler_treffer:
        st.warning(fehler_treffer)
        
    zeige_spielfeld(st.session_state.versuche, wasser_marker, treffer_marker)

with col2:
    st.subheader("Protokoll")

    if st.session_state.schussprotokoll:
        scroll_html = f"<div class='schreibmaschine' style='max-height:{150+f*35}px; overflow-y:auto; padding:0px;'>"

        for i, (koords, hits) in enumerate(st.session_state.schussprotokoll, 1):
            coords_str = ",".join(f"{chr(65 + r)}{c+1}" for r, c in koords)

            if hits == 4:
                symbol = "🔴"
            elif hits == 3:    
                symbol = "🟡"
            elif hits == 2:
                symbol = "🟢"
            elif hits == 1:
                symbol = "🔵"
            else:
                symbol = "🟣"

            scroll_html += f"<div style='margin-bottom:4px; padding:2px; border-radius:4px'>{symbol}Zug {i}: <b>{coords_str} </b></div>"

        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)
    else:
        st.info("Du hast noch keine Felder abgesucht.")
        
        




if st.session_state.phase == "spiel":
# 🕹️ Steuerungselemente
    r, c = st.session_state.cursor_pos  # Aktuelle Position
    radius = st.session_state.radius
    
# Reihe 1 – Hoch
    col_up = st.columns([1, 1, 6])
    with col_up[1]:
        if st.button("⬆️", key="up"):
            if r > radius:
                st.session_state.cursor_pos = (r - 1, c)
                st.rerun()
# Reihe 2 – Links, Abschuss, Rechts
    col_mid = st.columns([1, 1, 1, 5])
    with col_mid[0]:
        if st.button("⬅️", key="left"):
            if c > radius:
                st.session_state.cursor_pos = (r, c - 1)
                st.rerun()
    with col_mid[1]:
        if st.button("🔍", key="fire"):
           

        # Treffer auswerten
            schiffsfelder = [(r, c) for r in range(f) for c in range(f) if st.session_state.spielfeld[r][c] == 1]
            treffer = [pos for pos in aktive_felder if pos in schiffsfelder]

            st.session_state.versuche += aktive_felder
            st.session_state.schussprotokoll.append((aktive_felder, len(treffer)))
            st.session_state.zug_nr += 1

            st.session_state.treffer_feedback = f"🔍 {len(treffer)} Treffer!"
            st.rerun()


    with col_mid[2]:
        if st.button("➡️", key="right"):
            if c < f - 1:
                st.session_state.cursor_pos = (r, c + 1)
                st.rerun()
                

        
# Reihe 3 – Runter
    col_down = st.columns([1, 1, 3,3])
    with col_down[1]:
        if st.button("⬇️", key="down"):
            if r < f - 1:
                st.session_state.cursor_pos = (r + 1, c)
                st.rerun()

    with col_down[2]:
        
       
# 📐 Radiuswahl
        neuer_radius = st.slider("🌀 Streuradius", 1, 5, value=st.session_state.get("radius", 1))

        if neuer_radius != st.session_state.get("radius"):
            st.session_state.radius = neuer_radius
            
            # Cursor validieren nach neuem Radius
            r, c = st.session_state.cursor_pos
            max_r = f - 1            # unterste erlaubte Zeile
            max_c = f - 1            # rechte erlaubte Spalte
            min_r = neuer_radius     # oberste gültige Zeile
            min_c = neuer_radius     # linkeste gültige Spalte

            r = min(max(r, min_r), max_r)
            c = min(max(c, min_c), max_c)
            st.session_state.cursor_pos = (r, c)
            
            st.rerun()

        
        
    if "treffer_feedback" in st.session_state:
        st.toast(st.session_state.treffer_feedback)


        # Phase-Wechsel prüfen
    if st.session_state.zug_nr > MAX_ZUEGE:
        st.session_state.phase = "raten"
else:
    st.warning("🔒 Die Züge sind aufgebraucht – du kannst jetzt nicht mehr suchen.")
        
st.session_state.radius = neuer_radius

rekonstruieren = st.checkbox("🧩 Geheimnis jetzt rekonstruieren")

# Phase initialisieren
if "phase" not in st.session_state:
    st.session_state.phase = "spiel"

# Wenn maximale Züge überschritten → Ratephase
if st.session_state.zug_nr > MAX_ZUEGE:
    st.session_state.phase = "raten"

if st.session_state.phase == "raten" or rekonstruieren:
    st.header("🖊️ Rekonstruiere Geheimnis:")
    
    punkte_input = st.text_input("📥 Wertepunkte (x,y;x,y;...)", value="1,5;2,3;3,8")
    
   
    try:
        punkte = [tuple(map(int, pair.split(","))) for pair in punkte_input.split(";") if pair.strip()]
    except:
        st.error("❌ Ungültiges Format bei den Punkten. Bitte als x,y;x,y;... eingeben.")
        punkte = []
        
    

   
    if len(punkte) < k:
        st.warning(f"⚠️ Du brauchst mindestens {k} Anteile für die Rekonstruktion.")
    elif st.button("🧩 Rekonstruktion starten"):
        try:
            s_guess, konsistent, stimmen = konsistenzpruefung(punkte, k, p)
            werte = list(stimmen.values())
            max_h = max(werte)
            max_kandidaten = [s for s, h in stimmen.items() if h == max_h]

        # 🟡 Spezialfall: alle s-Werte gleich oft?
            if len(max_kandidaten) > 1:
                st.error("🔄 Kein eindeutiges Geheimnis rekonstruierbar: Mehrere s-Werte treten gleich oft auf.")
                st.write("🧩 Gleich häufige Kandidaten:")
                st.code(", ".join(str(s) for s in max_kandidaten))
                st.info("💡 **Tipp:** Füge einen weiteren Anteil hinzu, um eine Entscheidung zu ermöglichen.")
            
            elif konsistent:
                if s_guess == st.session_state.geheimes_s:
                    st.success(f"✅ Geheimnis richtig rekonstruiert: s = {s_guess}")
                    st.balloons()
                else:
                    st.error("Upps! Das ist das falsche Geheimnis!")
            else:
                st.warning(f"⚠️ Nicht eindeutig: häufigstes s = {s_guess}")
                st.write("Ergebnisse der Häufigkeitsanalyse:")
                st.json(stimmen)
                
            
                # 🕵️‍♂️ Analyse möglicher Störpunkte
                fehlerbericht = []
                for i, punkt in enumerate(punkte):
                     ohne_punkt = punkte[:i] + punkte[i+1:]
                     if len(ohne_punkt) >= k:
                         s_test, konsistent_test, _ = konsistenzpruefung(ohne_punkt, k, p)
                         if konsistent_test:
                             fehlerbericht.append(f"Ohne Punkt {punkt} ergibt sich konsistent **s = {s_test}**")

                if fehlerbericht:
                     text = "🧯 **Verdächtiger Punkt:**\n\n" + "\n".join(f"- {zeile}" for zeile in fehlerbericht)
                     st.info(text)
                if not fehlerbericht:
                     tipp = "**Verdacht auf falsche Anteile!**\n\n" + "**Tipp:** Entferne einen Punkt und versuche es erneut!"
                     st.info(tipp)
            
        except Exception as e:
            st.error(f"❌ Fehler bei der Rekonstruktion: {e}")
