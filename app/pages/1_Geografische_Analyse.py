import streamlit as st
import pandas as pd
import holoviews as hv
import sys
import csv

sys.path.insert(0, 'C:/Users/linus/OneDrive/BSc_Data_Science/Semester_2/Data_Visualisation/visualization_project/app'
                   '/classes')
import relation_chord_chart as rcc
import geo_map as gm
from topic_analysis import TopicAnalysis
import sent_sub_obj as sso


@st.cache_data
def load_data():
    path = '../data/without_content.tsv.xz'
    df = pd.read_csv(path, sep='\t', compression='xz')
    df['countries'] = df['countries'].apply(eval)
    df['entities_header'] = df['entities_header'].apply(eval)
    df['people'] = df['people'].apply(eval)
    df['date'] = pd.to_datetime(df['date'])
    return df


df = load_data()
df.columns = ['Medium', 'Headline', 'Datum', 'Länder', 'sentiment', 'subjectivity',
                           'Entitäten Header', 'Kategorie', 'Länder (englisch)', 'Personen']

# layout streamlit app
st.header('Geografische Analyse')
st.button('ℹ️', help="Mit den Filteroptionen können Sie die angezeigten Daten nach spezifischen "
                     "Kriterien einschränken. Die verfügbaren Filteroptionen sind: \n"
                     "1. Datum: Mit dieser Option können Sie ein beliebiges Datum auswählen."
                     "möglich, Daten für jeden beliebigen Tag im Jahr 2022 zu analysieren. \n\n"
                     "2. Kategorie: Hier können Sie auswählen, welche Artikelkategorien in den Daten enthalten "
                     "sein sollen. \n"
                     "3. Länder: Mit dieser Option können Sie auswählen, welche Länder in den Daten enthalten "
                     "sein sollen. ")

col1, col2, col3 = st.columns([1, 1, 1])  # Widgets
full_width_col1 = st.columns(1)  # Geo map
full_width_col2 = st.columns(1)  # Topic Analysis
col4 = st.columns([1, 1])  # Chord chart & Sentiment / Objectivity
full_width_col3 = st.columns(1)  # Dataframe


# CONFIG FOR ALL PLOTS
config = dict({'displayModeBar': False})

# remove streamlit menu
st.markdown("""
                                    <style>
                                    #MainMenu {visibility: hidden;}
                                    footer {visibility: hidden;}
                                    </style>
                                    """, unsafe_allow_html=True)

# DATE SELECTION (FILTER)
selected_date = col1.date_input("Wähle Datum",
                                value=pd.to_datetime('2022-02-24'),
                                min_value=pd.to_datetime('2022-01-01'),
                                max_value=pd.to_datetime('2022-12-31'))
selected_date = pd.to_datetime(selected_date)
filtered_df = df[df['Datum'] == selected_date]

# CATEGORY SELECTION (FILTER)
with col2:
    categories = df['Kategorie'].unique()
    categories_options = ['Alle'] + list(categories)
    selected_categories = st.multiselect('Wähle Kategorie', categories_options, default=['Alle'])
    if 'Alle' not in selected_categories:
        filtered_df = filtered_df[filtered_df['Kategorie'].isin(selected_categories)]
    else:
        pass

