import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile
import tarfile
import os
import threading

def selecionar_arquivos():
    files = filedialog.askopenfilenames(title="Selecione os arquivos")
    entry_files.delete(0, tk.END)
    entry_files.insert(0, files)
    sugerir_melhor_formato(files)

def selecionar_diretorio():
    directory = filedialog.askdirectory(title="Selecione o diretório de saída")
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)

def atualizar_barra_progresso(progress, total, bar):
    percentage = (progress / total) * 100
    bar['value'] = percentage
    progress_label.config(text=f"Progresso: {percentage:.2f}%")
    root.update_idletasks()

def calcular_tamanho_arquivos(files):
    total_size = 0
    for file in files:
        total_size += os.path.getsize(file)
    return total_size

def sugerir_melhor_formato(files):
    tipos = [os.path.splitext(file)[1].lower() for file in files]
    if all(tipo in ['.txt', '.log', '.csv'] for tipo in tipos):
        suggestion_label.config(text="Sugestão: RLE é o melhor para arquivos de texto.")
    elif all(tipo in ['.png', '.jpg', '.jpeg'] for tipo in tipos):
        suggestion_label.config(text="Sugestão: ZIP ou TAR.GZ são boas opções para imagens.")
    elif all(tipo in ['.mp4', '.avi', '.mkv'] for tipo in tipos):
        suggestion_label.config(text="Sugestão: TAR.BZ2 é uma boa opção para vídeos.")
    else:
        suggestion_label.config(text="Sugestão: ZIP é uma opção versátil.")

def compactar_rle(files, output_file, progress_bar):
    try:
        total = len(files)
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for idx, file in enumerate(files):
                with open(file, 'rb') as in_file:
                    data = in_file.read().decode('utf-8', errors='ignore')
                    compressed_data = rle_encode(data)
                    out_file.write(f"{os.path.basename(file)}:{compressed_data}\n")
                atualizar_barra_progresso(idx + 1, total, progress_bar)
        messagebox.showinfo("Sucesso", "Arquivos compactados com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao compactar arquivos RLE: {e}")

def descompactar_rle(input_file, output_dir, progress_bar):
    try:
        with open(input_file, 'r', encoding='utf-8') as in_file:
            lines = in_file.readlines()
        total = len(lines)
        for idx, line in enumerate(lines):
            filename, compressed_data = line.strip().split(':', 1)
            data = rle_decode(compressed_data)
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(data)
            atualizar_barra_progresso(idx + 1, total, progress_bar)
        messagebox.showinfo("Sucesso", "Arquivos descompactados com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao descompactar arquivos RLE: {e}")

def rle_encode(data):
    if not data:
        return ""
    encoding = []
    i = 0

    while i < len(data):
        count = 1
        while i + 1 < len(data) and data[i] == data[i + 1]:
            i += 1
            count += 1
        encoding.append(data[i])
        encoding.append(str(count))
        i += 1

    return ''.join(encoding)

def rle_decode(data):
    if not data:
        return ""
    decoding = []
    i = 0

    while i < len(data):
        char = data[i]
        count = []
        i += 1
        while i < len(data) and data[i].isdigit():
            count.append(data[i])
            i += 1
        decoding.append(char * int(''.join(count)))

    return ''.join(decoding)

def lz77_compress(data, window_size=4096, lookahead_buffer_size=18):
    if not data:
        return []
    compressed_data = []
    i = 0
    length_data = len(data)
    
    while i < length_data:
        match_distance = 0
        match_length = 0
        buffer_end = min(i + lookahead_buffer_size, length_data)
        
        for j in range(max(0, i - window_size), i):
            length = 0
            while length < lookahead_buffer_size and i + length < length_data and data[j + length] == data[i + length]:
                length += 1
            
            if length > match_length:
                match_distance = i - j
                match_length = length
        
        if match_length > 1:
            if i + match_length < length_data:
                compressed_data.append((match_distance, match_length, data[i + match_length]))
            else:
                compressed_data.append((match_distance, match_length, ''))
            i += match_length + 1
        else:
            compressed_data.append((0, 0, data[i]))
            i += 1
    
    return compressed_data

