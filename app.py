import streamlit as st
from openai import OpenAI
from datetime import datetime
import streamlit.components.v1 as components
import re

# Configurar cliente OpenAI usando secrets do Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def validar_formato_hora_strptime(hora_str: str) -> bool:
    """Valida se a string da hora está no formato HH:MM e se os valores são válidos."""
    if not isinstance(hora_str, str):
        return False
    
    # Remove espaços em branco
    hora_str = hora_str.strip()
    
    # Verifica se está vazio
    if not hora_str:
        return False
    
    # Verifica formato básico com regex
    if not re.match(r'^\d{1,2}:\d{2}$', hora_str):
        return False
    
    try:
        # Tenta fazer o parse
        # strptime("%H:%M") espera horas como "00"-"23" e minutos "00"-"59".
        # Se a regex permitir "H:MM", strptime falhará para horas de um dígito sem zero à esquerda.
        # No entanto, o placeholder e a ajuda sugerem "HH:MM", então o comportamento atual está ok.
        time_obj = datetime.strptime(hora_str, "%H:%M")
        
        # Validação adicional dos valores (pode ser redundante se strptime for bem-sucedido, mas não prejudica)
        parts = hora_str.split(':')
        if len(parts) != 2: # Já coberto pelo regex e strptime, mas para segurança.
            return False
            
        hour = int(parts[0])
        minute = int(parts[1])
        
        # Verifica se hora e minuto estão em ranges válidos
        if hour < 0 or hour > 23:
            return False
        if minute < 0 or minute > 59:
            return False
            
        return True
    except (ValueError, IndexError):
        return False

def time_input_native(label: str, key: str) -> str:
    """Input de hora usando apenas Streamlit nativo"""
    value = st.text_input(
        label, 
        key=key,
        placeholder="HH:MM (ex: 12:45)",
        help="Digite no formato HH:MM. Exemplos: 08:30, 14:25, 09:15"
    )
    return value.strip() if value else ""

# [Todas as outras funções permanecem iguais - obter_localizacao, criar_botao_copiar, etc.]

