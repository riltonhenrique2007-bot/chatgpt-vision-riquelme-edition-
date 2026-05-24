
import os
import sqlite3
import base64
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
from datetime import datetime
from groq import Groq
from PIL import Image, ImageTk
import banco_ia
from dotenv import load_dotenv

# 🦾 O SEGREDO DO PLAY VISUAL: Dispara o gatilho que puxa a sua chave gsk_ do HD!
load_dotenv()


caminho_imagem_global = None
imagem_tk_referencia = None
chat_id_atual = None

def limpar_tela_chat_visual():
    texto_central.pack_forget()
    area_chat.config(state=tk.NORMAL)
    area_chat.delete("1.0", tk.END)
    area_chat.config(state=tk.DISABLED)

def carregar_mensagens_do_chat_ativo():
    conexao = sqlite3.connect("historico_ia.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT usuario, ia FROM conversas_v2 WHERE chat_id=? ORDER BY id ASC", (chat_id_atual,))
    linhas = cursor.fetchall()
    conexao.close()
    area_chat.config(state=tk.NORMAL)
    for msg in linhas:
        usuario_txt = msg[0]
        ia_txt = msg[1]
        if usuario_txt and usuario_txt not in ["[Foto Analisada]", "[Foto]"]:
            area_chat.insert(tk.END, f"\nVocê: {usuario_txt}\n", "usuario_estilo")
        if ia_txt:
            area_chat.insert(tk.END, f"\nAssistente Riquelme: {ia_txt}\n\n" + "-" * 50 + "\n", "ia_estilo")
    area_chat.config(state=tk.DISABLED)
    area_chat.yview(tk.END)

def recarregar_lista_barra_lateral():
    lista_chats_ui.delete(0, tk.END)
    conexao = sqlite3.connect("historico_ia.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM chats ORDER BY id DESC")
    for linha in cursor.fetchall():
        lista_chats_ui.insert(tk.END, f"💬 Chat {linha[0]} ({linha[0]})")
    conexao.close()

def criar_novo_chat_sistema():
    global chat_id_atual
    conexao = sqlite3.connect("historico_ia.db")
    cursor = conexao.cursor()
    data_atual = datetime.now().strftime("%d/%m %H:%M")
    cursor.execute("INSERT INTO chats (nome, data_criacao) VALUES (?, ?)", (f"Chat {data_atual}", data_atual))
    chat_id_atual = cursor.lastrowid
    conexao.commit()
    conexao.close()
    recarregar_lista_barra_lateral()
    limpar_tela_chat_visual()

def alternar_chat_selecionado(event):
    global chat_id_atual
    selecao = lista_chats_ui.curselection()
    if not selecao: return
    texto_item = lista_chats_ui.get(selecao)
    chat_id_atual = int(texto_item.split("(")[-1].replace(")", ""))
    limpar_tela_chat_visual()
    carregar_mensagens_do_chat_ativo()

def selecionar_imagem():
    global caminho_imagem_global, imagem_tk_referencia
    arv = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
    if arv:
        caminho_imagem_global = arv
        texto_central.pack_forget()
        img = Image.open(arv)
        img.thumbnail((150, 150))
        imagem_tk_referencia = ImageTk.PhotoImage(img)
        area_chat.config(state=tk.NORMAL)
        area_chat.insert(tk.END, f"\nAnexado: {os.path.basename(arv)}\n")
        area_chat.image_create(tk.END, image=imagem_tk_referencia)
        area_chat.insert(tk.END, "\n")
        area_chat.config(state=tk.DISABLED)


def enviar_mensagem(event=None):
    global caminho_imagem_global
    pergunta = entrada_texto.get().strip()
    if not pergunta and not caminho_imagem_global: return
    entrada_texto.delete(0, tk.END)
    texto_central.pack_forget()
    area_chat.config(state=tk.NORMAL)
    if pergunta: area_chat.insert(tk.END, f"\nVocê: {pergunta}\n", "usuario_estilo")
    area_chat.config(state=tk.DISABLED)
    root.update()

    # 🛡️ ESCUDO DO GITHUB: Apagou a chave física e agora puxa direto do cofre .env!
    chave_groq = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=chave_groq)

    try:
        area_chat.config(state=tk.NORMAL)
        area_chat.insert(tk.END, "\nAnalisando...", "ia_estilo")
        area_chat.config(state=tk.DISABLED)
        root.update()

        # 🧠 MODELO DE VISÃO (LLAMA 4): Mantém os colchetes com type: text estruturados!
        if caminho_imagem_global:
            with open(caminho_imagem_global, "rb") as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            model = "meta-llama/llama-4-scout-17b-16e-instruct"
            msg = [{"type": "text", "text": pergunta or "Descreva a imagem"},
                   {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]
            caminho_imagem_global = None

        # 🦾 MODELO DE CHAT (LLAMA 3.1): Corrigido para TEXTO PURO (String) sem bugar a IA!
        else:
            model = seletor_modelo.get()
            conexao = sqlite3.connect("historico_ia.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT usuario, ia FROM conversas_v2 WHERE chat_id=? ORDER BY id DESC LIMIT 4",
                           (chat_id_atual,))
            passado = cursor.fetchall()
            conexao.close()

            texto_contexto = ""
            for m in reversed(passado):
                texto_contexto += f"Usuário: {m[0]}\nAssistente: {m[1]}\n"

            # String limpa e direta sem colchetes malditos!
            msg = f"Você é o Assistente Riquelme, especialista em Minecraft e Python. Responda em no máximo duas linhas. Histórico recente do chat:\n{texto_contexto}\nPergunta atual: {pergunta}"

        res = client.chat.completions.create(model=model, messages=[{"role": "user", "content": msg}], max_tokens=250,
                                             temperature=0.1)
        txt = res.choices[0].message.content

        # 🦾 Apaga o "Analisando..." e printa o texto verde limpo
        area_chat.config(state=tk.NORMAL)
        area_chat.delete("end-2c", "end")
        area_chat.insert(tk.END, f"\n\nAssistente Riquelme: {txt}\n\n" + "-" * 50 + "\n", "ia_estilo")
        area_chat.config(state=tk.DISABLED)
        area_chat.yview(tk.END)

        conexao = sqlite3.connect("historico_ia.db")
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO conversas_v2 (chat_id, data_hora, usuario, ia) VALUES (?, ?, ?, ?)",
                       (chat_id_atual, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pergunta or "[Foto]", txt))
        conexao.commit()
        conexao.close()

    except Exception as e:
        area_chat.config(state=tk.NORMAL)
        area_chat.insert(tk.END, f"\n❌ Erro: {e}\n\n")
        area_chat.config(state=tk.DISABLED)


