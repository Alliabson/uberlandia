import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import re
import requests
import io
from typing import Optional, Dict
import tempfile
import os
from fpdf import FPDF
import time




def login():
    # Centralizar manualmente o login
    st.markdown("""
        <style>
            div.block-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 90vh;
            }
            div.css-1v0mbdj.e1g8pov64 {  /* Esse seletor pode mudar conforme a versão */
                max-width: 400px;
                width: 100%;
                margin: auto;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔒 Login no Sistema")
    
    usuario_correto = "hamoa"
    senha_correta = "hamoauberlandia"

    usuario = st.text_input("🔍 Usuário")
    senha = st.text_input("🔐 Senha", type="password")
    
    if st.button("Entrar"):
        if usuario == usuario_correto and senha == senha_correta:
            st.session_state['logado'] = True
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")

if 'logado' not in st.session_state or not st.session_state['logado']:
    login()
    st.stop()
    st.rerun()


# SEMPRE iniciar o app com layout="wide" (não usar centered no começo!)
st.set_page_config(page_title="Sistema Imobiliário - Fichas Cadastrais", layout="wide")

# Configuração do banco de dados
DB_NAME = "celeste.db"

def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela Pessoa Física - Atualizada com campos do cônjuge
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes_pf (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        genero TEXT,
        data_nascimento TEXT,
        celular TEXT NOT NULL,
        cpf TEXT NOT NULL,
        email TEXT,  
        nacionalidade TEXT,
        profissao TEXT,
        estado_civil TEXT,
        regime_casamento TEXT,
        uniao_estavel TEXT,
        cep TEXT,
        endereco TEXT,
        numero TEXT,
        bairro TEXT,
        cidade TEXT,
        estado TEXT,
        nome_conjuge TEXT,
        genero_conjuge TEXT,
        data_nascimento_conjuge TEXT,
        cpf_conjuge TEXT,
        email_conjuge TEXT,  
        celular_conjuge TEXT,
        nacionalidade_conjuge TEXT,
        profissao_conjuge TEXT,
        estado_civil_conjuge TEXT,
        regime_casamento_conjuge TEXT,
        uniao_estavel_conjuge TEXT,
        cep_conjuge TEXT,
        endereco_conjuge TEXT,
        numero_conjuge TEXT,
        bairro_conjuge TEXT,
        cidade_conjuge TEXT,
        estado_conjuge TEXT,
        data_cadastro TEXT,
        corretor TEXT,
        imobiliaria TEXT,
        numero_negocio TEXT
    )
    ''')
    
    # Tabela Pessoa Jurídica - Corrigida (removidas colunas duplicadas)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes_pj (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT NOT NULL,
        cnpj TEXT NOT NULL,
        email TEXT,
        telefone_empresa TEXT,
        cep_empresa TEXT,
        endereco_empresa TEXT,
        numero_empresa TEXT,
        bairro_empresa TEXT,
        cidade_empresa TEXT,
        estado_empresa TEXT,
        genero_administrador TEXT,
        nome_administrador TEXT NOT NULL,
        data_nascimento_administrador TEXT,
        cpf_administrador TEXT NOT NULL,
        celular_administrador TEXT NOT NULL,
        email_administrador TEXT,
        nacionalidade_administrador TEXT,
        profissao_administrador TEXT,
        estado_civil_administrador TEXT,
        regime_casamento_administrador TEXT,
        uniao_estavel_administrador TEXT,
        cep_administrador TEXT,
        endereco_administrador TEXT,
        numero_administrador TEXT,
        bairro_administrador TEXT,
        cidade_administrador TEXT,
        estado_administrador TEXT,
        data_cadastro TEXT,
        corretor TEXT,
        imobiliaria TEXT,
        numero_negocio TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# Criar tabelas se não existirem
criar_tabelas()

# Criar tabelas se não existirem
criar_tabelas()

def verificar_e_atualizar_estrutura():
    """Verifica e atualiza a estrutura das tabelas conforme necessário"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Verificar e atualizar tabela clientes_pf
        cursor.execute("PRAGMA table_info(clientes_pf)")
        colunas_pf = [info[1] for info in cursor.fetchall()]
        
        colunas_necessarias_pf = [
            'nome', 'genero', 'data_nascimento', 'celular', 'cpf', 'email',
            'nacionalidade', 'profissao', 'estado_civil', 'regime_casamento',
            'uniao_estavel', 'cep', 'endereco', 'numero', 'bairro', 'cidade',
            'estado', 'nome_conjuge', 'genero_conjuge', 'data_nascimento_conjuge',
            'cpf_conjuge', 'email_conjuge', 'celular_conjuge', 'nacionalidade_conjuge', 
            'profissao_conjuge', 'estado_civil_conjuge', 'regime_casamento_conjuge',
            'uniao_estavel_conjuge', 'cep_conjuge', 'endereco_conjuge',
            'numero_conjuge', 'bairro_conjuge', 'cidade_conjuge',
            'estado_conjuge', 'data_cadastro', 'corretor', 'imobiliaria',
            'numero_negocio'
        ]
        
        for coluna in colunas_necessarias_pf:
            if coluna not in colunas_pf:
                cursor.execute(f'ALTER TABLE clientes_pf ADD COLUMN {coluna} TEXT')
                st.toast(f"Tabela PF: Adicionada coluna {coluna}", icon="🔧")
        
        # Verificar e atualizar tabela clientes_pj
        cursor.execute("PRAGMA table_info(clientes_pj)")
        colunas_pj = [info[1] for info in cursor.fetchall()]
        
        colunas_necessarias_pj = [
            'razao_social', 'cnpj', 'email', 'telefone_empresa', 'cep_empresa',
            'endereco_empresa', 'numero_empresa', 'bairro_empresa',
            'cidade_empresa', 'estado_empresa', 'genero_administrador',
            'nome_administrador', 'data_nascimento_administrador',
            'cpf_administrador', 'celular_administrador', 'email_administrador',
            'nacionalidade_administrador', 'profissao_administrador',
            'estado_civil_administrador', 'regime_casamento_administrador',
            'uniao_estavel_administrador', 'cep_administrador',
            'endereco_administrador', 'numero_administrador',
            'bairro_administrador', 'cidade_administrador',
            'estado_administrador', 'data_cadastro', 'corretor', 'imobiliaria',
            'numero_negocio'
        ]
        
        for coluna in colunas_necessarias_pj:
            if coluna not in colunas_pj:
                cursor.execute(f'ALTER TABLE clientes_pj ADD COLUMN {coluna} TEXT')
                st.toast(f"Tabela PJ: Adicionada coluna {coluna}", icon="🔧")
                
    except Exception as e:
        st.error(f"Erro ao verificar estrutura: {e}")
    finally:
        conn.commit()
        conn.close()


# Funções auxiliares
def formatar_data_ptbr(data):
    """Formata datetime para string dd/mm/yyyy"""
    if pd.isna(data) or data == "" or data is None:
        return ""
    if isinstance(data, str):
        try:
            if re.match(r'\d{2}/\d{2}/\d{4}', data):
                return data
            return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            return data
    return data.strftime('%d/%m/%Y')

def formatar_cpf(cpf: str) -> str:
    """Formata CPF para o padrão 000.000.000-00"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def validar_cpf(cpf: str) -> bool:
    """Valida um CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10:
        digito1 = 0
    
    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10:
        digito2 = 0
    
    return cpf[-2:] == f"{digito1}{digito2}"

def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ para o padrão 00.000.000/0000-00"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

def formatar_telefone(telefone: str) -> str:
    """Formata telefone para o padrão (00) 00000-0000"""
    telefone = re.sub(r'[^0-9]', '', telefone)
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone

def buscar_cep_viacep(cep: str) -> Optional[Dict[str, str]]:
    """Busca CEP usando a API ViaCEP"""
    try:
        cep = re.sub(r'[^0-9]', '', cep)
        if len(cep) != 8:
            return None
        
        url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            dados = response.json()
            if 'erro' not in dados:
                return {
                    'logradouro': dados.get('logradouro', ''),
                    'bairro': dados.get('bairro', ''),
                    'cidade': dados.get('localidade', ''),
                    'estado': dados.get('uf', '')
                }
        return None
    except Exception as e:
        st.warning(f"Erro ao buscar CEP na ViaCEP: {str(e)}")
        return None

def buscar_cep(cep: str) -> Optional[Dict[str, str]]:
    """Busca informações de endereço usando a API ViaCEP"""
    return buscar_cep_viacep(cep)

def preencher_endereco(tipo: str) -> None:
    """Preenche automaticamente os campos de endereço baseado no CEP"""
    cep_key = f"cep_{tipo}"
    if cep_key in st.session_state and st.session_state[cep_key]:
        cep_limpo = re.sub(r'[^0-9]', '', st.session_state[cep_key])
        if len(cep_limpo) == 8:
            try:
                endereco_info = buscar_cep(cep_limpo)
                if endereco_info:
                    campos = {
                        'logradouro': f"endereco_{tipo}",
                        'bairro': f"bairro_{tipo}",
                        'cidade': f"cidade_{tipo}",
                        'estado': f"estado_{tipo}"
                    }
                    
                    for campo_origem, campo_destino in campos.items():
                        if campo_destino not in st.session_state or not st.session_state[campo_destino]:
                            st.session_state[campo_destino] = endereco_info.get(campo_origem, '')
                    st.rerun()
            except Exception as e:
                st.warning(f"Erro ao buscar CEP: {str(e)}")

def gerar_pdf_formatado(tipo, dados):
    """Gera um PDF formatado similar às fichas originais com margens corretas"""
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    
    # Configurações de layout
    pdf.set_margins(20, 15, 20)  # Margens: esquerda, topo, direita
    pdf.set_auto_page_break(True, margin=15)  # Margem inferior
    
    # Configuração de fonte
    try:
        pdf.add_font('Arial', '', 'arial.ttf', uni=True)
        pdf.add_font('Arial', 'B', 'arialbd.ttf', uni=True)
        use_arial = True
    except:
        st.warning("Fontes Arial não encontradas, usando fontes padrão")
        use_arial = False
    
    # Título
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'FICHA CADASTRAL', 0, 1, 'C')
    pdf.ln(5)
    
    if tipo == 'pf':
        # Formatação para Pessoa Física
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'PESSOA FÍSICA', 0, 1)
        pdf.ln(3)
        
        # Dados da Imobiliária
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 6, 'CORRETOR(A):', 0, 0)
        pdf.cell(0, 6, dados.get('corretor', ''), 0, 1)
        pdf.cell(30, 6, 'IMOBILIÁRIA:', 0, 0)
        pdf.cell(0, 6, dados.get('imobiliaria', ''), 0, 1)
        pdf.cell(30, 6, 'Nº NEGÓCIO:', 0, 0)
        pdf.cell(0, 6, dados.get('numero_negocio', ''), 0, 1)
        pdf.ln(5)
        
        # Dados do Cliente
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, 'DADOS DO CLIENTE', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        # Nome
        pdf.cell(60, 6, 'NOME COMPLETO SEM ABREVIAR:', 0, 0)
        pdf.cell(0, 6, dados.get('nome', ''), 0, 1)
        
        # Dados pessoais
        pdf.cell(25, 6, 'GÊNERO:', 0, 0)
        pdf.cell(25, 6, dados.get('genero', ''), 0, 0)
        pdf.cell(40, 6, 'DATA NASCIMENTO:', 0, 0)
        pdf.cell(0, 6, dados.get('data_nascimento', ''), 0, 1)
        
        pdf.cell(20, 6, 'CPF:', 0, 0)
        pdf.cell(40, 6, dados.get('cpf', ''), 0, 0)
        pdf.cell(25, 6, 'CELULAR:', 0, 0)
        pdf.cell(0, 6, dados.get('celular', ''), 0, 1)
        pdf.cell(20, 6, 'E-MAIL:', 0, 0)
        pdf.cell(0, 6, dados.get('email', ''), 0, 1)
        
        pdf.cell(35, 6, 'NACIONALIDADE:', 0, 0)
        pdf.cell(40, 6, dados.get('nacionalidade', ''), 0, 0)
        pdf.cell(25, 6, 'PROFISSÃO:', 0, 0)
        pdf.cell(0, 6, dados.get('profissao', ''), 0, 1)
        
        # Estado Civil com condicional para união estável
        estado_civil = dados.get('estado_civil', '')
        if estado_civil in ["SOLTEIRO(A)", "VIÚVO(A)", "DIVORCIADO(A)"] and dados.get('uniao_estavel', '') == "SIM":
            estado_civil += " (União Estável)"
            
        pdf.cell(30, 6, 'ESTADO CIVIL:', 0, 0)
        pdf.cell(40, 6, estado_civil, 0, 0)
        pdf.cell(45, 6, 'REGIME CASAMENTO:', 0, 0)
        pdf.cell(0, 6, dados.get('regime_casamento', ''), 0, 1)
        pdf.ln(5)
        
        # Endereço
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, 'ENDEREÇO ', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(15, 6, 'CEP:', 0, 0)
        pdf.cell(25, 6, dados.get('cep', ''), 0, 0)
        pdf.cell(25, 6, 'ENDEREÇO:   ', '0', 0)
        pdf.cell(0, 6, dados.get('endereco', ''), 0, 1)
        
        pdf.cell(20, 6, 'NÚMERO:', 0, 0)
        pdf.cell(20, 6, dados.get('numero', ''), 0, 0)
        pdf.cell(20, 6, 'BAIRRO:', 0, 0)
        pdf.cell(0, 6, dados.get('bairro', ''), 0, 1)
        
        pdf.cell(20, 6, 'CIDADE:', 0, 0)
        pdf.cell(50, 6, dados.get('cidade', ''), 0, 0)
        pdf.cell(25, 6, 'ESTADO:   ', 0, 0)
        pdf.cell(0, 6, dados.get('estado', ''), 0, 1)
        pdf.ln(5)
        
        # Dados do Cônjuge (se houver)
        if dados.get('nome_conjuge', ''):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, 'DADOS DO CÔNJUGE', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            pdf.cell(60, 6, 'NOME COMPLETO SEM ABREVIAR:', 0, 0)
            pdf.cell(0, 6, dados.get('nome_conjuge', ''), 0, 1)
            
            # Adicionados gênero e data de nascimento do cônjuge
            pdf.cell(25, 6, 'GÊNERO:', 0, 0)
            pdf.cell(25, 6, dados.get('genero_conjuge', ''), 0, 0)
            pdf.cell(40, 6, 'DATA NASCIMENTO:', 0, 0)
            pdf.cell(0, 6, dados.get('data_nascimento_conjuge', ''), 0, 1)
            
            pdf.cell(20, 6, 'CPF:', 0, 0)
            pdf.cell(40, 6, dados.get('cpf_conjuge', ''), 0, 0)
            pdf.cell(25, 6, 'CELULAR:', 0, 0)
            pdf.cell(0, 6, dados.get('celular_conjuge', ''), 0, 1)
            pdf.cell(20, 6, 'E-MAIL:', 0, 0)
            pdf.cell(0, 6, dados.get('email_conjuge', ''), 0, 1)
            
            pdf.cell(35, 6, 'NACIONALIDADE:', 0, 0)
            pdf.cell(40, 6, dados.get('nacionalidade_conjuge', ''), 0, 0)
            pdf.cell(25, 6, 'PROFISSÃO:', 0, 0)
            pdf.cell(0, 6, dados.get('profissao_conjuge', ''), 0, 1)
            
            # Estado Civil do cônjuge com condicional para união estável
            estado_civil_conjuge = dados.get('estado_civil_conjuge', '')
            if estado_civil_conjuge in ["SOLTEIRO(A)", "VIÚVO(A)", "DIVORCIADO(A)"] and dados.get('uniao_estavel_conjuge', '') == "SIM":
                estado_civil_conjuge += " (União Estável)"
                
            pdf.cell(30, 6, 'ESTADO CIVIL:', 0, 0)
            pdf.cell(40, 6, estado_civil_conjuge, 0, 0)
            pdf.cell(45, 6, 'REGIME CASAMENTO:', 0, 0)
            pdf.cell(0, 6, dados.get('regime_casamento_conjuge', ''), 0, 1)
            pdf.ln(5)
            
            # Endereço do Cônjuge
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, 'ENDEREÇO DO CÔNJUGE ', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            pdf.cell(15, 6, 'CEP:', 0, 0)
            pdf.cell(25, 6, dados.get('cep_conjuge', ''), 0, 0)
            pdf.cell(25, 6, 'ENDEREÇO:   ', '0', 0)
            pdf.cell(0, 6, dados.get('endereco_conjuge', ''), 0, 1)
            
            pdf.cell(20, 6, 'NÚMERO:', 0, 0)
            pdf.cell(20, 6, dados.get('numero_conjuge', ''), 0, 0)
            pdf.cell(20, 6, 'BAIRRO:', 0, 0)
            pdf.cell(0, 6, dados.get('bairro_conjuge', ''), 0, 1)
            
            pdf.cell(20, 6, 'CIDADE:', 0, 0)
            pdf.cell(50, 6, dados.get('cidade_conjuge', ''), 0, 0)
            pdf.cell(25, 6, 'ESTADO:   ', 0, 0)
            pdf.cell(0, 6, dados.get('estado_conjuge', ''), 0, 1)
            pdf.ln(5)
        
        # Termo de consentimento
        pdf.set_font('Arial', '', 8)
        pdf.multi_cell(0, 4, 'Para os fins da Lei 13.709/18, o titular concorda com: (i) o tratamento de seus dados pessoais e de seu cônjuge, quando for o caso, para os fins relacionados ao cumprimento das obrigações previstas na Lei, nesta ficha cadastral ou dela decorrente; e (ii) o envio de seus dados pessoais e da documentação respectiva a órgãos e entidades tais como a Secretaria da Fazenda Municipal, administração do condomínio, Cartórios, ao credor fiduciário, à companhia securitizadora e a outras pessoas, nos limites permitidos em Lei.')
          
        # Data Justificada a esquerda abaixo
        pdf.ln(2)
        pdf.cell(0, 5, f"Uberlândia/MG, {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
               
        pdf.ln(5)  # Espaço adicional

        # Assinaturas
        pdf.ln(8)
        pdf.set_font('Arial', '', 10)
        col_width = pdf.w / 2 - 15
        
        # Linhas de assinatura
        pdf.cell(col_width, 6, '_______________________________', 0, 0, 'C')
        pdf.cell(col_width, 6, '_______________________________', 0, 1, 'C')
        # 1° Proponente
        pdf.cell(col_width, 6, 'ASSINATURA DO 1° PROPONENTE', 0, 0, 'C')
        pdf.cell(col_width, 6, 'ASSINATURA DO 2° PROPONENTE', 0, 1, 'C')

    
    else:
        # Formatação para Pessoa Jurídica (ajustada para ficar igual à PF)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'PESSOA JURÍDICA', 0, 1)
        pdf.ln(3)
        
        # Dados da Imobiliária
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 6, 'CORRETOR(A):', 0, 0)
        pdf.cell(0, 6, dados.get('corretor', ''), 0, 1)
        pdf.cell(30, 6, 'IMOBILIÁRIA:', 0, 0)
        pdf.cell(0, 6, dados.get('imobiliaria', ''), 0, 1)
        pdf.cell(30, 6, 'Nº NEGÓCIO:', 0, 0)
        pdf.cell(0, 6, dados.get('numero_negocio', ''), 0, 1)
        pdf.ln(5)
        
        # Dados da Empresa
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, 'DADOS DA EMPRESA', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        # Razão Social
        pdf.cell(60, 6, 'RAZÃO SOCIAL:', 0, 0)
        pdf.cell(0, 6, dados.get('razao_social', ''), 0, 1)
        
        # CNPJ e Telefone
        pdf.cell(20, 6, 'CNPJ:', 0, 0)
        pdf.cell(50, 6, dados.get('cnpj', ''), 0, 0)
        pdf.cell(25, 6, 'TELEFONE:', 0, 0)
        pdf.cell(0, 6, dados.get('telefone_empresa', ''), 0, 1)
        
        # E-mail
        pdf.cell(20, 6, 'E-MAIL:', 0, 0)
        pdf.cell(0, 6, dados.get('email', ''), 0, 1)
        pdf.ln(5)
        
        # Endereço da Empresa
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, 'ENDEREÇO DA EMPRESA', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(15, 6, 'CEP:', 0, 0)
        pdf.cell(25, 6, dados.get('cep_empresa', ''), 0, 0)
        pdf.cell(25, 6, 'ENDEREÇO:  ', 'B', 0)
        pdf.cell(0, 6, dados.get('endereco_empresa', ''), 0, 1)
        
        pdf.cell(20, 6, 'NÚMERO:', 0, 0)
        pdf.cell(20, 6, dados.get('numero_empresa', ''), 0, 0)
        pdf.cell(20, 6, 'BAIRRO:', 0, 0)
        pdf.cell(0, 6, dados.get('bairro_empresa', ''), 0, 1)
        
        pdf.cell(20, 6, 'CIDADE:', 0, 0)
        pdf.cell(50, 6, dados.get('cidade_empresa', ''), 0, 0)
        pdf.cell(25, 6, 'ESTADO:  ', 0, 0)
        pdf.cell(0, 6, dados.get('estado_empresa', ''), 0, 1)
        pdf.ln(5)
        
        # Dados do Administrador
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, 'DADOS DO ADMINISTRADOR', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        # Nome
        pdf.cell(60, 6, 'NOME COMPLETO SEM ABREVIAR:', 0, 0)
        pdf.cell(0, 6, dados.get('nome_administrador', ''), 0, 1)
        
        # Dados pessoais
        pdf.cell(25, 6, 'GÊNERO:', 0, 0)
        pdf.cell(25, 6, dados.get('genero_administrador', ''), 0, 0)
        pdf.cell(40, 6, 'DATA NASCIMENTO:', 0, 0)
        pdf.cell(0, 6, dados.get('data_nascimento_administrador', ''), 0, 1)
        
        pdf.cell(20, 6, 'CPF:', 0, 0)
        pdf.cell(40, 6, dados.get('cpf_administrador', ''), 0, 0)
        pdf.cell(25, 6, 'CELULAR:', 0, 0)
        pdf.cell(0, 6, dados.get('celular_administrador', ''), 0, 1)
        pdf.cell(20, 6, 'E-MAIL:', 0, 0)
        pdf.cell(0, 6, dados.get('email_administrador', ''), 0, 1)
        
        pdf.cell(35, 6, 'NACIONALIDADE:', 0, 0)
        pdf.cell(40, 6, dados.get('nacionalidade_administrador', ''), 0, 0)
        pdf.cell(25, 6, 'PROFISSÃO:', 0, 0)
        pdf.cell(0, 6, dados.get('profissao_administrador', ''), 0, 1)
        
        # Estado Civil com condicional para união estável
        estado_civil = dados.get('estado_civil_administrador', '')
        if estado_civil in ["SOLTEIRO(A)", "VIÚVO(A)", "DIVORCIADO(A)"] and dados.get('uniao_estavel_administrador', '') == "SIM":
            estado_civil += " (União Estável)"
            
        pdf.cell(30, 6, 'ESTADO CIVIL:', 0, 0)
        pdf.cell(40, 6, estado_civil, 0, 0)
        pdf.cell(45, 6, 'REGIME CASAMENTO:', 0, 0)
        pdf.cell(0, 6, dados.get('regime_casamento_administrador', ''), 0, 1)
        pdf.ln(5)
        
        # Endereço do Administrador
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, 'ENDEREÇO DO ADMINISTRADOR', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(15, 6, 'CEP:', 0, 0)
        pdf.cell(25, 6, dados.get('cep_administrador', ''), 0, 0)
        pdf.cell(25, 6, 'ENDEREÇO:  ', 'B', 0)
        pdf.cell(0, 6, dados.get('endereco_administrador', ''), 0, 1)
        
        pdf.cell(20, 6, 'NÚMERO:', 0, 0)
        pdf.cell(20, 6, dados.get('numero_administrador', ''), 0, 0)
        pdf.cell(20, 6, 'BAIRRO:', 0, 0)
        pdf.cell(0, 6, dados.get('bairro_administrador', ''), 0, 1)
        
        pdf.cell(20, 6, 'CIDADE:', 0, 0)
        pdf.cell(50, 6, dados.get('cidade_administrador', ''), 0, 0)
        pdf.cell(25, 6, 'ESTADO:  ', 0, 0)
        pdf.cell(0, 6, dados.get('estado_administrador', ''), 0, 1)
        pdf.ln(5)
        
        # Termo de consentimento
        pdf.set_font('Arial', '', 8)
        pdf.multi_cell(0, 4, 'Para os fins da Lei 13.709/18, o titular concorda com: (i) o tratamento de seus dados pessoais e de seu cônjuge, quando for o caso, para os fins relacionados ao cumprimento das obrigações previstas na Lei, nesta ficha cadastral ou dela decorrente; e (ii) o envio de seus dados pessoais e da documentação respectiva a órgãos e entidades tais como a Secretaria da Fazenda Municipal, administração do condomínio, Cartórios, ao credor fiduciário, à companhia securitizadora e a outras pessoas, nos limites permitidos em Lei.')
    
    
        # Data centralizada abaixo
        pdf.ln(5)
        pdf.cell(0, 5, f"Uberlândia/MG, {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    
    
        # Assinatura
        pdf.ln(8)
        pdf.set_font('Arial', '', 10)
        
        # Assinatura do Administrador
        pdf.cell(0, 6, '_______________________________', 0, 1, 'C')
        pdf.cell(0, 6, 'ASSINATURA DO ADMINISTRADOR', 0, 1, 'C')
        pdf.ln(10)  # Espaço adicional

    
    # Salva o PDF temporariamente
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, f"ficha_{tipo}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    pdf.output(pdf_path)
    
    return pdf_path

# Funções de banco de dados
def carregar_clientes_pf():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql('SELECT * FROM clientes_pf', conn)
    conn.close()
    return df

def carregar_clientes_pj():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql('SELECT * FROM clientes_pj', conn)
    conn.close()
    return df

def salvar_cliente_pf(cliente):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO clientes_pf (
        nome, genero, data_nascimento, celular, cpf, email,
        nacionalidade, profissao, estado_civil, regime_casamento, uniao_estavel,
        cep, endereco, numero, bairro, cidade, estado,
        nome_conjuge, genero_conjuge, data_nascimento_conjuge, cpf_conjuge,
        celular_conjuge, email_conjuge, nacionalidade_conjuge, profissao_conjuge,
        estado_civil_conjuge, regime_casamento_conjuge, uniao_estavel_conjuge,
        cep_conjuge, endereco_conjuge, numero_conjuge, bairro_conjuge,
        cidade_conjuge, estado_conjuge, data_cadastro,
        corretor, imobiliaria, numero_negocio
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        cliente['nome'], cliente['genero'], cliente['data_nascimento'],
        cliente['celular'], cliente['cpf'], cliente.get('email', ''),
        cliente['nacionalidade'], cliente['profissao'], cliente['estado_civil'],
        cliente['regime_casamento'], cliente['uniao_estavel'],
        cliente['cep'], cliente['endereco'], cliente['numero'],
        cliente['bairro'], cliente['cidade'], cliente['estado'],
        cliente.get('nome_conjuge', ''), cliente.get('genero_conjuge', ''), 
        cliente.get('data_nascimento_conjuge', ''), cliente.get('cpf_conjuge', ''),
        cliente.get('celular_conjuge', ''), cliente.get('email_conjuge', ''), 
        cliente.get('nacionalidade_conjuge', ''), cliente.get('profissao_conjuge', ''),
        cliente.get('estado_civil_conjuge', ''), cliente.get('regime_casamento_conjuge', ''),
        cliente.get('uniao_estavel_conjuge', ''), cliente.get('cep_conjuge', ''),
        cliente.get('endereco_conjuge', ''), cliente.get('numero_conjuge', ''),
        cliente.get('bairro_conjuge', ''), cliente.get('cidade_conjuge', ''),
        cliente.get('estado_conjuge', ''), cliente['data_cadastro'], 
        cliente['corretor'], cliente['imobiliaria'], cliente['numero_negocio']
    ))
    conn.commit()
    conn.close()

