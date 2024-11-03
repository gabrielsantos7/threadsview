import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


@st.cache_data
def load_data():
    path = Path(__file__).parent / "dataset" / "threads.xlsx"

    # Carrega todas as planilhas em um dicionário de DataFrames
    data_dict = pd.read_excel(path, sheet_name=None)

    # Concatena todos os DataFrames em um único DataFrame
    combined_df = pd.concat(data_dict.values(), ignore_index=True)

    # Converter a coluna "Data e Hora" para datetime
    combined_df["Data e Hora"] = pd.to_datetime(
        combined_df["Data e Hora"], errors='coerce', format="%d/%m/%Y %H:%M:%S"
    )
    print(combined_df)
    return combined_df


def main():
    # Configura o layout para ocupar toda a largura da tela
    st.set_page_config(layout='wide')

    # Lê o conteúdo do arquivo README.md
    with open("README.md", "r", encoding="utf-8") as file:
        readme_content = file.read()

    # Renderiza o conteúdo em Markdown
    st.markdown(readme_content)

    # Carregando e tratando os dados
    df = load_data()

    st.sidebar.title("Filtros")
    keywords = st.sidebar.multiselect(
        "Palavras - Chave",
        df["Palavras-Chave"].unique(),
        df["Palavras-Chave"].unique()
    )

    # Definindo o intervalo de datas usando a coluna convertida
    date_interval = st.sidebar.date_input(
        "Intervalo de datas",
        (df["Data e Hora"].min().date(), df["Data e Hora"].max().date()),
        min_value=df["Data e Hora"].min().date(),
        max_value=df["Data e Hora"].max().date(),
        format="DD/MM/YYYY"
    )

    # Convertendo o intervalo de data para datetime64
    start_date = pd.to_datetime(date_interval[0])
    end_date = pd.to_datetime(date_interval[1])

    # Aplicando os filtros
    df_filtered = df[
        (df["Palavras-Chave"].isin(keywords)) &
        (df["Data e Hora"].between(start_date, end_date))
    ]

    if keywords:
        st.subheader("Threads coletadas")
        st.write(f'Foram coletadas um total de {
            len(df_filtered)} threads com as palavras-chave: {", ".join(keywords)} no intervalo de tempo selecionado.')
        st.dataframe(df_filtered)

        st.subheader("Análises gráficas")
        comments_fig = px.bar(df_filtered, x="Palavras-Chave", y="Comentários",
                              title="Números de comentários por palavra-chave")
        st.plotly_chart(comments_fig)

        posts_por_data = df_filtered.groupby(df_filtered['Data e Hora'].dt.date).size(
        ).reset_index(name='Número de posts')
        date_fig = px.line(posts_por_data, x="Data e Hora", y="Número de posts",
                           title="Número de posts ao longo do período")
        st.plotly_chart(date_fig)

    else:
        st.warning(
            "Selecione ao menos uma palavra-chave para apresentar os resultados.")

    st.subheader("Conclusão")
    st.write("""
    A pesquisa revelou que as threads coletadas abordaram uma ampla gama de assuntos relacionados ao Brasil e à cultura afro-brasileira, destacando a riqueza e diversidade dos tópicos discutidos. A ferramenta desenvolvida demonstrou ser altamente eficaz na coleta e análise desses dados, provando seu potencial para ser reutilizada em pesquisas envolvendo diferentes temas e palavras-chave.

    Apesar do sucesso obtido, a rede social estudada apresenta algumas limitações em termos de busca e filtragem de conteúdo, especialmente quando comparada ao Twitter. A plataforma do Twitter permite a realização de pesquisas complexas com múltiplos filtros, como data de publicação, idioma, geolocalização e outros parâmetros avançados. Essas funcionalidades ampliam as possibilidades de análise e podem representar uma vantagem em projetos de coleta de dados mais detalhados e personalizados.
    """)


main()
