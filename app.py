import streamlit as st
from data_processor import DataProcessorPPTX
from pptx_updater import PPTXUpdater

st.set_page_config(page_title="Automação Relatórios ITS", layout="wide", page_icon="📊")

st.title("📊 Atualizador Automático de PPTX (Julho -> Agosto)")
st.write("Insira as bases de Agosto para atualizar o template de Julho da ilha selecionada.")

# Barra lateral para upload das bases
with st.sidebar:
    st.header("Bases de Dados (Agosto)")
    file_monit = st.file_uploader("Monitorias (.xlsx)", type=['xlsx'])
    file_detalhes = st.file_uploader("Detalhes de Avaliação (.csv)", type=['csv'])
    file_abonos = st.file_uploader("Abonos (.csv)", type=['csv'])
    file_mope = st.file_uploader("Mope (.xlsx)", type=['xlsx'])

# Parâmetros de negócio
col1, col2 = st.columns(2)
with col1:
    operacao = st.selectbox("Selecione a Operação", ["Voz", "Digital"])
with col2:
    ilha_alvo = st.selectbox("Selecione a Ilha (Aba PPT)", ["Serasa Premium", "CRC", "Cadastro Positivo", "Reclame Aqui"])

st.markdown("---")

# Ação de geração
if st.button("Gerar Apresentação de Agosto", type="primary", use_container_width=True):
    # Valida se os 4 arquivos foram upados
    if not all([file_monit, file_detalhes, file_abonos, file_mope]):
        st.warning("⚠️ Faça o upload das 4 bases de dados na barra lateral antes de gerar.")
    else:
        with st.spinner("1. Lendo bases de dados e cruzando Mope com Monitorias..."):
            try:
                # Inicia processamento Pandas
                processor = DataProcessorPPTX(file_monit, file_detalhes, file_abonos, file_mope)
                
                # Exemplo: Calcula KPIs de Agosto (Mês 8)
                dados_visao = processor.gerar_visao_geral(ilha=ilha_alvo, mes_atual_num=8)
                
                # Seleciona o template correspondente de Julho
                template_file = "templates/Weekly Julho final - VOZ.pptx" if operacao == "Voz" else "templates/Weekly Julho final - DIGITAL.pptx"
                
                st.spinner("2. Injetando novos dados no PowerPoint...")
                updater = PPTXUpdater(template_file)
                
                # -------------------------------------------------------------
                # INJEÇÃO NO SLIDE DE VISÃO GERAL (Exemplo: Ilha Serasa Premium)
                # OBS: Estes são os nomes internos das caixas de texto no seu PPTX
                # Mapeados da sua apresentação "Premium"
                # -------------------------------------------------------------
                # No seu slide de Visão Geral:
                # CaixaDeTexto 30 é o 'Volume de Monitorias'
                # CaixaDeTexto 36 é a 'Média Do Mês'
                # CaixaDeTexto 47 é o 'Volume de Feedback'
                
                # Atenção: Ajuste o índice do slide dependendo da ilha selecionada.
                # Premium é o slide índice 3 (quarto slide)
                slide_visao_geral_premium = 3 
                
                updater.atualizar_texto_por_nome(slide_visao_geral_premium, 'CaixaDeTexto 30', dados_visao['Volume Total'])
                updater.atualizar_texto_por_nome(slide_visao_geral_premium, 'CaixaDeTexto 36', dados_visao['Média Geral'])
                updater.atualizar_texto_por_nome(slide_visao_geral_premium, 'CaixaDeTexto 47', dados_visao['Volume Feedbacks'])
                
                # Prepara arquivo gerado
                ppt_pronto = updater.obter_arquivo_em_memoria()
                
                st.success(f"✅ Relatório de Agosto gerado com sucesso para a ilha {ilha_alvo} ({operacao})!")
                st.info("Os comentários qualitativos da qualidade foram preservados no template original.")
                
                # Botão de download
                st.download_button(
                    label="📥 Fazer Download da Apresentação",
                    data=ppt_pronto,
                    file_name=f"Resultados_{ilha_alvo}_Agosto.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )

            except Exception as e:
                st.error(f"❌ Ocorreu um erro no cruzamento das planilhas: {e}")
                st.error("Verifique se as colunas 'Operador' (Monitorias) e 'NOME' (Mope) existem nos arquivos enviados.")