def salvar_cliente_pj(cliente):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO clientes_pj (
        razao_social, cnpj, email, telefone_empresa, cep_empresa, endereco_empresa,
        numero_empresa, bairro_empresa, cidade_empresa, estado_empresa,
        genero_administrador, nome_administrador, data_nascimento_administrador,
        cpf_administrador, celular_administrador, email_administrador, nacionalidade_administrador,
        profissao_administrador, estado_civil_administrador, regime_casamento_administrador,
        uniao_estavel_administrador, cep_administrador, endereco_administrador,
        numero_administrador, bairro_administrador, cidade_administrador,
        estado_administrador, data_cadastro, corretor, imobiliaria, numero_negocio
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        cliente['razao_social'], cliente['cnpj'], cliente.get('email', ''),
        cliente.get('telefone_empresa', ''), cliente.get('cep_empresa', ''),
        cliente.get('endereco_empresa', ''), cliente.get('numero_empresa', ''),
        cliente.get('bairro_empresa', ''), cliente.get('cidade_empresa', ''),
        cliente.get('estado_empresa', ''), cliente['genero_administrador'],
        cliente['nome_administrador'], cliente.get('data_nascimento_administrador', ''),
        cliente['cpf_administrador'], cliente['celular_administrador'],
        cliente.get('email_administrador', ''),  # Nova coluna adicionada
        cliente.get('nacionalidade_administrador', 'BRASILEIRA'),
        cliente.get('profissao_administrador', ''),
        cliente.get('estado_civil_administrador', ''),
        cliente.get('regime_casamento_administrador', ''),
        cliente.get('uniao_estavel_administrador', 'NÃO'),
        cliente.get('cep_administrador', ''), cliente.get('endereco_administrador', ''),
        cliente.get('numero_administrador', ''), cliente.get('bairro_administrador', ''),
        cliente.get('cidade_administrador', ''), cliente.get('estado_administrador', ''),
        cliente['data_cadastro'], cliente.get('corretor', ''),
        cliente.get('imobiliaria', ''), cliente.get('numero_negocio', '')
    ))
    
    conn.commit()
    conn.close()