def lz77_decompress(compressed_data):
    if not compressed_data:
        return ""
    decompressed_data = []
    
    for item in compressed_data:
        (distance, length, char) = item
        if distance > 0:
            start = len(decompressed_data) - distance
            for _ in range(length):
                decompressed_data.append(decompressed_data[start])
                start += 1
        decompressed_data.append(char)
    
    return ''.join(decompressed_data)

def compactar_lz77(files, output_file, progress_bar):
    try:
        total = len(files)
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for idx, file in enumerate(files):
                with open(file, 'rb') as in_file:
                    data = in_file.read().decode('utf-8', errors='ignore')
                    compressed_data = lz77_compress(data)
                    out_file.write(f"{os.path.basename(file)}:{compressed_data}\n")
                atualizar_barra_progresso(idx + 1, total, progress_bar)
        messagebox.showinfo("Sucesso", "Arquivos compactados com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao compactar arquivos LZ77: {e}")

def descompactar_lz77(input_file, output_dir, progress_bar):
    try:
        with open(input_file, 'r', encoding='utf-8') as in_file:
            lines = in_file.readlines()
        total = len(lines)
        for idx, line in enumerate(lines):
            filename, compressed_data = line.strip().split(':', 1)
            data = lz77_decompress(eval(compressed_data))
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(data)
            atualizar_barra_progresso(idx + 1, total, progress_bar)
        messagebox.showinfo("Sucesso", "Arquivos descompactados com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao descompactar arquivos LZ77: {e}")

def compactar_arquivos():
    files = root.tk.splitlist(entry_files.get())
    output_dir = entry_directory.get()
    formato = combo_format.get()
    
    if not files or not output_dir:
        messagebox.showerror("Erro", "Por favor, selecione os arquivos e o diretório de saída.")
        return
    
    progress_bar.pack(pady=10)
    progress_label.pack(pady=5)
    root.update_idletasks()

    total_size_before = calcular_tamanho_arquivos(files)

    def compactar():
        if formato == "zip":
            output_file = os.path.join(output_dir, "arquivos_compactados.zip")
            with zipfile.ZipFile(output_file, 'w') as zipf:
                total = len(files)
                for idx, file in enumerate(files):
                    zipf.write(file, os.path.basename(file))
                    atualizar_barra_progresso(idx + 1, total, progress_bar)
        elif formato == "tar.gz":
            output_file = os.path.join(output_dir, "arquivos_compactados.tar.gz")
            with tarfile.open(output_file, 'w:gz') as tarf:
                total = len(files)
                for idx, file in enumerate(files):
                    tarf.add(file, arcname=os.path.basename(file))
                    atualizar_barra_progresso(idx + 1, total, progress_bar)
        elif formato == "tar.bz2":
            output_file = os.path.join(output_dir, "arquivos_compactados.tar.bz2")
            with tarfile.open(output_file, 'w:bz2') as tarf:
                total = len(files)
                for idx, file in enumerate(files):
                    tarf.add(file, arcname=os.path.basename(file))
                    atualizar_barra_progresso(idx + 1, total, progress_bar)
        elif formato == "rle":
            output_file = os.path.join(output_dir, "arquivos_compactados.rle")
            compactar_rle(files, output_file, progress_bar)
        elif formato == "lz77":
            output_file = os.path.join(output_dir, "arquivos_compactados.lz77")
            compactar_lz77(files, output_file, progress_bar)
        else:
            messagebox.showerror("Erro", "Formato de compactação não suportado.")
            return

        total_size_after = os.path.getsize(output_file)
        messagebox.showinfo("Sucesso", f"Arquivos compactados com sucesso em {output_file}\nTamanho original: {total_size_before / (1024 * 1024):.2f} MB\nTamanho compactado: {total_size_after / (1024 * 1024):.2f} MB")
        progress_bar.pack_forget()
        progress_label.pack_forget()

    threading.Thread(target=compactar).start()

