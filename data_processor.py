import pandas as pd
import numpy as np

class DataProcessorPPTX:
    def __init__(self, file_monit, file_detalhes, file_abonos, file_mope):
        # 1. Leitura forçando o formato correto para arquivos br (ponto e vírgula e acentuação)
        self.df_monit = pd.read_excel(file_monit)
        self.df_mope = pd.read_excel(file_mope, sheet_name='MAPA') 
        self.df_detalhes = pd.read_csv(file_detalhes, sep=';', encoding='utf-8-sig', low_memory=False)
        self.df_abonos = pd.read_csv(file_abonos, sep=';', encoding='utf-8-sig', low_memory=False)
        
        # 2. CORREÇÃO DA DATA: Na sua planilha real o nome é "Data Atendimento"
        self.df_monit['Data Atendimento'] = pd.to_datetime(self.df_monit['Data Atendimento'], errors='coerce')
        
        # 3. CORREÇÃO DO MOPE: A coluna de cruzamento é "Nome" (primeira letra maiúscula)
        self.df_base = pd.merge(self.df_monit, self.df_mope, left_on='Operador', right_on='Nome', how='left')

    def _filtrar_por_ilha_e_mes(self, ilha, mes):
        """Filtra o dataframe master cruzando a seleção com a coluna 'Produto'"""
        # Ajusta a busca pois a opção "Serasa Premium" aparece como "Serasa - 0800 Premium" na base
        ilha_busca = "Premium" if ilha == "Serasa Premium" else ilha
        
        # 4. CORREÇÃO DO FILTRO: Usamos 'Produto' porque a coluna 'Ilha' não existe no Mope
        mask_ilha = self.df_base['Produto'].str.contains(ilha_busca, case=False, na=False)
        mask_mes = self.df_base['Data Atendimento'].dt.month == mes
        
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
