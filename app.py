import streamlit as st
from openai import OpenAI
from datetime import datetime

# Configurar cliente OpenAI usando secrets do Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def refinar_texto_com_openai(texto):
    """Função para refinar o texto usando OpenAI GPT"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em correção gramatical, coesão e coerência de textos oficiais da Polícia Militar. Corrija apenas erros gramaticais, melhore a coesão e coerência do texto, mantendo o formato original e o tom formal. Não altere informações factuais ou dados específicos."
                },
                {
                    "role": "user",
                    "content": f"Por favor, corrija este relatório policial mantendo todas as informações originais, apenas melhorando a gramática, coesão e coerência:\n\n{texto}"
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao conectar com OpenAI: {str(e)}")
        return texto

def gerar_historico(dados):
    """Função para gerar o histórico baseado no template"""
    
    # Template base
    template = f"""Em atendimento à Ordem de Serviço, vinculada ao Programa de Segurança Rural no Vale do Jamari, foi realizada uma visita técnica em {dados['data']}, com início às {dados['hora_inicio']} e término às {dados['hora_fim']}. A diligência ocorreu na propriedade rural denominada {dados['tipo_propriedade']} "{dados['nome_propriedade']}", situada em {dados['endereco']}, na Zona Rural do município de {dados['municipio']}/{dados['uf']}. Procedeu-se ao levantamento das coordenadas geográficas, sendo a porteira de acesso principal localizada em {dados['lat_long_porteira']}, e a sede/residência principal em {dados['lat_long_sede']}. A área total da propriedade compreende {dados['area']} {dados['unidade_area']}. O proprietário, Sr. "{dados['nome_proprietario']}", inscrito no CPF/CNPJ sob o nº "{dados['cpf_cnpj']}", com contato telefônico principal "{dados['telefone']}", esteve presente durante a visita. A principal atividade econômica desenvolvida no local é "{dados['atividade_principal']}"."""
    
    # Adicionar informação sobre veículos apenas se houver
    if dados['veiculos']:
        template += f" Foram identificados os seguintes veículos automotores na propriedade: {dados['veiculos']}."
    
    # Adicionar informação sobre rebanho apenas se houver marca de gado
    if dados['marca_gado']:
        template += f" O rebanho possui marca/sinal/ferro registrado como \"{dados['marca_gado']}\"."
    
    template += f""" A visita teve como objetivo central o cadastro e georreferenciamento da propriedade no sistema do Programa de Segurança Rural, o que foi efetivado. Consequentemente, foi afixada a placa de identificação do programa, de nº "{dados['numero_placa']}", entregue via mídia digital. Adicionalmente, foram repassadas ao proprietário orientações concernentes ao programa mencionado, a fim de sanar as dúvidas existentes. A presente visita cumpriu os objetivos estabelecidos pela referida Ordem de Serviço, sendo as informações coletadas e registradas com base nas declarações do proprietário e na verificação in loco."""
    
    return template

def main():
    st.set_page_config(
        page_title="Gerador de Histórico Policial - Segurança Rural",
        page_icon="🚔",
        layout="wide"
    )
    
    st.title("🚔 Gerador de Histórico Policial")
    st.subheader("Programa de Segurança Rural - Vale do Jamari")
    
    # Verificar se a API Key está configurada
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("⚠️ API Key da OpenAI não configurada! Configure no arquivo .streamlit/secrets.toml")
        st.stop()
    
    # Sidebar com instruções
    with st.sidebar:
        st.header("📋 Instruções")
        st.write("1. Preencha todos os campos obrigatórios")
        st.write("2. Marque se existe marca de gado registrada")
        st.write("3. Clique em 'Gerar Histórico'")
        st.write("4. O texto será refinado automaticamente")
        st.write("5. Copie o resultado final")
    
    # Formulário principal
    with st.form("formulario_historico"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("📅 Dados da Visita")
            data = st.date_input("Data da visita")
            hora_inicio = st.time_input("Hora de início")
            hora_fim = st.time_input("Hora de término")
            
            st.header("🏠 Dados da Propriedade")
            tipo_propriedade = st.selectbox("Tipo de propriedade", ["Sítio", "Fazenda", "Chácara", "Estância"])
            nome_propriedade = st.text_input("Nome da propriedade", placeholder="Ex: São José")
            endereco = st.text_area("Endereço completo", placeholder="Inclua referências se houver")
            municipio = st.text_input("Município")
            uf = st.selectbox("UF", ["RO", "AC", "AM", "RR", "PA", "TO", "MT", "MS", "GO", "DF"])
            
        with col2:
            st.header("📍 Coordenadas GPS")
            lat_long_porteira = st.text_input("Coordenadas da porteira (Lat, Long)", placeholder="Ex: -9.897289, -63.017788")
            lat_long_sede = st.text_input("Coordenadas da sede (Lat, Long)", placeholder="Ex: -9.897500, -63.017900")
            
            st.header("📏 Área e Proprietário")
            area = st.number_input("Área da propriedade", min_value=0.0, step=0.1)
            unidade_area = st.selectbox("Unidade", ["hectares", "alqueires"])
            nome_proprietario = st.text_input("Nome do proprietário")
            cpf_cnpj = st.text_input("CPF/CNPJ", placeholder="000.000.000-00 ou 00.000.000/0000-00")
            telefone = st.text_input("Telefone", placeholder="(69) 99999-9999")
        
        st.header("💼 Atividade Econômica")
        atividade_principal = st.text_input("Atividade principal", placeholder="Ex: Criação de bovinos")
        
        st.header("🚗 Veículos (Opcional)")
        veiculos = st.text_area("Descrição dos veículos", 
                               placeholder="Ex: uma caminhonete marca Ford, modelo Ranger, placa ABC-1234, cor Prata; um trator marca Massey Ferguson, modelo 265, sem placa, cor Vermelha")
        
        st.header("🐄 Rebanho")
        marca_gado = st.text_input("Marca/sinal/ferro registrado (Opcional)", 
                                  placeholder="Ex: JB na paleta esquerda")
        
        st.header("🏷️ Placa de Identificação")
        numero_placa = st.text_input("Número da placa", placeholder="Ex: PSR-001")
        
        # Botão de submissão
        submitted = st.form_submit_button("🚀 Gerar Histórico", use_container_width=True)
        
        if submitted:
            # Validar campos obrigatórios
            campos_obrigatorios = [
                data, hora_inicio, hora_fim, nome_propriedade, endereco,
                municipio, lat_long_porteira, lat_long_sede,
                area, nome_proprietario, cpf_cnpj, telefone, atividade_principal,
                numero_placa
            ]
            
            if not all(campos_obrigatorios):
                st.error("❌ Por favor, preencha todos os campos obrigatórios!")
                return
            
            # Preparar dados
            dados = {
                'data': data.strftime("%d/%m/%Y"),
                'hora_inicio': hora_inicio.strftime("%H:%M"),
                'hora_fim': hora_fim.strftime("%H:%M"),
                'tipo_propriedade': tipo_propriedade,
                'nome_propriedade': nome_propriedade,
                'endereco': endereco,
                'municipio': municipio,
                'uf': uf,
                'lat_long_porteira': lat_long_porteira,
                'lat_long_sede': lat_long_sede,
                'area': str(area),
                'unidade_area': unidade_area,
                'nome_proprietario': nome_proprietario,
                'cpf_cnpj': cpf_cnpj,
                'telefone': telefone,
                'atividade_principal': atividade_principal,
                'veiculos': veiculos,
                'marca_gado': marca_gado,
                'numero_placa': numero_placa
            }
            
            # Gerar histórico
            with st.spinner("🔄 Gerando histórico..."):
                historico_bruto = gerar_historico(dados)
            
            # Refinar com OpenAI
            with st.spinner("✨ Refinando texto com IA..."):
                historico_refinado = refinar_texto_com_openai(historico_bruto)
            
            # Exibir resultado
            st.success("✅ Histórico gerado com sucesso!")
            
            st.header("📄 Histórico Final")
            st.text_area("Copie o texto abaixo:", value=historico_refinado, height=400)
            
            # Botão para copiar
            st.code(historico_refinado, language=None)

if __name__ == "__main__":
    main()