def abrir_janela_principal():
    global root, texto_central, area_chat, entrada_texto, lista_chats_ui, seletor_modelo
    root = tk.Tk()
    root.title("ChatGPT Pro do Mestre Riquelme")
    root.geometry("1000x650")
    root.configure(bg="#212121")
    barra_lateral = tk.Frame(root, bg="#171717", width=250)
    barra_lateral.pack(side=tk.LEFT, fill=tk.Y)
    barra_lateral.pack_propagate(False)
    tk.Button(barra_lateral, text="+ Novo Chat", font=("Arial", 11, "bold"), bg="#2f2f2f", fg="#FFFFFF", bd=0, pady=8,
              command=criar_novo_chat_sistema).pack(padx=15, pady=15, fill=tk.X)
    lista_chats_ui = tk.Listbox(barra_lateral, bg="#171717", fg="#ECECF1", bd=0, font=("Arial", 11),
                                highlightthickness=0, selectbackground="#2f2f2f")
    lista_chats_ui.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    lista_chats_ui.bind("<<ListboxSelect>>", alternar_chat_selecionado)
    area_principal = tk.Frame(root, bg="#212121")
    area_principal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    painel_topo = tk.Frame(area_principal, bg="#212121")
    painel_topo.pack(fill=tk.X, padx=20, pady=10)
    seletor_modelo = ttk.Combobox(painel_topo,
                                  values=["llama-3.1-8b-instant", "meta-llama/llama-4-scout-17b-16e-instruct"],
                                  state="readonly", width=35)
    seletor_modelo.set("llama-3.1-8b-instant")
    seletor_modelo.pack(side=tk.LEFT, padx=5)
    texto_central = tk.Label(area_principal, text="Por onde começamos?", font=("Arial", 24, "bold"), fg="#FFFFFF",
                             bg="#212121")
    texto_central.pack(pady=20)
    area_chat = scrolledtext.ScrolledText(area_principal, wrap=tk.WORD, font=("Arial", 12), bg="#212121", fg="#ECECF1",
                                          bd=0, highlightthickness=0)
    area_chat.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
    area_chat.config(state=tk.DISABLED)
    area_chat.tag_config("usuario_estilo", foreground="#FFFFFF", font=("Arial", 12, "bold"))
    area_chat.tag_config("ia_estilo", foreground="#10a37f", font=("Arial", 12))
    frame_entrada = tk.Frame(area_principal, bg="#2f2f2f", bd=0, padx=10, pady=5)
    frame_entrada.pack(padx=20, pady=20, fill=tk.X, side=tk.BOTTOM)
    tk.Button(frame_entrada, text="+", font=("Arial", 14, "bold"), fg="#b4b4b4", bg="#2f2f2f", bd=0,
              command=selecionar_imagem).pack(side=tk.LEFT, padx=5)
    entrada_texto = tk.Entry(frame_entrada, font=("Arial", 13), bg="#2f2f2f", fg="#FFFFFF", bd=0,
                             insertbackground="white")
    entrada_texto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    entrada_texto.bind("<Return>", enviar_mensagem)
    recarregar_lista_barra_lateral()
    criar_novo_chat_sistema()
    root.mainloop()


def aceitar_termos_no_banco(janela_termos):
    conexao = sqlite3.connect("historico_ia.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('termos_aceitos', 'True')")
    conexao.commit()
    conexao.close()
    janela_termos.destroy()
    abrir_janela_principal()


def exibir_tela_termos():
    banco_ia.inicializar_banco_dados()
    if banco_ia.verificar_termos_aceitos():
        abrir_janela_principal()
        return
    janela_termos = tk.Tk()
    janela_termos.title("Termos de Serviço")
    janela_termos.geometry("500x350")
    janela_termos.configure(bg="#212121")
    lbl = tk.Label(janela_termos, text="Termos de Uso - Riquelme AI", font=("Arial", 14, "bold"), fg="#FFFFFF",
                   bg="#212121")
    lbl.pack(pady=20)
    btn = tk.Button(janela_termos, text="ACEITAR E INICIAR", font=("Arial", 11, "bold"), bg="#10a37f", fg="#FFFFFF",
                    bd=0, padx=20, pady=10, command=lambda: aceitar_termos_no_banco(janela_termos))
    btn.pack(pady=40)
    janela_termos.mainloop()


if __name__ == "__main__":
    exibir_tela_termos()
