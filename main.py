import requests
import json
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import messagebox
from pyperclip import copy

HEARDERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"}
mangas_info = 'mangs.json'
mangas_url = 'mangas.txt'
MANGAS_LER = 'capitulos para ler.json'


def atualiza_mangs(data, manga_novo, mangas_info):
    data.update(manga_novo)
    with open(mangas_info, 'r+') as file:
        json.dump(data, file, indent=1)


def verify_last_chaper(data, last_chapter, name_manga, manga_novo):
    try:
        if last_chapter > data[name_manga]['ultimo_capitulo']:
            with open(MANGAS_LER, 'r') as file:
                file_data = json.load(file)
                file_data.update(manga_novo)
            with open(MANGAS_LER, 'w') as file:
                json.dump(file_data, file, indent=1)

            atualiza_mangs(data, manga_novo, mangas_info)
            messagebox.showinfo(title='Capitulo novo !', message=f'Capitulo novo de: {name_manga}')
        else:
            return 0
    except json.decoder.JSONDecodeError:
        print('json.decoder.JSONDecodeError')
        with open(MANGAS_LER, 'r+') as file:
            json.dump(manga_novo, file, indent=1)
        messagebox.showinfo(title='Capitulo novo !', message=f'Capitulo novo de: {name_manga}')
        
        atualiza_mangs(data, manga_novo, mangas_info)

    except KeyError:
        print('key error')
        #data.update(manga_novo)
        with open(MANGAS_LER, 'r') as file:
            #json.dump(manga_novo, file, indent=1)
            file_data = json.load(file)
            file_data.update(manga_novo)
            with open(MANGAS_LER, 'w') as file:
                json.dump(file_data, file, indent=1)

        messagebox.showinfo(title='Capitulo novo !', message=f'Capitulo novo de: {name_manga}')

        atualiza_mangs(data, manga_novo, mangas_info)

    else:
        atualiza_mangs(data, manga_novo, mangas_info)


def cria_manga(url):

    request = requests.get(url,headers=HEARDERS)
    request.raise_for_status()

    soup = BeautifulSoup(request.content, 'html.parser')
    try:
        last_chapter = (soup.find('a', {'class':"chapter-name text-nowrap"}).get_text())
        last_chapter_index = last_chapter.index("r")

        last_chapter = last_chapter[1 + last_chapter_index:]

        last_chapter = [i for i in last_chapter if i in '0123456789.-']
        last_chapter = ''.join(last_chapter)

    except AttributeError:
        print(f'Pagina do manga não enctrado:\nurl: {url}')
        return 0

    print(soup.find('div', class_='story-info-right').h1.getText())
    last_chapter = float(last_chapter)
    name_manga = soup.find('div', class_='story-info-right').h1.getText()
    manga_novo = {name_manga: {
            'ultimo_capitulo':last_chapter,
            'capitulo_anterior':'',
            'url':url
            }}
    try:
        with open(mangas_info,'r+') as file:
            data = json.load(file)

    except json.decoder.JSONDecodeError:
        with open(mangas_info, 'w') as file:
            data = json.dump(manga_novo, file, indent=1)

    else:
        verify_last_chaper(data, last_chapter, name_manga, manga_novo)   
    finally:
        mangas_para_ler()


def ultimo_chap(event):
  """Show the last chapter of the manga selected in the listbox"""
  selected = lista_mangas.curselection()
  manga_name = lista_mangas.get(selected)

  with open (mangas_info) as mangas:    
    mangas = json.load(mangas)

  ultimo_cap = mangas[manga_name]['ultimo_capitulo']
  procura_ult_entry.delete(0, END)
  procura_ult_entry.insert(0, ultimo_cap)
  copy(mangas[manga_name]['url'])


