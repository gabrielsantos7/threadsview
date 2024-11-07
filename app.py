import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

def get_extended_date_range(data, date_column):
    # Obtém as datas mínima e máxima do DataFrame
    min_date = data[date_column].min()
    max_date = data[date_column].max()

    # Adiciona um dia extra para ampliar o intervalo
    extended_min_date = min_date - pd.Timedelta(days=1)
    extended_max_date = max_date + pd.Timedelta(days=1)

    return extended_min_date, extended_max_date

@st.cache_data
def load_data():
    # Define o caminho do arquivo
    file_path = Path(__file__).parent / "dataset" / "threads.xlsx"

    # Carrega todas as planilhas em um dicionário de DataFrames
    df = pd.read_excel(file_path, sheet_name="Filtered_Posts")

    # Concatena todos os DataFrames em um único DataFrame
    # combined_df = pd.concat(sheet_data.values(), ignore_index=True)

    # Converte a coluna "Data e Hora" para o tipo datetime
    df["Data e Hora"] = pd.to_datetime(
        df["Data e Hora"], errors='coerce', format="%d/%m/%Y %H:%M:%S"
    )

    return df


def main():
    # Configura o layout da página
    st.set_page_config(layout='wide')

    # Carrega o conteúdo do arquivo README.md
    with open("README.md", "r", encoding="utf-8") as file:
        readme_content = file.read()
    st.markdown(readme_content)

    # Carrega os dados
    data = load_data()

    # Configura filtros na barra lateral
    st.sidebar.title("Filtros")
    selected_keywords = st.sidebar.multiselect(
        "Palavras-Chave",
        data["Palavras-Chave"].unique(),
        default=data["Palavras-Chave"].unique()
    )

    # Usa a função para obter as datas mínima e máxima estendidas
    filter_start_date, filter_end_date = get_extended_date_range(data, "Data e Hora")

    # Define o intervalo de datas com base nas datas estendidas
    date_range = st.sidebar.date_input(
        "Intervalo de datas",
        (filter_start_date.date(), filter_end_date.date()),
        min_value=filter_start_date.date(),
        max_value=filter_end_date.date()
    )
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    # Filtra os dados com base nos filtros selecionados
    filtered_data = data[
        (data["Palavras-Chave"].isin(selected_keywords)) &
        (data["Data e Hora"].between(start_date, end_date))
    ]

    if selected_keywords:
        # Seção de análises gerais
        st.subheader("📊 Visão Geral sobre o conteúdo coletado")
        col1, col2, col3, col4 = st.columns(4)

        
        # Exibe métricas formatadas
        col1.metric("Número de threads", f"{len(filtered_data):,}".replace(",", "."))
        col2.metric("Soma de curtidas", f"{filtered_data['Curtidas'].sum():,}".replace(",", "."))
        col3.metric("Soma de comentários", f"{filtered_data['Comentários'].sum():,}".replace(",", "."))
        col4.metric("Soma de republicações", f"{filtered_data['Republicações'].sum():,}".replace(",", "."))

        # Exibe o DataFrame filtrado
        st.dataframe(filtered_data)

        # Preparação dos dados para o gráfico de engajamento
        st.subheader("📈 Análises gráficas")
        engagement_summary = filtered_data.groupby("Palavras-Chave")[["Curtidas", "Comentários", "Republicações"]].sum().reset_index()
        engagement_summary["Engajamento Total"] = engagement_summary[["Curtidas", "Comentários", "Republicações"]].sum(axis=1)

        # Gráfico de barras para engajamento total
        engagement_chart = px.bar(
            engagement_summary, x="Palavras-Chave", y="Engajamento Total",
            title="Engajamento (Soma de Curtidas, Comentários e Republicações) por Palavra-Chave"
        )
        st.plotly_chart(engagement_chart)

        # Preparação e visualização do gráfico de posts por data
        posts_by_date = filtered_data.groupby(filtered_data['Data e Hora'].dt.date).size().reset_index(name='Número de posts')
        date_chart = px.line(posts_by_date, x="Data e Hora", y="Número de posts", title="Número de posts ao decorrer do tempo")
        st.plotly_chart(date_chart)

    else:
        st.warning("Selecione ao menos uma palavra-chave para apresentar os resultados.")

    # Seção de conclusão
    st.subheader("🔍 Conclusão")
    st.write("""
    A pesquisa revelou que as threads coletadas abordaram uma ampla gama de assuntos relacionados ao Brasil e à cultura afro-brasileira, destacando a riqueza e diversidade dos tópicos discutidos. A ferramenta desenvolvida demonstrou ser altamente eficaz na coleta e análise desses dados, provando seu potencial para ser reutilizada em pesquisas envolvendo diferentes temas e palavras-chave.

    Apesar do sucesso obtido, a rede social estudada apresenta algumas limitações em termos de busca e filtragem de conteúdo, especialmente quando comparada ao Twitter. A plataforma do Twitter permite a realização de pesquisas complexas com múltiplos filtros, como data de publicação, idioma, geolocalização e outros parâmetros avançados. Essas funcionalidades ampliam as possibilidades de análise e podem representar uma vantagem em projetos de coleta de dados mais detalhados e personalizados.
    """)

main()
