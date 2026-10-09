import pandas as pd
import numpy as np

class DataProcessorPPTX:
    def __init__(self, file_monit, file_detalhes, file_abonos, file_mope):
        """Inicializa o processador, faz leitura e merge básico."""
        # Lê os arquivos do Streamlit (em memória)
        self.df_monit = pd.read_excel(file_monit)
        self.df_detalhes = pd.read_csv(file_detalhes)
        # O Mope lê a aba específica 'MAPA' que você mencionou
        self.df_mope = pd.read_excel(file_mope, sheet_name='MAPA') 
        self.df_abonos = pd.read_csv(file_abonos)
        
        # Garante o formato de data
        self.df_monit['Data do Atendimento'] = pd.to_datetime(self.df_monit['Data do Atendimento'], errors='coerce')
        
        # Enriquecimento: Une Monitoria com Mope (Assumindo que a chave de cruzamento seja NOME ou MATRICULA do Operador)
        # Atenção: Ajuste 'Operador' e 'NOME' se os nomes das colunas forem diferentes nos seus arquivos reais
        self.df_base = pd.merge(self.df_monit, self.df_mope, left_on='Operador', right_on='NOME', how='left')

    def _filtrar_por_ilha_e_mes(self, ilha, mes):
        """Filtra o dataframe mestre pela Ilha e pelo Mês numérico (ex: 8 para Agosto)"""
        mask_ilha = self.df_base['Ilha'] == ilha
        mask_mes = self.df_base['Data do Atendimento'].dt.month == mes
        return self.df_base[mask_ilha & mask_mes]

    def gerar_visao_geral(self, ilha, mes_atual_num):
        """Gera dicionário com Volume Total, Média Geral e Volume Feedbacks."""
        df_atual = self._filtrar_por_ilha_e_mes(ilha, mes_atual_num)
        
        if df_atual.empty:
            return {"Volume Total": "0", "Média Geral": "0.00", "Volume Feedbacks": "0"}

        volume_total = len(df_atual)
        
        # Calcula a média se existir a coluna 'Nota'
        media_geral = df_atual['Nota'].mean() if 'Nota' in df_atual else 0.0
        
        # Lógica simplificada de Feedbacks (Ajustar de acordo com sua regra de justificados/abonos)
        volume_feedbacks = volume_total 

        return {
            "Volume Total": str(volume_total),
            "Média Geral": f"{media_geral:.2f}".replace('.', ','), # PPTX br costuma usar vírgula
            "Volume Feedbacks": str(volume_feedbacks)
        }
    
    # As funções gerar_pontos_ofensores() e gerar_ranking_evolutivo() entram aqui.
    # Elas seguem a lógica que elaboramos na primeira resposta.