def obter_localizacao():
    """Função para obter localização em tempo real com alta precisão"""
    html_code = """
    <div style="padding: 15px; border: 2px solid #0066cc; border-radius: 10px; margin: 15px 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);">
        <h4 style="margin-top: 0; color: #0066cc;">📍 Obter Localização de Alta Precisão</h4>
        
        <div style="margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
            <button onclick="getHighPrecisionLocation()" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.37);
                flex: 1 1 auto;
                min-width: 180px;
                text-align: center;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🎯 Localização de Alta Precisão
            </button>
            
            <button onclick="getQuickLocation()" style="
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 4px 15px 0 rgba(76, 175, 80, 0.37);
                flex: 1 1 auto;
                min-width: 180px;
                text-align: center;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                ⚡ Localização Rápida
            </button>
            
            <button onclick="clearLocation()" style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 4px 15px 0 rgba(245, 87, 108, 0.37);
                flex: 1 1 auto;
                min-width: 120px;
                text-align: center;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🗑️ Limpar
            </button>
        </div>
        
        <div id="status" style="margin-top: 15px; font-weight: bold; font-size: 14px;"></div>
        <div id="coordinates" style="margin-top: 15px; display: none;"></div>
        
    </div>

    <script>
    let currentCoords = null;
    let watchId = null;
    let bestAccuracy = Infinity;
    let attempts = 0;
    let maxAttempts = 10;
    
    function getHighPrecisionLocation() {
        const status = document.getElementById("status");
        const coordinates = document.getElementById("coordinates");
        
        if (!navigator.geolocation) {
            status.innerHTML = "❌ Geolocalização não é suportada por este navegador.";
            status.style.color = "#dc3545";
            return;
        }
        
        bestAccuracy = Infinity;
        attempts = 0;
        currentCoords = null;
        
        status.innerHTML = "🎯 Iniciando localização de alta precisão... Aguarde até 60 segundos.";
        status.style.color = "#007bff";
        coordinates.style.display = "none";
        
        watchId = navigator.geolocation.watchPosition(
            function(position) {
                attempts++;
                const accuracy = position.coords.accuracy;
                
                status.innerHTML = `🔄 Tentativa ${attempts}/${maxAttempts} - Precisão: ±${Math.round(accuracy)}m`;
                
                if (accuracy < bestAccuracy && (accuracy < 10 || attempts >= maxAttempts)) {
                    bestAccuracy = accuracy;
                    processPosition(position, true);
                    if (watchId) navigator.geolocation.clearWatch(watchId);
                    watchId = null;
                } else if (attempts >= maxAttempts) {
                    processPosition(position, true);
                    if (watchId) navigator.geolocation.clearWatch(watchId);
                    watchId = null;
                }
            },
            handleLocationError,
            {
                enableHighAccuracy: true,
                timeout: 60000,
                maximumAge: 0
            }
        );
        
        setTimeout(() => {
            if (watchId) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
                if (currentCoords) { 
                    status.innerHTML = `✅ Localização obtida! (Melhor esforço após timeout)`;
                } else {
                    status.innerHTML = "⏰ Tempo limite. Tente em área mais aberta ou use localização rápida.";
                    status.style.color = "#ff9800";
                }
            }
        }, 60000);
    }
    
    function getQuickLocation() {
        const status = document.getElementById("status");
        
        if (!navigator.geolocation) {
            status.innerHTML = "❌ Geolocalização não é suportada por este navegador.";
            status.style.color = "#dc3545";
            return;
        }
        
        status.innerHTML = "⚡ Obtendo localização rápida...";
        status.style.color = "#28a745";
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                processPosition(position, false);
            },
            handleLocationError,
            {
                enableHighAccuracy: true, 
                timeout: 15000, 
                maximumAge: 60000 
            }
        );
    }
    
    function processPosition(position, isHighPrecision) {
        const status = document.getElementById("status");
        const coordinates = document.getElementById("coordinates");
        
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        const accuracy = position.coords.accuracy;
        const timestamp = new Date(position.timestamp);
        
        currentCoords = {
            lat: lat.toFixed(8),
            lng: lng.toFixed(8),
            formatted: `${lat.toFixed(8)}, ${lng.toFixed(8)}`,
            accuracy: accuracy
        };
        
        let precisionLevel = "";
        let precisionColor = "";
        
        if (accuracy <= 5) {
            precisionLevel = "🎯 EXCELENTE";
            precisionColor = "#28a745";
        } else if (accuracy <= 10) {
            precisionLevel = "✅ MUITO BOA";
            precisionColor = "#28a745";
        } else if (accuracy <= 50) {
            precisionLevel = "👍 BOA";
            precisionColor = "#ffc107";
        } else if (accuracy <= 100) {
            precisionLevel = "⚠️ REGULAR";
            precisionColor = "#ff9800";
        } else {
            precisionLevel = "❌ BAIXA";
            precisionColor = "#dc3545";
        }
        
        status.innerHTML = `✅ Localização obtida! Nível: ${precisionLevel} (±${Math.round(accuracy)}m)`;
        status.style.color = precisionColor;
        
        coordinates.innerHTML = `
            <div style="
                background: rgba(255,255,255,0.95); 
                padding: 20px; 
                border-radius: 12px; 
                border-left: 5px solid ${precisionColor};
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                margin-top: 15px;
            ">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">📍 LATITUDE</div>
                        <div style="font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; color: #333;">${lat.toFixed(8)}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">📍 LONGITUDE</div>
                        <div style="font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; color: #333;">${lng.toFixed(8)}</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <button id="gpsCopyCoordsButton" onclick="copyCoords()" style="
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        border: none;
                        padding: 12px 16px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
                        transition: all 0.3s;
                    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        📋 Copiar Coordenadas
                    </button>
                    
                    <button onclick="openMaps()" style="
                        background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
                        color: white;
                        border: none;
                        padding: 12px 16px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                        box-shadow: 0 4px 12px rgba(111, 66, 193, 0.3);
                        transition: all 0.3s;
                    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        🗺️ Ver no Mapa
                    </button>
                </div>
            </div>
        `;
        
        coordinates.style.display = "block";
        
        sessionStorage.setItem('gps_coords', currentCoords.formatted);
        sessionStorage.setItem('gps_accuracy', accuracy.toString());
        sessionStorage.setItem('gps_timestamp', timestamp.toISOString());
    }
    
    function handleLocationError(error) {
        const status = document.getElementById("status");
        const coordinates = document.getElementById("coordinates"); 
        
        let errorMsg = "";
        let suggestions = "";
        
        switch(error.code) {
            case error.PERMISSION_DENIED:
                errorMsg = "❌ Acesso à localização negado.";
                suggestions = "💡 Permita acesso nas configurações do navegador.";
                break;
            case error.POSITION_UNAVAILABLE:
                errorMsg = "❌ Localização não disponível.";
                suggestions = "💡 Verifique se GPS está ativo e tente ao ar livre.";
                break;
            case error.TIMEOUT:
                errorMsg = "❌ Tempo limite excedido.";
                suggestions = "💡 Tente localização rápida ou mova para área aberta.";
                break;
            default:
                errorMsg = "❌ Erro desconhecido ao obter localização.";
                suggestions = "💡 Recarregue a página e tente novamente.";
                break;
        }
        
        status.innerHTML = errorMsg + "<br><span style='font-size: 12px; color: #777;'>" + suggestions + "</span>";
        status.style.color = "#dc3545";
        if (coordinates) { 
            coordinates.style.display = "none";
        }
    }
    
    function copyCoords() {
        if (!currentCoords || !currentCoords.formatted) {
            const status = document.getElementById("status");
            if (status) {
                const originalStatusText = status.innerHTML;
                const originalStatusColor = status.style.color;
                status.innerHTML = "📋 Nenhuma coordenada para copiar. Obtenha a localização primeiro.";
                status.style.color = "#ff9800";
                setTimeout(() => {
                    if (status.innerHTML === "📋 Nenhuma coordenada para copiar. Obtenha a localização primeiro.") {
                        status.innerHTML = originalStatusText;
                        status.style.color = originalStatusColor;
                    }
                }, 3000);
            }
            return;
        }

        const textToCopy = currentCoords.formatted;
        const copyButton = document.getElementById("gpsCopyCoordsButton");
        
        let originalButtonText = "📋 Copiar Coordenadas";
        let originalButtonStyleBackground = "linear-gradient(135deg, #28a745 0%, #20c997 100%)"; 

        if (copyButton) {
            originalButtonText = copyButton.innerHTML;
            originalButtonStyleBackground = copyButton.style.background || originalButtonStyleBackground;
        }

        function showSuccessFeedback() {
            if (copyButton) {
                copyButton.innerHTML = "✅ Copiado!";
                copyButton.style.background = "linear-gradient(135deg, #17a2b8 0%, #138496 100%)"; 
                setTimeout(() => {
                    copyButton.innerHTML = originalButtonText;
                    copyButton.style.background = originalButtonStyleBackground;
                }, 2000);
            } else { 
                const statusDiv = document.getElementById("status");
                if (statusDiv) {
                    const prevStatus = statusDiv.innerHTML;
                    const prevColor = statusDiv.style.color;
                    statusDiv.innerHTML = "✅ Coordenadas copiadas!";
                    statusDiv.style.color = "#17a2b8"; 
                    setTimeout(() => {
                        statusDiv.innerHTML = prevStatus;
                        statusDiv.style.color = prevColor;
                    }, 2000);
                }
            }
        }

        function showFailureFeedback(usePrompt = true) {
            if (copyButton) {
                copyButton.innerHTML = "❌ Falha ao copiar";
                copyButton.style.background = "linear-gradient(135deg, #dc3545 0%, #c82333 100%)"; 
                setTimeout(() => {
                    copyButton.innerHTML = originalButtonText;
                    copyButton.style.background = originalButtonStyleBackground;
                }, 3000);
            }
            if (usePrompt) {
                prompt('Não foi possível copiar automaticamente. Copie manualmente:', textToCopy);
            }
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(textToCopy).then(
                () => { 
                    showSuccessFeedback();
                },
                (err) => { 
                    console.warn('navigator.clipboard.writeText falhou, tentando fallback execCommand: ', err);
                    fallbackCopy();
                }
            );
        } else {
            console.warn('navigator.clipboard não disponível, usando fallback execCommand.');
            fallbackCopy();
        }

        function fallbackCopy() {
            const textArea = document.createElement("textarea");
            textArea.value = textToCopy;
            textArea.style.position = "fixed"; 
            textArea.style.top = "-9999px";
            textArea.style.left = "-9999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showSuccessFeedback();
                } else {
                    console.error('Fallback execCommand falhou em copiar.');
                    showFailureFeedback(true); 
                }
            } catch (err) {
                console.error('Erro crítico no fallback execCommand: ', err);
                showFailureFeedback(true); 
            }
            document.body.removeChild(textArea);
        }
    }
    
    function openMaps() {
        if (currentCoords && currentCoords.lat && currentCoords.lng) {
            // CORRIGIDO: Usar template literals do JavaScript e URL válida do Google Maps
            const mapsUrl = `https://maps.google.com/?q=${currentCoords.lat},${currentCoords.lng}`;
            window.open(mapsUrl, '_blank');
        } else {
             const status = document.getElementById("status");
            if(status) { 
                const originalStatusText = status.innerHTML;
                const originalStatusColor = status.style.color;
                status.innerHTML = "🗺️ Nenhuma coordenada para ver no mapa. Obtenha a localização primeiro.";
                status.style.color = "#ff9800"; 
                setTimeout(() => {
                    if (status.innerHTML === "🗺️ Nenhuma coordenada para ver no mapa. Obtenha a localização primeiro.") {
                        status.innerHTML = originalStatusText;
                        status.style.color = originalStatusColor;
                    }
                }, 3000);
            }
        }
    }
    
    function clearLocation() {
        if (watchId) {
            navigator.geolocation.clearWatch(watchId);
            watchId = null;
        }
        const statusDiv = document.getElementById("status");
        const coordinatesDiv = document.getElementById("coordinates");

        if (statusDiv) statusDiv.innerHTML = "🗑️ Localização limpa.";
        if (coordinatesDiv) coordinatesDiv.style.display = "none";
        
        currentCoords = null;
        bestAccuracy = Infinity;
        attempts = 0;
        
        sessionStorage.removeItem('gps_coords');
        sessionStorage.removeItem('gps_accuracy');
        sessionStorage.removeItem('gps_timestamp');

        setTimeout(() => {
            if (statusDiv && statusDiv.innerHTML === "🗑️ Localização limpa.") {
                statusDiv.innerHTML = "";
            }
        }, 2000);
    }
    </script>
    """
    
    components.html(html_code, height=450) 

