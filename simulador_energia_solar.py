import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests

# Configurações da página
st.set_page_config(
    page_title="Simulador de Energia Solar",
    page_icon="☀️",
    layout="wide"
)

# Função para calcular energia gerada
def calcular_energia_gerada(area, eficiencia, irradiacao, temperatura):
    """
    Fórmula simplificada:
    Energia (kWh/dia) = Área (m²) * Eficiência (%) * Irradiação (kWh/m²/dia) * (1 - 0.005*(Temperatura - 25))
    """
    return area * eficiencia * irradiacao * (1 - 0.005 * (temperatura - 25))

# Função para obter dados climáticos
def obter_dados_climaticos(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperatura = data['main']['temp']
        irradiacao = (100 - data['clouds']['all']) / 100 * 5  # Estimativa de irradiação (kWh/m²/dia)
        return temperatura, irradiacao
    else:
        st.error("Erro ao obter dados climáticos. Verifique a API key.")
        return None, None

# Interface principal
def main():
    st.title("Simulador de Energia Solar ☀️")
    st.markdown("""
    **Como usar**:
    1. Insira a latitude e longitude da localização.
    2. Defina a área disponível para painéis solares (em m²).
    3. Insira a eficiência dos painéis (%).
    4. Cole sua API Key do OpenWeatherMap.
    5. Clique em **Simular**!
    """)

    # Sidebar para entrada de dados
    st.sidebar.header("Configurações")
    lat = st.sidebar.number_input("Latitude", value=-23.5505)  # Exemplo: São Paulo
    lon = st.sidebar.number_input("Longitude", value=-46.6333)
    area = st.sidebar.number_input("Área disponível (m²)", value=50.0)
    eficiencia = st.sidebar.number_input("Eficiência dos painéis (%)", value=20.0) / 100
    api_key = st.sidebar.text_input("API Key do OpenWeatherMap", type="password")

    if st.sidebar.button("Simular"):
        if api_key:
            with st.spinner("Calculando..."):
                temperatura, irradiacao = obter_dados_climaticos(lat, lon, api_key)
                if temperatura and irradiacao:
                    energia_gerada = calcular_energia_gerada(area, eficiencia, irradiacao, temperatura)

                    # Exibindo resultados
                    st.header("📊 Resultados")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Energia Gerada", f"{energia_gerada:.2f} kWh/dia")
                    col2.metric("Temperatura", f"{temperatura} °C")
                    col3.metric("Irradiação Solar", f"{irradiacao:.2f} kWh/m²/dia")

                    # Gráfico de 30 dias
                    st.subheader("Projeção Mensal")
                    dias = np.arange(1, 31)
                    energia_mensal = [energia_gerada * dia for dia in dias]
                    plt.figure(figsize=(10, 5))
                    plt.plot(dias, energia_mensal, marker='o', color='orange')
                    plt.title("Energia Gerada em 30 Dias")
                    plt.xlabel("Dias")
                    plt.ylabel("Energia Total (kWh)")
                    plt.grid(True)
                    st.pyplot(plt)

                    # Cálculo de redução de CO2 (exemplo: 0.5 kg de CO2 por kWh economizado)
                    reducao_co2 = energia_gerada * 0.5 * 30  # Estimativa mensal
                    st.info(f"🌿 Redução estimada de CO2: **{reducao_co2:.2f} kg/mês**")
        else:
            st.error("Insira uma API Key válida.")

if __name__ == "__main__":
    main()