def mangas_para_ler():
    lista_mangas_ler.delete(0, END)
    try:
        with open(MANGAS_LER, 'r') as mangas:
            mangas_ler = json.load(mangas)
            manga_keys = [manga for manga in list(mangas_ler)]
    except json.JSONDecodeError:
        return 0


    for manga in manga_keys:
        lista_mangas_ler.insert(END, manga)
        lista_mangas_ler.insert(END, mangas_ler[manga]['url'])
        lista_mangas_ler.insert(END, '')


def atualiza_mangas():
    try:
        with open(mangas_url,'r') as f:
            mangas = f.readlines()
    except FileNotFoundError:
        print("Nenhum manga encontrado")
    else:
        for manga in mangas:
            cria_manga(manga.strip())
            print('finalizou')         
            print(f'url:{manga}')
            mangas_para_ler()
    finally:    
        mangas_para_ler()
        messagebox.showinfo(title="Finalizou atualização", message='Finalizado atualização')



def keys_listener(event):
    match event.char:
        case 'r':
            atualiza_mangas()
            return 0
        case 'a':
            mangas_para_ler()
            return print("Atualizado lista de mangas")
        case 'd':
            deleta_manga()


def copy_to_clipboard(event):
    """Copy to clipboard on click"""
    selected = lista_mangas_ler.curselection()
    #pyperclip
    copy(lista_mangas_ler.get(selected))


def limpa_mangas():
    with open(MANGAS_LER, 'w') as file:
        file.truncate()
    mangas_para_ler()


def atualiza_lista_mangas():
    lista_mangas.delete(0, END)
    for manga in mangas:        
        lista_mangas.insert(END, manga)


def deleta_manga():
    manga = lista_mangas.get(lista_mangas.curselection())
    print(lista_mangas.curselection()[0])
    if messagebox.askyesno(title="Confirma exclusão ?", message=f"Excluir o manga: {manga}?"):
        
        # Abre arquivos
        with open(mangas_info, 'r') as mangas_json:
            mangas_json = json.load(mangas_json)
        
        with open(mangas_url, 'r') as url_mangas:
            urls = url_mangas.readlines()
        
        #Encontra url do manga, para excluir do arquivo de urls primeiro
        manga_url = f"{mangas_json[manga]['url']}\n"
        try:
            urls.remove(manga_url)
            with open(mangas_url, 'w') as file:            
                file.writelines(urls)
        except ValueError:
            pass

        print("Realizando a exclusão...")        
        mangas_json.pop(manga)                

        with open(mangas_info, 'w') as file:
            json.dump(mangas_json, file, indent=1)                    

        atualiza_lista_mangas()
        
        return print(f"{manga} excluido com sucesso !")
            

#Window
window = Tk()
window.title("Atualiza Manga")
window.config(padx=20, pady=10)

window.bind("<Key>", keys_listener)

#Buttons
atualiza_caps_button = Button(text='Atualiza Capitulos',command=atualiza_mangas)
atualiza_caps_button.grid(column=0,row=1)

delete_button = Button(text='Limpa lista', command=limpa_mangas)
delete_button.grid(column=1, row=1)

#entrys
procura_ult_entry = Entry(width=10)
procura_ult_entry.grid(column=0, row=3, columnspan=2, ipady=5, pady=3)

#Labels
title_label = Label(text='Procura Mangas')
title_label.grid(column=0, row=0,columnspan=2,pady=10)

#listbox todos mangas
lista_mangas = Listbox(window, width=60, height=20)
try:
    with open (mangas_info) as mangas:
        mangas = json.load(mangas)
except json.decoder.JSONDecodeError:
    pass
else:
    atualiza_lista_mangas()
lista_mangas.grid(column=0,row=2,)
lista_mangas.bind('<<ListboxSelect>>', ultimo_chap)

#listbox mangas para ler
lista_mangas_ler = Listbox(window, width=60, height=20)
lista_mangas_ler.grid(column=1, row=2,padx=10)
lista_mangas_ler.bind('<<ListboxSelect>>', copy_to_clipboard)

mangas_para_ler()

window.mainloop()
