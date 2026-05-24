import sqlite3
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

def inicializar_banco_dados():
    conexao = sqlite3.connect("historico_ia.db")
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS configuracoes (chave TEXT PRIMARY KEY, valor TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, data_criacao TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS conversas_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, data_hora TEXT, usuario TEXT, ia TEXT)")
    conexao.commit()
    conexao.close()

def verificar_termos_aceitos():
    conexao = sqlite3.connect("historico_ia.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT valor FROM configuracoes WHERE chave='termos_aceitos'")
    resultado = cursor.fetchone()
    conexao.close()
    return resultado is not None and resultado[0] == "True"