def criar_botao_copiar(texto):
    texto_escapado = texto.replace('`', '\\`').replace('"', '\\"').replace("'", "\\'")
    unique_id_suffix = ''.join(filter(str.isalnum, texto_escapado[:20])) 

    button_html = f"""
    <div style="margin: 10px 0;">
        <button 
            id="customCopyButton_{unique_id_suffix}"
            onclick="copyToClipboard_{unique_id_suffix}()" 
            style="
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(238, 90, 36, 0.4);
            "
            onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(238, 90, 36, 0.6)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(238, 90, 36, 0.4)'"
        >
            📋 Copiar Texto Completo
        </button>
    </div>
    
    <script>
    if (typeof copyToClipboard_{unique_id_suffix} !== 'function') {{
        function copyToClipboard_{unique_id_suffix}() {{
            const textToCopy = `{texto_escapado}`;
            const button = document.getElementById("customCopyButton_{unique_id_suffix}");
            const originalButtonText = button.innerHTML;
            const originalButtonStyleBackground = button.style.background;

            function showSuccessOnButton() {{
                button.innerHTML = '✅ Texto Copiado!';
                button.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'; 
                setTimeout(function() {{
                    button.innerHTML = originalButtonText;
                    button.style.background = originalButtonStyleBackground;
                }}, 2000);
            }}

            function showFailureOnButton(usePrompt = true) {{
                button.innerHTML = '❌ Falha ao Copiar';
                button.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)'; 
                setTimeout(function() {{
                    button.innerHTML = originalButtonText;
                    button.style.background = originalButtonStyleBackground;
                }}, 3000);
                if (usePrompt) {{
                    prompt("Falha ao copiar. Por favor, copie manualmente:", textToCopy);
                }}
            }}

            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(textToCopy).then(
                    showSuccessOnButton,
                    function(err) {{ 
                        console.warn('navigator.clipboard.writeText falhou, tentando fallback: ', err);
                        fallbackCopyToClipboardInternal();
                    }}
                );
            }} else {{ 
                console.warn('navigator.clipboard não disponível, usando fallback.');
                fallbackCopyToClipboardInternal();
            }}

            function fallbackCopyToClipboardInternal() {{
                const textArea = document.createElement("textarea");
                textArea.value = textToCopy;
                textArea.style.position = "fixed";  
                textArea.style.top = "-9999px";    
                textArea.style.left = "-9999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {{
                    const successful = document.execCommand('copy');
                    if (successful) {{
                        showSuccessOnButton();
                    }} else {{
                        console.error('Fallback execCommand falhou em copiar.');
                        showFailureOnButton(true);
                    }}
                }} catch (err) {{
                    console.error('Erro crítico no fallback execCommand: ', err);
                    showFailureOnButton(true);
                }}
                document.body.removeChild(textArea);
            }}
        }}
    }}
    </script>
    """
    
    components.html(button_html, height=80)