# Carregar dados iniciais
if 'clientes_pf' not in st.session_state:
    st.session_state.clientes_pf = carregar_clientes_pf()

if 'clientes_pj' not in st.session_state:
    st.session_state.clientes_pj = carregar_clientes_pj()

# Interface principal
st.title("Sistema de Cadastro Imobiliário")

# Abas
tab1, tab2, tab3 = st.tabs([
    "Ficha Cadastral PF", 
    "Ficha Cadastral PJ", 
    "Consulta de Registros"
])

# Variáveis para controle dos downloads
pdf_path_pf = None
pdf_path_pj = None

with tab1:
    st.header("Ficha Cadastral - Pessoa Física")
    
    submitted_pf = False
    imprimir_pf = False
    
    with st.form(key="form_pf"):
        # Dados da Imobiliária
        st.subheader("Dados da Imobiliária")
        col1, col2 = st.columns(2)
        with col1:
            corretor = st.text_input("Corretor(a)")
            imobiliaria = st.text_input("Imobiliária", value=" ")
        with col2:
            numero_negocio = st.text_input("Nº do Negócio")
        
        # Dados do Cliente - Layout Compacto
        st.subheader("Dados do Cliente")
        
        # Linha 1: Gênero
        genero = st.radio("Gênero", ["MASCULINO", "FEMININO"], horizontal=True)
        
        # Linha 2: Nome e Data Nascimento
        linha1 = st.columns([2, 1])
        with linha1[0]:
            nome = st.text_input("Nome Completo *")
        with linha1[1]:
            data_nascimento = st.date_input("Data de Nascimento", 
                                         value=None,
                                         format="DD/MM/YYYY",
                                         key="data_nascimento_pf")
        
        # Linha 3: CPF e Celular
        linha2 = st.columns(2)
        with linha2[0]:
            cpf = st.text_input("CPF *", help="Formato: 000.000.000-00", 
                              value=st.session_state.get("cpf_pf", ""),
                              key="cpf_pf")
        with linha2[1]:
            celular = st.text_input("Celular *", help="Formato: (00) 00000-0000", 
                                  value=st.session_state.get("celular_pf", ""),
                                  key="celular_pf")
        
        # Dados Complementares
        st.markdown("**Dados Complementares**")
        
        # Linha 4: Nacionalidade e Profissão
        linha3 = st.columns(2)
        with linha3[0]:
            nacionalidade = st.text_input("Nacionalidade", value="BRASILEIRA")
        with linha3[1]:
            profissao = st.text_input("Profissão")
        
        # Linha 5: E-mail
        email = st.text_input("E-mail")
        
        # Linha 6: Estado Civil e Regime de Casamento
        linha4 = st.columns(2)
        with linha4[0]:
            estado_civil = st.selectbox("Estado Civil", 
                                     ["", "CASADO(A)", "SOLTEIRO(A)", "VIÚVO(A)", "DIVORCIADO(A)"])
        with linha4[1]:
            regime_casamento = st.selectbox("Regime de Casamento",
                ["", "COMUNHÃO UNIVERSAL DE BENS", "SEPARAÇÃO DE BENS", 
                "COMUNHÃO PARCIAL DE BENS", "COMUNHÃO DE BENS (REGIME ÚNICO ANTES DE 1977)"]
            )
        
        # Linha 7: União Estável
        uniao_estavel = st.checkbox("União Estável")

        # Endereço (mantido como estava)
        st.subheader("Endereço")
        col1, col2 = st.columns(2)
        with col1:
            cep = st.text_input("CEP", help="Formato: 00000-000", 
                              value=st.session_state.get("cep_pf", ""),
                              key="cep_pf")
            
            buscar_cep_pf = st.form_submit_button("Buscar CEP")
            if buscar_cep_pf:
                preencher_endereco('pf')
           
            endereco = st.text_input("Endereço", key="endereco_pf")
            numero = st.text_input("Número", key="numero_pf")
        with col2:
            bairro = st.text_input("Bairro", key="bairro_pf")
            cidade = st.text_input("Cidade", key="cidade_pf")
            estado = st.text_input("Estado", key="estado_pf")
        
        # Dados do 2° Proponente/Cônjuge (mantido como estava)
        st.subheader("Dados do 2° Proponente/Cônjuge")
        tem_conjuge = st.radio("Casado ou convivente com o 1° proponente?", 
                             ["SIM", "NÃO"], horizontal=True)
        
        if tem_conjuge == "SIM":
            # Seção do Cônjuge com layout compacto similar
            genero_conjuge = st.radio("Gênero", ["MASCULINO", "FEMININO"], 
                                    key="genero_conjuge_pf", horizontal=True)
            
            linha_conjuge1 = st.columns([2, 1])
            with linha_conjuge1[0]:
                nome_conjuge = st.text_input("Nome Completo")
            with linha_conjuge1[1]:
                data_nascimento_conjuge = st.date_input("Data de Nascimento", 
                                                      value=None,
                                                      format="DD/MM/YYYY",
                                                      key="data_nascimento_conjuge_pf")
            
            linha_conjuge2 = st.columns(2)
            with linha_conjuge2[0]:
                cpf_conjuge = st.text_input("CPF", help="Formato: 000.000.000-00", 
                                          value=st.session_state.get("cpf_conjuge_pf", ""),
                                          key="cpf_conjuge_pf")
            with linha_conjuge2[1]:
                celular_conjuge = st.text_input("Celular", help="Formato: (00) 00000-0000", 
                                              value=st.session_state.get("celular_conjuge_pf", ""),
                                              key="celular_conjuge_pf")
            
            linha_conjuge3 = st.columns(2)
            with linha_conjuge3[0]:
                nacionalidade_conjuge = st.text_input("Nacionalidade", value="BRASILEIRA", key="nacionalidade_conjuge_pf")
            with linha_conjuge3[1]:
                profissao_conjuge = st.text_input("Profissão", key="profissao_conjuge_pf")
            
            email_conjuge = st.text_input("E-mail do Cônjuge", key="email_conjuge_pf")
            
            linha_conjuge4 = st.columns(2)
            with linha_conjuge4[0]:
                estado_civil_conjuge = st.selectbox("Estado Civil", 
                                                  ["", "CASADO(A)", "SOLTEIRO(A)", "VIÚVO(A)", "DIVORCIADO(A)"],
                                                  key="estado_civil_conjuge_pf")
            with linha_conjuge4[1]:
                regime_casamento_conjuge = st.selectbox("Regime de Casamento", 
                                                      ["", "COMUNHÃO UNIVERSAL DE BENS", "SEPARAÇÃO DE BENS", 
                                                       "COMUNHÃO PARCIAL DE BENS", "COMUNHÃO DE BENS (REGIME ÚNICO ANTES DE 1977)"],
                                                      key="regime_casamento_conjuge_pf")
            
            uniao_estavel_conjuge = st.checkbox("União Estável", key="uniao_estavel_conjuge_pf")

            # Endereço do Cônjuge (mantido como estava)
            col1, col2 = st.columns(2)
            with col1:
                cep_conjuge = st.text_input("CEP", help="Formato: 00000-000", 
                                          value=st.session_state.get("cep_conjuge_pf", ""),
                                          key="cep_conjuge_pf")

                buscar_cep_conjuge = st.form_submit_button("Buscar CEP do Cônjuge")
                if buscar_cep_conjuge and st.session_state.get("cep_conjuge_pf", ""):
                    preencher_endereco('conjuge_pf')
    
                endereco_conjuge = st.text_input("Endereço", key="endereco_conjuge_pf")
                numero_conjuge = st.text_input("Número", key="numero_conjuge_pf")
            with col2:
                bairro_conjuge = st.text_input("Bairro", key="bairro_conjuge_pf")
                cidade_conjuge = st.text_input("Cidade", key="cidade_conjuge_pf")
                estado_conjuge = st.text_input("Estado", key="estado_conjuge_pf")
        
        # Termo de consentimento e botões (mantidos como estavam)
        st.markdown("""
        **Para os fins da Lei 13.709/18, o titular concorda com:**  
        (i) o tratamento de seus dados pessoais e de seu cônjuge, quando for o caso, para os fins relacionados ao cumprimento das obrigações
        previstas na Lei, nesta ficha cadastral ou dela decorrente; e  
        (ii) o envio de seus dados pessoais e da documentação respectiva a órgãos e entidades tais como a Secretaria da Fazenda Municipal,
        administração do condomínio, Cartórios, ao credor fiduciário, à companhia securitizadora e a outras pessoas, nos limites permitidos em Lei.
        """)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            submitted_pf = st.form_submit_button("Salvar Cadastro")
        with col2:
            imprimir_pf = st.form_submit_button("Imprimir Formulário")
    
    # Processar após o formulário
    if submitted_pf:
        # Formatar os campos antes de salvar
        celular_formatado = formatar_telefone(st.session_state.get("celular_pf", ""))
        cpf_formatado = formatar_cpf(st.session_state.get("cpf_pf", ""))
        cep_formatado = re.sub(r'[^0-9]', '', st.session_state.get("cep_pf", ""))
        data_nascimento_formatada = data_nascimento.strftime('%d/%m/%Y') if data_nascimento else ""
        
        if tem_conjuge == "SIM":
            cpf_conjuge_formatado = formatar_cpf(st.session_state.get("cpf_conjuge_pf", ""))
            celular_conjuge_formatado = formatar_telefone(st.session_state.get("celular_conjuge_pf", ""))
            cep_conjuge_formatado = re.sub(r'[^0-9]', '', st.session_state.get("cep_conjuge_pf", ""))
            data_nascimento_conjuge_formatada = data_nascimento_conjuge.strftime('%d/%m/%Y') if data_nascimento_conjuge else ""
        else:
            cpf_conjuge_formatado = celular_conjuge_formatado = cep_conjuge_formatado = data_nascimento_conjuge_formatada = ""
            genero_conjuge = ""
        
        if not nome or not cpf_formatado or not celular_formatado:
            st.error("Por favor, preencha os campos obrigatórios (*)")
        elif not validar_cpf(cpf_formatado):
            st.error("CPF inválido. Por favor, verifique o número.")
        else:
            novo_cliente = {
                'nome': nome,
                'genero': genero,
                'data_nascimento': data_nascimento_formatada,
                'celular': celular_formatado,
                'cpf': cpf_formatado,
                'email': email,
                'nacionalidade': nacionalidade,
                'profissao': profissao,
                'estado_civil': estado_civil,
                'uniao_estavel': "SIM" if uniao_estavel else "NÃO",
                'regime_casamento': regime_casamento,
                'cep': cep_formatado,
                'endereco': st.session_state.get("endereco_pf", ""),
                'numero': st.session_state.get("numero_pf", ""),
                'bairro': st.session_state.get("bairro_pf", ""),
                'cidade': st.session_state.get("cidade_pf", ""),
                'estado': st.session_state.get("estado_pf", ""),
                'nome_conjuge': nome_conjuge if tem_conjuge == "SIM" else "",
                'genero_conjuge': genero_conjuge if tem_conjuge == "SIM" else "",
                'data_nascimento_conjuge': data_nascimento_conjuge_formatada if tem_conjuge == "SIM" else "",
                'cpf_conjuge': cpf_conjuge_formatado if tem_conjuge == "SIM" else "",
                'celular_conjuge': celular_conjuge_formatado if tem_conjuge == "SIM" else "",
                'email_conjuge': email_conjuge if tem_conjuge == "SIM" else "",
                'nacionalidade_conjuge': nacionalidade_conjuge if tem_conjuge == "SIM" else "",
                'profissao_conjuge': profissao_conjuge if tem_conjuge == "SIM" else "",
                'estado_civil_conjuge': estado_civil_conjuge if tem_conjuge == "SIM" else "",
                'uniao_estavel_conjuge': "SIM" if tem_conjuge == "SIM" and uniao_estavel_conjuge else "NÃO",
                'regime_casamento_conjuge': regime_casamento_conjuge if tem_conjuge == "SIM" else "",
                'cep_conjuge': cep_conjuge_formatado if tem_conjuge == "SIM" else "",
                'endereco_conjuge': st.session_state.get("endereco_conjuge_pf", "") if tem_conjuge == "SIM" else "",
                'numero_conjuge': st.session_state.get("numero_conjuge_pf", "") if tem_conjuge == "SIM" else "",
                'bairro_conjuge': st.session_state.get("bairro_conjuge_pf", "") if tem_conjuge == "SIM" else "",
                'cidade_conjuge': st.session_state.get("cidade_conjuge_pf", "") if tem_conjuge == "SIM" else "",
                'estado_conjuge': st.session_state.get("estado_conjuge_pf", "") if tem_conjuge == "SIM" else "",
                'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'corretor': corretor,
                'imobiliaria': imobiliaria,
                'numero_negocio': numero_negocio
            }
            
            try:
                salvar_cliente_pf(novo_cliente)
                st.session_state.clientes_pf = carregar_clientes_pf()
                st.success("Cliente cadastrado com sucesso!")
                
                # Gera o PDF após salvar
                pdf_path_pf = gerar_pdf_formatado('pf', novo_cliente)
            except Exception as e:
                st.error(f"Erro ao salvar cliente: {e}")
    
    if imprimir_pf:
        # Formata os dados para impressão
        dados_impressao = {
            'nome': nome,
            'genero': genero,
            'data_nascimento': data_nascimento.strftime('%d/%m/%Y') if data_nascimento else "",
            'celular': formatar_telefone(st.session_state.get("celular_pf", "")),
            'cpf': formatar_cpf(st.session_state.get("cpf_pf", "")),
            'email': email,
            'nacionalidade': nacionalidade,
            'profissao': profissao,
            'estado_civil': estado_civil,
            'uniao_estavel': "SIM" if uniao_estavel else "NÃO",
            'regime_casamento': regime_casamento,
            'cep': st.session_state.get("cep_pf", ""),
            'endereco': st.session_state.get("endereco_pf", ""),
            'numero': st.session_state.get("numero_pf", ""),
            'bairro': st.session_state.get("bairro_pf", ""),
            'cidade': st.session_state.get("cidade_pf", ""),
            'estado': st.session_state.get("estado_pf", ""),
            'corretor': corretor,
            'imobiliaria': imobiliaria,
            'numero_negocio': numero_negocio,
            'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        if tem_conjuge == "SIM":
            dados_impressao.update({
                'nome_conjuge': nome_conjuge,
                'genero_conjuge': genero_conjuge,
                'data_nascimento_conjuge': data_nascimento_conjuge.strftime('%d/%m/%Y') if data_nascimento_conjuge else "",
                'cpf_conjuge': formatar_cpf(st.session_state.get("cpf_conjuge_pf", "")),
                'celular_conjuge': formatar_telefone(st.session_state.get("celular_conjuge_pf", "")),
                'email_conjuge': email_conjuge,
                'nacionalidade_conjuge': nacionalidade_conjuge,
                'profissao_conjuge': profissao_conjuge,
                'estado_civil_conjuge': estado_civil_conjuge,
                'uniao_estavel_conjuge': "SIM" if uniao_estavel_conjuge else "NÃO",
                'regime_casamento_conjuge': regime_casamento_conjuge,
                'cep_conjuge': st.session_state.get("cep_conjuge_pf", ""),
                'endereco_conjuge': st.session_state.get("endereco_conjuge_pf", ""),
                'numero_conjuge': st.session_state.get("numero_conjuge_pf", ""),
                'bairro_conjuge': st.session_state.get("bairro_conjuge_pf", ""),
                'cidade_conjuge': st.session_state.get("cidade_conjuge_pf", ""),
                'estado_conjuge': st.session_state.get("estado_conjuge_pf", "")
            })
        
        # Gera o PDF
        pdf_path_pf = gerar_pdf_formatado('pf', dados_impressao)
    
    # Botão de download fora do formulário
    if pdf_path_pf:
        with open(pdf_path_pf, "rb") as f:
            st.download_button(
                "Baixar Ficha em PDF",
                f,
                file_name=f"ficha_pf_{nome if nome else 'sem_nome'}.pdf",
                mime="application/pdf"
            )

with tab2:
    st.header("Ficha Cadastral - Pessoa Jurídica")
    
    submitted_pj = False
    imprimir_pj = False
    
    with st.form(key="form_pj"):
        # Dados da Imobiliária
        st.subheader("Dados da Imobiliária")
        col1, col2 = st.columns(2)
        with col1:
            corretor = st.text_input("Corretor(a)", key="corretor_pj")
            imobiliaria = st.text_input("Imobiliária", key="imobiliaria_pj", value=" ")
        with col2:
            numero_negocio = st.text_input("Nº do Negócio", key="numero_negocio_pj")
        
        # Dados da Pessoa Jurídica
        st.subheader("Dados da Pessoa Jurídica")
        razao_social = st.text_input("Razão Social (conforme o cartão de CNPJ) *", key="razao_social_pj")
        cnpj = st.text_input("CNPJ *", key="cnpj_pj", help="Formato: 00.000.000/0000-00",
                            value=st.session_state.get("cnpj_pj", ""))
        email = st.text_input("E-mail", key="email_pj")
        
        # Endereço da Empresa
        st.subheader("Endereço da Empresa")
        col1, col2 = st.columns(2)
        with col1:
            telefone_empresa = st.text_input("Telefone", key="telefone_empresa_pj", help="Formato: (00) 0000-0000")
            cep_empresa = st.text_input("CEP", key="cep_empresa_pj", help="Formato: 00000-000")
            
            buscar_cep_empresa = st.form_submit_button("Buscar CEP Empresa")
            if buscar_cep_empresa:
                preencher_endereco('empresa_pj')
            
            endereco_empresa = st.text_input("Endereço", key="endereco_empresa_pj")
            numero_empresa = st.text_input("Número", key="numero_empresa_pj")
        with col2:
            bairro_empresa = st.text_input("Bairro", key="bairro_empresa_pj")
            cidade_empresa = st.text_input("Cidade", key="cidade_empresa_pj")
            estado_empresa = st.text_input("Estado", key="estado_empresa_pj")
        

        # Dados do Administrador
        st.subheader("Dados do Administrador")

        # Container principal com 2 colunas (como no print 2)
        col1, col2 = st.columns(2)

        with col1:
            # Primeira coluna (esquerda)
            genero_administrador = st.radio("Gênero", ["MASCULINO", "FEMININO"], 
                                          key="genero_administrador_pj",
                                          horizontal=True)
            
            nome_administrador = st.text_input("Nome Completo *", key="nome_administrador_pj")
            
            data_nascimento_administrador = st.date_input("Data de Nascimento", 
                                                        value=None,
                                                        format="DD/MM/YYYY",
                                                        key="data_nascimento_administrador_pj")
            
            st.markdown("**Dados Complementares**")
            
            # Sub-colunas para CPF e Celular
            cpf_celular = st.columns(2)
            with cpf_celular[0]:
                cpf_administrador = st.text_input("CPF *", key="cpf_administrador_pj",
                                                help="Formato: 000.000.000-00",
                                                value=st.session_state.get("cpf_administrador_pj", ""))
            with cpf_celular[1]:
                celular_administrador = st.text_input("Celular *", key="celular_administrador_pj",
                                                    help="Formato: (00) 00000-0000",
                                                    value=st.session_state.get("celular_administrador_pj", ""))

        with col2:
            # Segunda coluna (direita)
            nacionalidade_administrador = st.text_input("Nacionalidade", 
                                                      value="BRASILEIRA", 
                                                      key="nacionalidade_administrador_pj")
            
            profissao_administrador = st.text_input("Profissão", key="profissao_administrador_pj")
            
            email_administrador = st.text_input("E-mail", key="email_administrador_pj")
            
            # Sub-colunas para Estado Civil e Regime
            civil_regime = st.columns(2)
            with civil_regime[0]:
                estado_civil_administrador = st.selectbox("Estado Civil", 
                                                        ["", "CASADO(A)", "SOLTEIRO(A)", "VIÚVO(A)", "DIVORCIADO(A)"],
                                                        key="estado_civil_administrador_pj")
            with civil_regime[1]:
                regime_casamento_administrador = st.selectbox("Regime de Casamento", 
                                                            ["", "COMUNHÃO UNIVERSAL DE BENS", "SEPARAÇÃO DE BENS", 
                                                             "COMUNHÃO PARCIAL DE BENS", "COMUNHÃO DE BENS (REGIME ÚNICO ANTES DE 1977)"],
                                                            key="regime_casamento_administrador_pj")
            
            # União Estável alinhada à direita
            uniao_estavel_administrador = st.checkbox("União Estável", key="uniao_estavel_administrador_pj")
        
        # Endereço do Administrador
        st.subheader("Endereço do Administrador")
        col1, col2 = st.columns(2)
        with col1:
            cep_administrador = st.text_input("CEP", key="cep_administrador_pj", help="Formato: 00000-000")
            
            buscar_cep_administrador = st.form_submit_button("Buscar CEP Administrador")
            if buscar_cep_administrador:
                preencher_endereco('administrador_pj')
            
            endereco_administrador = st.text_input("Endereço", key="endereco_administrador_pj")
            numero_administrador = st.text_input("Número", key="numero_administrador_pj")
        with col2:
            bairro_administrador = st.text_input("Bairro", key="bairro_administrador_pj")
            cidade_administrador = st.text_input("Cidade", key="cidade_administrador_pj")
            estado_administrador = st.text_input("Estado", key="estado_administrador_pj")
        
        # Termo de consentimento
        st.markdown("""
        **Para os fins da Lei 13.709/18, o titular concorda com:**  
        (i) o tratamento de seus dados pessoais e de seu cônjuge, quando for o caso, para os fins relacionados ao cumprimento das obrigações
        previstas na Lei, nesta ficha cadastral ou dela decorrente; e  
        (ii) o envio de seus dados pessoais e da documentação respectiva a órgãos e entidades tais como a Secretaria da Fazenda Municipal,
        administração do condomínio, Cartórios, ao credor fiduciário, à companhia securitizadora e a outras pessoas, nos limites permitidos em Lei.
        """)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            submitted_pj = st.form_submit_button("Salvar Cadastro")
        with col2:
            imprimir_pj = st.form_submit_button("Imprimir Formulário")
    
    # Processar após o formulário
    if submitted_pj:
        # Formatar os campos antes de salvar
        cnpj_formatado = formatar_cnpj(st.session_state.get("cnpj_pj", ""))
        cpf_administrador_formatado = formatar_cpf(st.session_state.get("cpf_administrador_pj", ""))
        celular_administrador_formatado = formatar_telefone(st.session_state.get("celular_administrador_pj", ""))
        telefone_empresa_formatado = formatar_telefone(st.session_state.get("telefone_empresa_pj", ""))
        cep_empresa_formatado = re.sub(r'[^0-9]', '', st.session_state.get("cep_empresa_pj", ""))
        cep_administrador_formatado = re.sub(r'[^0-9]', '', st.session_state.get("cep_administrador_pj", ""))
        data_nascimento_administrador_formatada = data_nascimento_administrador.strftime('%d/%m/%Y') if data_nascimento_administrador else ""
        
        if not razao_social or not cnpj_formatado or not nome_administrador or not cpf_administrador_formatado or not celular_administrador_formatado:
            st.error("Por favor, preencha os campos obrigatórios (*)")
        elif not validar_cpf(cpf_administrador_formatado):
            st.error("CPF do administrador inválido. Por favor, verifique o número.")
        else:
            novo_cliente = {
                'razao_social': razao_social,
                'cnpj': cnpj_formatado,
                'email': email,
                'telefone_empresa': telefone_empresa_formatado,
                'cep_empresa': cep_empresa_formatado,
                'endereco_empresa': st.session_state.get("endereco_empresa_pj", ""),
                'numero_empresa': st.session_state.get("numero_empresa_pj", ""),
                'bairro_empresa': st.session_state.get("bairro_empresa_pj", ""),
                'cidade_empresa': st.session_state.get("cidade_empresa_pj", ""),
                'estado_empresa': st.session_state.get("estado_empresa_pj", ""),
                'genero_administrador': genero_administrador,
                'nome_administrador': nome_administrador,
                'data_nascimento_administrador': data_nascimento_administrador_formatada,
                'cpf_administrador': cpf_administrador_formatado,
                'celular_administrador': celular_administrador_formatado,
                'nacionalidade_administrador': nacionalidade_administrador,
                'profissao_administrador': profissao_administrador,
                'estado_civil_administrador': estado_civil_administrador,
                'uniao_estavel_administrador': "SIM" if uniao_estavel_administrador else "NÃO",
                'regime_casamento_administrador': regime_casamento_administrador,
                'cep_administrador': cep_administrador_formatado,
                'endereco_administrador': st.session_state.get("endereco_administrador_pj", ""),
                'numero_administrador': st.session_state.get("numero_administrador_pj", ""),
                'bairro_administrador': st.session_state.get("bairro_administrador_pj", ""),
                'cidade_administrador': st.session_state.get("cidade_administrador_pj", ""),
                'estado_administrador': st.session_state.get("estado_administrador_pj", ""),
                'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'corretor': corretor,
                'imobiliaria': imobiliaria,
                'numero_negocio': numero_negocio
            }
            
            try:
                salvar_cliente_pj(novo_cliente)
                st.session_state.clientes_pj = carregar_clientes_pj()
                st.success("Cliente cadastrado com sucesso!")
                
                # Gera o PDF após salvar
                pdf_path_pj = gerar_pdf_formatado('pj', novo_cliente)
            except Exception as e:
                st.error(f"Erro ao salvar cliente: {e}")
    
    if imprimir_pj:
        # Formata os dados para impressão
        dados_impressao = {
            'razao_social': razao_social,
            'cnpj': formatar_cnpj(st.session_state.get("cnpj_pj", "")),
            'email': email,
            'telefone_empresa': formatar_telefone(st.session_state.get("telefone_empresa_pj", "")),
            'cep_empresa': st.session_state.get("cep_empresa_pj", ""),
            'endereco_empresa': st.session_state.get("endereco_empresa_pj", ""),
            'numero_empresa': st.session_state.get("numero_empresa_pj", ""),
            'bairro_empresa': st.session_state.get("bairro_empresa_pj", ""),
            'cidade_empresa': st.session_state.get("cidade_empresa_pj", ""),
            'estado_empresa': st.session_state.get("estado_empresa_pj", ""),
            'genero_administrador': genero_administrador,
            'nome_administrador': nome_administrador,
            'data_nascimento_administrador': data_nascimento_administrador.strftime('%d/%m/%Y') if data_nascimento_administrador else "",
            'cpf_administrador': formatar_cpf(st.session_state.get("cpf_administrador_pj", "")),
            'celular_administrador': formatar_telefone(st.session_state.get("celular_administrador_pj", "")),
            'nacionalidade_administrador': nacionalidade_administrador,
            'profissao_administrador': profissao_administrador,
            'estado_civil_administrador': estado_civil_administrador,
            'uniao_estavel_administrador': "SIM" if uniao_estavel_administrador else "NÃO",
            'regime_casamento_administrador': regime_casamento_administrador,
            'cep_administrador': st.session_state.get("cep_administrador_pj", ""),
            'endereco_administrador': st.session_state.get("endereco_administrador_pj", ""),
            'numero_administrador': st.session_state.get("numero_administrador_pj", ""),
            'bairro_administrador': st.session_state.get("bairro_administrador_pj", ""),
            'cidade_administrador': st.session_state.get("cidade_administrador_pj", ""),
            'estado_administrador': st.session_state.get("estado_administrador_pj", ""),
            'corretor': corretor,
            'imobiliaria': imobiliaria,
            'numero_negocio': numero_negocio,
            'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Gera o PDF
        pdf_path_pj = gerar_pdf_formatado('pj', dados_impressao)
    
    # Botão de download fora do formulário
    if pdf_path_pj:
        with open(pdf_path_pj, "rb") as f:
            st.download_button(
                "Baixar Ficha em PDF",
                f,
                file_name=f"ficha_pj_{razao_social if razao_social else 'sem_razao_social'}.pdf",
                mime="application/pdf"
            )

with tab3:
    st.header("Consulta de Registros")
    
    tipo_consulta = st.radio("Tipo de Consulta", 
                            ["Pessoa Física", "Pessoa Jurídica"], 
                            horizontal=True)
    
    if tipo_consulta == "Pessoa Física":
        df = st.session_state.clientes_pf.copy()
        id_col = 'id'
        nome_col = 'nome'
        doc_col = 'cpf'
        tabela = 'clientes_pf'
    else:
        df = st.session_state.clientes_pj.copy()
        id_col = 'id'
        nome_col = 'razao_social'
        doc_col = 'cnpj'
        tabela = 'clientes_pj'
    
    if not df.empty:
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            filtro_nome = st.text_input(f"Filtrar por {'nome' if tipo_consulta == 'Pessoa Física' else 'razão social'}")
        
        with col2:
            filtro_doc = st.text_input(f"Filtrar por {'CPF' if tipo_consulta == 'Pessoa Física' else 'CNPJ'}")
        
        # Aplicar filtros
        if filtro_nome:
            df = df[df[nome_col].str.contains(filtro_nome, case=False, na=False)]
        
        if filtro_doc:
            df = df[df[doc_col].str.contains(filtro_doc, case=False, na=False)]
        
        # Formatar dados para exibição
        df_formatado = df.copy()
        for col in df_formatado.columns:
            if 'data' in col.lower():
                df_formatado[col] = df_formatado[col].apply(lambda x: formatar_data_ptbr(x) if pd.notna(x) else '')
            if doc_col in col or 'cpf' in col.lower() or 'cnpj' in col.lower():
                if tipo_consulta == "Pessoa Física":
                    df_formatado[col] = df_formatado[col].apply(lambda x: formatar_cpf(x) if pd.notna(x) else '')
                else:
                    df_formatado[col] = df_formatado[col].apply(lambda x: formatar_cnpj(x) if pd.notna(x) else '')
            if 'celular' in col.lower() or 'telefone' in col.lower():
                df_formatado[col] = df_formatado[col].apply(lambda x: formatar_telefone(x) if pd.notna(x) else '')
        
        # Mostrar tabela com opção de seleção
        st.dataframe(df_formatado)
        
        # Selecionar registro para reimpressão
        if not df_formatado.empty:
            registros = df_formatado[[id_col, nome_col, doc_col]].to_dict('records')
            opcoes = {f"{r[id_col]} - {r[nome_col]} - {r[doc_col]}": r[id_col] for r in registros}
            
            selected = st.selectbox("Selecione um registro para reimprimir:", options=list(opcoes.keys()))
            
            if st.button("Reimprimir Ficha Selecionada"):
                registro_id = opcoes[selected]
                
                # Buscar dados completos no banco
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {tabela} WHERE id = ?", (registro_id,))
                dados = cursor.fetchone()
                conn.close()
                
                if dados:
                    # Converter para dicionário com nomes de colunas
                    cols = [column[0] for column in cursor.description]
                    dados_dict = dict(zip(cols, dados))
                    
                    # Aplicar formatação para garantir que seja igual ao PDF original
                    dados_formatados = {}
                    for key, value in dados_dict.items():
                        if value is None:
                            value = ''
                        
                        # Formatar datas
                        if 'data' in key.lower() and value:
                            try:
                                if re.match(r'\d{2}/\d{2}/\d{4}', str(value)):
                                    dados_formatados[key] = value
                                else:
                                    dados_formatados[key] = datetime.strptime(value, '%Y-%m-%d').strftime('%d/%m/%Y')
                            except:
                                dados_formatados[key] = value
                        
                        # Formatar CPF/CNPJ
                        elif ('cpf' in key.lower() or 'cnpj' in key.lower()) and value:
                            if 'cpf' in key.lower():
                                dados_formatados[key] = formatar_cpf(value)
                            else:
                                dados_formatados[key] = formatar_cnpj(value)
                        
                        # Formatar telefones
                        elif ('celular' in key.lower() or 'telefone' in key.lower()) and value:
                            dados_formatados[key] = formatar_telefone(value)
                        
                        # Manter outros valores como estão
                        else:
                            dados_formatados[key] = value
                    
                    # Garantir que campos booleanos estejam corretos
                    if tipo_consulta == "Pessoa Física":
                        for campo in ['uniao_estavel', 'uniao_estavel_conjuge']:
                            if campo in dados_formatados:
                                dados_formatados[campo] = 'SIM' if dados_formatados[campo] == 'SIM' else 'NÃO'
                    else:
                        if 'uniao_estavel_administrador' in dados_formatados:
                            dados_formatados['uniao_estavel_administrador'] = 'SIM' if dados_formatados['uniao_estavel_administrador'] == 'SIM' else 'NÃO'
                    
                    # Gerar PDF
                    pdf_path = gerar_pdf_formatado('pf' if tipo_consulta == "Pessoa Física" else 'pj', dados_formatados)
                    
                    # Botão de download
                    with open(pdf_path, "rb") as f:
                        nome_arquivo = f"ficha_{'pf' if tipo_consulta == 'Pessoa Física' else 'pj'}_reimpressao_{dados_formatados.get(nome_col, 'sem_nome')}.pdf"
                        st.download_button(
                            "Baixar Ficha em PDF",
                            f,
                            file_name=nome_arquivo,
                            mime="application/pdf"
                        )
        
        # Opção para exportar dados
        if st.button("Exportar Dados para Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_formatado.to_excel(writer, index=False, sheet_name='Dados')
            output.seek(0)
            st.download_button(
                label="Baixar Arquivo Excel",
                data=output,
                file_name=f"clientes_{tipo_consulta.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("Nenhum registro encontrado.")
