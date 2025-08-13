# Spårbarhetsrapport - Streamlit App

En webbapplikation för att generera spårbarhetsrapporter från Excel-filer. Applikationen låter användare ladda upp två Excel-filer och genererar automatiskt en interaktiv HTML-rapport som visar spårbarhetsdata i hierarkisk struktur.

## Funktioner

- 📁 **Filuppladdning**: Ladda upp 2+ Excel-filer samtidigt med drag-and-drop
- 🤖 **Smart parsning**: Identifierar automatiskt filtyp (nivålista, lagerlogg, sök i spårbarhet)  
- 🏗️ **Hierarkisk struktur**: Bevarar och visar komplex produktstruktur med indrag och nivåer
- 🎨 **Professionell design**: Responsive HTML-rapporter med modern typografi
- 🖨️ **Utskriftsvänlig**: Optimerad för utskrift och PDF-export
- 🗑️ **Smart cache**: Automatisk rensning när nya filer laddas upp
- ☁️ **Molnbaserad**: Körs direkt i webbläsaren via Streamlit Cloud

## Live Demo

🚀 **[Prova appen live här!](https://sparbarhet-rapport.streamlit.app)** *(länk kommer när appen är deployad)*

## Lokal installation

### Förutsättningar

- Python 3.8 eller högre
- pip (Python package manager)

### Installation

1. Klona repositoryt:
```bash
git clone https://github.com/[ditt-användarnamn]/sparbarhet-streamlit.git
cd sparbarhet-streamlit
```

2. Installera beroenden:
```bash
pip install -r requirements.txt
```

3. Kör applikationen:
```bash
streamlit run streamlit_app.py
```

4. Öppna webbläsaren och gå till `http://localhost:8501`

## Användning

1. **Ladda upp filer**: Välj två Excel-filer genom att dra och släppa dem eller klicka på uppladdningsområdena
2. **Visa statistik**: När filerna är uppladdade visas statistik om antal artiklar och poster
3. **Generera rapport**: Klicka på "Visa spårbarhetsrapport" för att generera och visa rapporten
4. **Exportera**: Använd knapparna i rapporten för att skriva ut eller spara som PDF

## Filformat som stöds

Applikationen stöder följande Excel-filtyper:
- **Nivålista**: Hierarkisk struktur med artiklar och operationer
- **Lagerlogg**: Lagertransaktioner med batch- och chargenummer
- **Sök i spårbarhet**: Exporterade sökresultat från spårbarhetssystem

## Teknisk arkitektur

```
streamlit_app.py          # Huvudapplikation med Streamlit UI
├── traceability_parser.py    # Parser för olika Excel-format
├── traceability_model.py     # Datamodeller och databas
└── html_generator.py         # HTML-rapportgenerator
```

## Deployment till Streamlit Cloud

1. Forka detta repository till din GitHub
2. Logga in på [Streamlit Cloud](https://streamlit.io/cloud)
3. Klicka på "New app"
4. Välj ditt repository och branch
5. Ange `streamlit_app.py` som huvudfil
6. Klicka på "Deploy"

## Bidra

Pull requests är välkomna! För större ändringar, öppna först ett issue för att diskutera vad du vill ändra.

## Licens

[MIT](https://choosealicense.com/licenses/mit/)

## Support

Vid frågor eller problem, öppna ett issue på GitHub eller kontakta [din-email@exempel.se]

## Utvecklat av

[Ditt namn/organisation]

---

**Not**: Denna applikation är optimerad för svenska spårbarhetsdata och använder svenska termer i gränssnittet.