def refinar_texto_com_openai(texto):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # ou outro modelo que preferir
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
            max_tokens=2000, # Ajuste conforme necessário
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao conectar com OpenAI: {str(e)}")
        return texto # Retorna o texto original em caso de erro

def gerar_historico(dados):
    # Template permanece o mesmo
    template = f"""Em atendimento à Ordem de Serviço, vinculada ao Programa de Segurança Rural no Vale do Jamari, foi realizada uma visita técnica em {dados['data']}, com início às {dados['hora_inicio']} e término às {dados['hora_fim']}. A diligência ocorreu na propriedade rural denominada {dados['tipo_propriedade']} "{dados['nome_propriedade']}", situada em {dados['endereco']}, na Zona Rural do município de {dados['municipio']}/{dados['uf']}. Procedeu-se ao levantamento das coordenadas geográficas, sendo a porteira de acesso principal localizada em {dados['lat_long_porteira']}, e a sede/residência principal em {dados['lat_long_sede']}. A área total da propriedade compreende {dados['area']} {dados['unidade_area']}. O proprietário, Sr. "{dados['nome_proprietario']}", inscrito no CPF/CNPJ sob o nº "{dados['cpf_cnpj']}", com contato telefônico principal "{dados['telefone']}", esteve presente durante a visita. A principal atividade econômica desenvolvida no local é "{dados['atividade_principal']}"."""
    if dados['veiculos']:
        template += f" Foram identificados os seguintes veículos automotores na propriedade: {dados['veiculos']}."
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
    
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("⚠️ API Key da OpenAI não configurada! Configure no arquivo .streamlit/secrets.toml")
        st.stop()
    
    with st.sidebar:
        st.header("📋 Instruções")
        st.write("1. **📍 Localização**: Use os botões '🎯 Alta Precisão' ou '⚡ Rápida' para obter coordenadas GPS.")
        st.write("2. Preencha todos os campos obrigatórios.")
        st.write("3. Para as horas, use o formato HH:MM (ex: 08:30, 14:00).")
        st.write("4. Campos opcionais: veículos e marca de gado.")
        st.write("5. Clique em '🚀 Gerar Histórico'.")
        st.write("6. O texto será refinado automaticamente pela IA.")
        st.write("7. Use o botão '📋 Copiar Texto Completo' ou '💾 Baixar como TXT'.")
        
        st.header("🔧 Dicas de Precisão GPS")
        st.write("📱 **No celular**: Permita acesso à localização quando solicitado pelo navegador.")
        st.write("🌍 **GPS**: Funciona melhor ao ar livre com visão clara do céu.")
        st.write("⏰ **Paciência**: A 'Alta Precisão' pode levar até 60 segundos.")
        st.write("📍 **Posição**: Mantenha o dispositivo relativamente parado durante a captura para melhor precisão.")
        st.write("🔒 **HTTPS**: A geolocalização do navegador geralmente requer conexão segura (HTTPS).")
        
        debug_mode = st.checkbox("🐛 Modo Debug", key="debug_mode_checkbox")
    
    with st.form("formulario_historico"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("📅 Dados da Visita")
            data_visita = st.date_input("Data da visita", key="data_visita_input")
            
            hora_inicio_str = time_input_native("Hora de início", key="comp_hora_inicio")
            hora_fim_str = time_input_native("Hora de término", key="comp_hora_fim")
            
            if debug_mode: # Debug inicial dos valores capturados do input nativo
                st.write(f"🐛 Debug Input - Hora início (raw): '{hora_inicio_str}'")
                st.write(f"🐛 Debug Input - Hora fim (raw): '{hora_fim_str}'")
            
            st.header("🏠 Dados da Propriedade")
            tipo_propriedade = st.selectbox("Tipo de propriedade", ["Sítio", "Fazenda", "Chácara", "Estância"], key="tipo_prop_sel")
            nome_propriedade = st.text_input("Nome da propriedade", placeholder="Ex: São José", key="nome_prop_text")
            endereco = st.text_area("Endereço completo", placeholder="Inclua referências se houver", key="endereco_text_area")
            municipio = st.text_input("Município", key="municipio_text")
            uf = st.selectbox("UF", ["RO", "AC", "AM", "RR", "PA", "TO", "MT", "MS", "GO", "DF"], key="uf_sel")
            
        with col2:
            st.header("📍 Coordenadas GPS")
            obter_localizacao() # Componente HTML para GPS
            
            lat_long_porteira = st.text_input("Coordenadas da porteira (Lat, Long)", key="lat_long_porteira_input", placeholder="Ex: -9.897289, -63.017788")
            lat_long_sede = st.text_input("Coordenadas da sede (Lat, Long)", key="lat_long_sede_input", placeholder="Ex: -9.897500, -63.017900")
            
            st.header("📏 Área e Proprietário")
            area = st.number_input("Área da propriedade", min_value=0.01, step=0.1, format="%.2f", key="area_num_input")
            unidade_area = st.selectbox("Unidade", ["hectares", "alqueires"], key="unidade_area_sel")
            nome_proprietario = st.text_input("Nome do proprietário", key="nome_proprietario_text")
            cpf_cnpj = st.text_input("CPF/CNPJ", placeholder="000.000.000-00 ou 00.000.000/0000-00", key="cpf_cnpj_text")
            telefone = st.text_input("Telefone", placeholder="(69) 99999-9999", key="telefone_text")
        
        st.header("💼 Atividade Econômica")
        atividade_principal = st.text_input("Atividade principal", placeholder="Ex: Criação de bovinos", key="atividade_text")
        
        st.header("🚗 Veículos (Opcional)")
        veiculos = st.text_area("Descrição dos veículos", 
                               placeholder="Ex: uma caminhonete marca Ford, modelo Ranger, placa ABC-1234, cor Prata; um trator marca Massey Ferguson, modelo 265, sem placa, cor Vermelha", key="veiculos_text_area")
        
        st.header("🐄 Rebanho")
        marca_gado = st.text_input("Marca/sinal/ferro registrado (Opcional)", 
                                  placeholder="Ex: JB na paleta esquerda", key="marca_gado_text")
        
        st.header("🏷️ Placa de Identificação")
        numero_placa = st.text_input("Número da placa", placeholder="Ex: PSR-001", key="numero_placa_text")
        
        submitted = st.form_submit_button("🚀 Gerar Histórico", use_container_width=True)
    
    if submitted:
        hora_inicio_val_final = hora_inicio_str # Já é .strip() pela função time_input_native
        hora_fim_val_final = hora_fim_str       # Já é .strip() pela função time_input_native

        if debug_mode:
            st.write("### 🐛 Debug Detalhado (Após Submit, Antes da Validação)")
            st.write(f"Hora início (para validação): '{hora_inicio_val_final}', Tipo: {type(hora_inicio_val_final)}, Len: {len(hora_inicio_val_final if hora_inicio_val_final else '')}")
            st.write(f"Hora fim (para validação): '{hora_fim_val_final}', Tipo: {type(hora_fim_val_final)}, Len: {len(hora_fim_val_final if hora_fim_val_final else '')}")
            
            # Teste regex individual corrigido
            if hora_inicio_val_final:
                match_inicio_debug = re.match(r'^\d{1,2}:\d{2}$', hora_inicio_val_final)
                st.write(f"🐛 Debug Regex match início ('{hora_inicio_val_final}'): {match_inicio_debug is not None}")
            else:
                st.write(f"🐛 Debug Regex match início: String vazia, não testado.")
            
            if hora_fim_val_final:
                match_fim_debug = re.match(r'^\d{1,2}:\d{2}$', hora_fim_val_final)
                st.write(f"🐛 Debug Regex match fim ('{hora_fim_val_final}'): {match_fim_debug is not None}")
            else:
                st.write(f"🐛 Debug Regex match fim: String vazia, não testado.")

        campos_obrigatorios_dict = {
            "Data da visita": data_visita,
            "Hora de início": hora_inicio_val_final, 
            "Hora de término": hora_fim_val_final,   
            "Nome da propriedade": nome_propriedade,
            "Endereço completo": endereco,
            "Município": municipio,
            "Coordenadas da porteira": lat_long_porteira,
            "Coordenadas da sede": lat_long_sede,
            "Área da propriedade": area, 
            "Nome do proprietário": nome_proprietario,
            "CPF/CNPJ": cpf_cnpj,
            "Telefone": telefone,
            "Atividade principal": atividade_principal,
            "Número da placa": numero_placa
        }
        
        campos_vazios_nomes = []
        for nome, valor in campos_obrigatorios_dict.items():
            if isinstance(valor, str) and not valor.strip(): # Checa strings vazias ou só com espaços
                campos_vazios_nomes.append(nome)
            elif valor is None: # Checa None para campos não-string (como data_visita, area)
                 if nome == "Área da propriedade" and (area is None or area <=0) : 
                     if nome not in campos_vazios_nomes: campos_vazios_nomes.append(nome + " (deve ser > 0)")
                 elif nome != "Área da propriedade": 
                     campos_vazios_nomes.append(nome)
        
        if area is None or area <= 0: # Garantir que a área seja validada mesmo se não for None, mas <=0
            if "Área da propriedade (deve ser > 0)" not in campos_vazios_nomes and \
               "Área da propriedade" not in campos_vazios_nomes :
                 campos_vazios_nomes.append("Área da propriedade (deve ser > 0)")

        erros_formato_hora = []
        if not hora_inicio_val_final: # Adicionado para checar se o campo obrigatório de hora está vazio
            if "Hora de início" not in campos_vazios_nomes: campos_vazios_nomes.append("Hora de início")
        elif not validar_formato_hora_strptime(hora_inicio_val_final):
            erros_formato_hora.append("Hora de início")
        
        if not hora_fim_val_final: # Adicionado para checar se o campo obrigatório de hora está vazio
            if "Hora de término" not in campos_vazios_nomes: campos_vazios_nomes.append("Hora de término")
        elif not validar_formato_hora_strptime(hora_fim_val_final):
            erros_formato_hora.append("Hora de término")

        if campos_vazios_nomes:
            # Remover duplicatas e ordenar para mensagem de erro clara
            unique_campos_vazios = sorted(list(set(campos_vazios_nomes)))
            st.error(f"❌ Por favor, preencha todos os campos obrigatórios: {', '.join(unique_campos_vazios)}!")
        elif erros_formato_hora:
            st.error(f"❌ Formato de hora inválido para: {', '.join(erros_formato_hora)}. Use o formato HH:MM e valores válidos (ex: 08:30).")
            if debug_mode:
                st.error(f"🐛 Debug Valores Hora para Validação - Início: '{hora_inicio_val_final}', Fim: '{hora_fim_val_final}'")
        else:
            dados = {
                'data': data_visita.strftime("%d/%m/%Y"),
                'hora_inicio': hora_inicio_val_final, 
                'hora_fim': hora_fim_val_final,     
                'tipo_propriedade': tipo_propriedade,
                'nome_propriedade': nome_propriedade,
                'endereco': endereco,
                'municipio': municipio,
                'uf': uf,
                'lat_long_porteira': lat_long_porteira,
                'lat_long_sede': lat_long_sede,
                'area': f"{area:.2f}", 
                'unidade_area': unidade_area,
                'nome_proprietario': nome_proprietario,
                'cpf_cnpj': cpf_cnpj,
                'telefone': telefone,
                'atividade_principal': atividade_principal,
                'veiculos': veiculos if veiculos.strip() else "", # Garante que não passe só espaços
                'marca_gado': marca_gado if marca_gado.strip() else "", # Garante que não passe só espaços
                'numero_placa': numero_placa
            }
           
            with st.spinner("🔄 Gerando histórico..."):
                historico_bruto = gerar_historico(dados)
           
            with st.spinner("✨ Refinando texto com IA..."):
                historico_refinado = refinar_texto_com_openai(historico_bruto)
           
            st.success("✅ Histórico gerado com sucesso!")
           
            st.header("📄 Histórico Final")
            st.text_area("Texto gerado:", value=historico_refinado, height=400, key="historico_final_text_area_display_unique", disabled=True) 
                       
            col_copy, col_download = st.columns(2)
           
            with col_copy:
                criar_botao_copiar(historico_refinado)
           
            with col_download:
                st.download_button(
                    label="💾 Baixar como TXT",
                    data=historico_refinado,
                    file_name=f"historico_policial_{data_visita.strftime('%Y%m%d')}_{nome_propriedade.replace(' ','_') if nome_propriedade else 'desconhecido'}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()