def descompactar_arquivos():
    input_file = filedialog.askopenfilename(title="Selecione o arquivo", filetypes=[("Todos os arquivos", "*.*")])
    output_dir = entry_directory.get()
    
    if not input_file or not output_dir:
        messagebox.showerror("Erro", "Por favor, selecione o arquivo e o diretório de saída.")
        return
    
    progress_bar.pack(pady=10)
    progress_label.pack(pady=5)
    root.update_idletasks()

    def descompactar():
        if input_file.endswith(".zip"):
            with zipfile.ZipFile(input_file, 'r') as zipf:
                total = len(zipf.namelist())
                for idx, name in enumerate(zipf.namelist()):
                    zipf.extract(name, output_dir)
                    atualizar_barra_progresso(idx + 1, total, progress_bar)
        elif input_file.endswith(".tar.gz"):
            with tarfile.open(input_file, 'r:gz') as tarf:
                members = tarf.getmembers()
                total = len(members)
                for idx, member in enumerate(members):
                    tarf.extract(member, output_dir)
                    atualizar_barra_progresso(idx + 1, total, progress_bar)
        elif input_file.endswith(".tar.bz2"):
            with tarfile.open(input_file, 'r:bz2') as tarf:
                members = tarf.getmembers()
                total = len(members)
                for idx, member in enumerate(members):
                    tarf.extract(member, output_dir)
                    atualizar_barra_progresso(idx + 1, total, progress_bar)
        elif input_file.endswith(".rle"):
            descompactar_rle(input_file, output_dir, progress_bar)
        elif input_file.endswith(".lz77"):
            descompactar_lz77(input_file, output_dir, progress_bar)
        else:
            messagebox.showerror("Erro", "Formato de descompactação não suportado.")
            return
        
        messagebox.showinfo("Sucesso", f"Arquivos descompactados com sucesso em {output_dir}")
        progress_bar.pack_forget()
        progress_label.pack_forget()

    threading.Thread(target=descompactar).start()


root = tk.Tk()
root.title("ZipMestre - Compactador e Descompactador de Arquivos")
root.geometry("600x450")


label_title = tk.Label(root, text="ZipMestre - Compactador e Descompactador de Arquivos", font=("Helvetica", 16))
label_title.pack(pady=10)

label_subtitle = tk.Label(root, text="Selecione os arquivos e o diretório de saída", font=("Helvetica", 12))
label_subtitle.pack(pady=5)


entry_files = tk.Entry(root, width=50)
entry_files.pack(pady=5)

btn_files = tk.Button(root, text="Selecionar Arquivos", command=selecionar_arquivos)
btn_files.pack(pady=5)


entry_directory = tk.Entry(root, width=50)
entry_directory.pack(pady=5)

btn_directory = tk.Button(root, text="Selecionar Diretório de Saída", command=selecionar_diretorio)
btn_directory.pack(pady=5)


suggestion_label = tk.Label(root, text="", font=("Helvetica", 10))
suggestion_label.pack(pady=5)


label_format = tk.Label(root, text="Escolha o formato de compactação:")
label_format.pack(pady=5)

combo_format = ttk.Combobox(root, values=["zip", "tar.gz", "tar.bz2", "rle", "lz77"])
combo_format.pack(pady=5)
combo_format.current(0) 


progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_label = tk.Label(root, text="Progresso: 0%")


btn_compactar = tk.Button(root, text="Compactar Arquivos", command=compactar_arquivos)
btn_compactar.pack(pady=5)

btn_descompactar = tk.Button(root, text="Descompactar Arquivo", command=descompactar_arquivos)
btn_descompactar.pack(pady=5)


root.mainloop()