# COUNTRY SELECTION (FILTER)
with col3:
    country_en_de_dict = {}
    with open('../data/countries_en_de.csv', 'r', encoding='UTF-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            country_en_de_dict[row[1]] = row[0]
    countries = list(country_en_de_dict.keys())
    country_options = ['Alle'] + countries
    # create multiselect widget
    selected_countries = st.multiselect('Wähle Land', country_options, default=['Alle'])


    def contains_country(country_list, countries):
        for country in countries:
            if country in country_list:
                return True
        return False


    if 'Alle' not in selected_countries:
        filtered_df = filtered_df[filtered_df['Länder'].apply(lambda x:
                                                              all(country in x for country in selected_countries))]
    else:
        pass

# CHORD RELATION DIAGRAM
chord_chart = rcc.ChordCharts(filtered_df['Länder']).country_chord_chart()
with col4[0]:
    st.header("Länder Vorkomnisse in Artikel")
    st.bokeh_chart(hv.render(chord_chart, backend='bokeh'))


# SENTIMENT PLOT
sentiment_plot = sso.SentimentPlot(filtered_df['sentiment'])
sentiment_plot.create_plot()

with col4[1]:
    st.header("Stimmung")
    st.button('ℹ️', help="Die Stimmungsanalyse (Sentiment-Analyse) ist eine Technik aus dem Bereich der Künstlichen Intelligenz, n"
                  "Die Stimmungsanalyse (Sentiment-Analyse) ist eine Technik aus dem Bereich der Künstlichen Intelligenz, n"
                  "die verwendet wird, um die Stimmung oder den emotionalen Ton von Inhalten zu ermitteln. In unserem Fall "
                  "haben wir diese Methode auf Zeitungsartikel angewendet.\n\n"
    
                  "Unsere Analyse teilt die Ergebnisse in vier Kategorien ein: --, -, +, ++. \n"
    
                  "1. --: Diese Kategorie umfasst Artikel, die eine stark negative Stimmung ausdrücken. Dies könnte sich "
                  "auf Artikel beziehen, die schwerwiegende Probleme, Kontroversen oder negative Ereignisse behandeln.\n"
    
                  "2. -: Artikel in dieser Kategorie weisen eine allgemein negative Stimmung auf, jedoch nicht so stark "
                  "wie die in der Kategorie --\n"
    
                  "3. +: Diese Artikel vermitteln eine generell positive Stimmung. Sie könnten positive Entwicklungen, "
                  "Erfolge oder freudige Ereignisse thematisieren.\n"
    
                  "4. ++: Artikel in dieser Kategorie drücken eine sehr positive Stimmung aus. Sie könnten außergewöhnlich "
                  "positive Ereignisse oder hervorragende Erfolge darstellen.\n\n"
                  "Bitte beachten Sie, dass die Sentiment-Analyse auf maschinellem Lernen basiert und nicht perfekt ist. Sie "
                  "dient als Anhaltspunkt für die generelle Stimmungslage in den analysierten Artikeln, kann aber bestimmte "
                  "Nuancen und Kontexte übersehen.")

    st.plotly_chart(sentiment_plot.fig, config=config)


# SUBJECTIVITY PLOT
subjectivity_plot = sso.SubjectivityPlot(filtered_df['subjectivity'])
subjectivity_plot.create_plot()
objectivity_subjectivity_description = """
Die Objektivitäts- und Subjektivitätsanalyse ist eine Methode, um zu beurteilen, wie objektiv oder subjektiv ein Text ist. Objektive Texte enthalten im Allgemeinen Fakten, während subjektive Texte Meinungen, Annahmen und persönliche Ansichten ausdrücken.

In unserem Fall wenden wir diese Analyse auf Zeitungsartikel an. Unsere Analyse kategorisiert jeden Artikel entweder als "OBJ" für objektiv oder "SUB" für subjektiv. Diese Einstufung basiert auf einer Reihe von Faktoren, einschließlich der Verwendung von faktischen versus emotionalen Wörtern, dem Kontext und dem allgemeinen Ton des Artikels.

1. "OBJ": Artikel in dieser Kategorie sind in der Regel objektiv. Sie enthalten Fakten, Zahlen und konkrete Informationen. Diese Artikel enthalten wenig bis gar keine persönlichen Meinungen oder emotionale Sprache.

2. "SUB": Artikel in dieser Kategorie sind in der Regel subjektiv. Sie können persönliche Meinungen, Annahmen, emotionale Sprache und persönliche Ansichten enthalten. Diese Artikel können immer noch Fakten und Informationen enthalten, aber sie sind in der Regel mit einer subjektiven Perspektive oder Interpretation verknüpft.

Bitte beachten Sie, dass die Analyse von Objektivität und Subjektivität auf maschinellem Lernen basiert und nicht perfekt ist. Sie dient als Anhaltspunkt für den generellen Ton und die Art des Inhalts in den analysierten Artikeln, kann aber bestimmte Nuancen und Kontexte übersehen.
"""

with col4[1]:
    st.header("Subjektivität")
    st.button('ℹ️', help=objectivity_subjectivity_description)
    st.plotly_chart(subjectivity_plot.fig,config=config)

# WORLDMAP
data_country_series = filtered_df['Länder (englisch)']
data_country_list = [eval(i) for i in data_country_series.dropna().tolist()]

world_map = gm.WorldMap(data_country_list)
world_map_chart = world_map.erstelle_weltkarte()
with full_width_col1[0]:
    st.header("Ländernennung")
    st.plotly_chart(world_map_chart, config={'scrollZoom': False, 'displayModeBar': False}, use_container_width=True)

# TOPIC ANALYSIS
with full_width_col2[0]:
    st.subheader('Themen Analyse')
    st.button('ℹ️', help='Die Themen Analyse zeigt die am häufigsten vorkommenden Wörter '
                         'in den Artikeln an.')
    topic_analysis = TopicAnalysis()
    st.plotly_chart(topic_analysis.plot_most_common_words(filtered_df['Entitäten Header'], 20),config=config)

# DATA TABLE
with full_width_col3[0]:
    filtered_df['Datum'] = filtered_df['Datum'].dt.strftime('%d.%m.%Y')
    st.subheader('Artikeltabelle')
    st.button('ℹ️', help='Die Tabelle zeigt die Artikel an, nach denen die Filter gesetzt wurden.')
    st.dataframe(filtered_df.loc[:, ['Medium', 'Headline', 'Kategorie', 'Datum']], width=1100)

if __name__ == '__main__':
    pass
