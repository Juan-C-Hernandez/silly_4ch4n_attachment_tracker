# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 16:09:27 2023

@author: juanh
"""

from multiprocessing import Pool

import functions


threads_tracking = set()


pool = Pool()

commands_por_palabra = ["Agregar palabra", "Quitar palabra", "Imprimir palabras",
                        "Buscar hilos", "Limpiar palabras", "Descargar hilo",
                        "Descargar todos los hilos", "Imprimir todos los hilos",
                        "Regresar"]

commands_menu_principal = ["Buscar hilos con palabras clave", "Track hilo", "Imprime hilos seguidos", "Salir"]


def callback_exito(thread_id):
    print(f"{thread_id} se ha descargado con exito\n")
    return
        

def callback_error(error):
    print(f"Ocurrio un error al descargar hilo: {error}\n")


def agregar_hilos_seguidos(hilos):
    global threads_tracking
    threads_tracking.update(hilos)
    

def imprime_elementos(lista):
    for i, item in enumerate(lista):
        print(f"{i + 1}. {item}")
        
        
def imprime_menu(commands):
    if not len(commands):
        print("No hay elementos en el menu principal")
        return
    
    imprime_elementos(commands)
    

def track_hilo():
    t = input("Tablero: ")
    h = input("Hilo a seguir: ")
    if h not in threads_tracking:
        pool.apply_async(func=functions.track_thread, args=(t, h), callback=callback_exito, error_callback=callback_error)
        threads_tracking.add(h)


def imprime_hilos_seguidos():
    if len(threads_tracking) == 0:
        print("No hay hilos")
    else:
        imprime_elementos(threads_tracking)
    print()


def buscar_hilos_por_palabras_menu():
    palabras = set()
    hilos_tmp = set()
    tablero = ''
    while True:
        imprime_menu(commands_por_palabra)
        
        seleccion = input("Selección: ")
        
        if seleccion == '1':
            palabra = input("Palabra: ")
            palabras.add(palabra)
        
        elif seleccion == '2':
            palabra = input("Palabra: ")
            
            if palabra in palabras:
                palabras.remove(palabra)
            
            else:
                print(f"{palabra} no se encuentra en las palabras")
        
        elif seleccion == '3':
            imprime_elementos(palabras)
        
        elif seleccion == '4':            
            if len(palabras) == 0:
                print("No hay palabras agregadas.")
                continue
            
            tablero = input("Tablero: ")
            
            if functions.exists_board_by_id(tablero):
                hilos = functions.get_threads_by_keywords(tablero, palabras)
                
                if len(hilos) == 0:
                    print("No se han encontrado hilos con esos palabras")
                
                else:
                    print(f"Se han encontrado {len(hilos)} hilos")
                    s = input("Agregar? (S/n)")
                    if s != 'N' and s != 'n':
                        hilos_tmp.update(hilos)
                        print("Se agregaron los hilos")
                    else:
                        print("No se agregó nada")
        
        elif seleccion == '5':
            palabras.clear()
            
        elif seleccion == '6':
            if len(hilos_tmp) == 0:
                print("No hay hilos")
                continue
            
            for i, hilo in enumerate(hilos_tmp):
                print(f"{i}. {hilo}")
                
            hilo = input("Id hilo a descargar: ")
            pool.apply_async(func=functions.download_thread, args=(tablero, hilo), callback=callback_exito, error_callback=callback_error)
            hilos_tmp.remove(hilo)
            
        elif seleccion == '7':
            for hilo in hilos_tmp:
                if hilo not in threads_tracking:
                    print(f"Descargando hilo {hilo}")
                    pool.apply_async(func=functions.download_thread, args=(tablero, hilo), callback=callback_exito, error_callback=callback_error)
            agregar_hilos_seguidos(hilos_tmp)
            hilos_tmp.clear()
                
        elif seleccion == '8':
            if len(threads_tracking) == 0:
                print("No hay hilos")
                continue
            
            print("Hilos seguidos")
            for i, hilo in enumerate(threads_tracking):
                print(f"{i}. {hilo} - {type(hilo)}")
                
        elif seleccion == '0':
            break


def main():
    while True:
        imprime_menu(commands_menu_principal)
        seleccion = input("Selección: ")
        if seleccion == '1':
            buscar_hilos_por_palabras_menu()
        
        elif seleccion == '2':
            track_hilo()
            
        elif seleccion == '3':
            imprime_hilos_seguidos()
            
        elif seleccion == '0':
            break
    
    print("Se ha salido del menu principal.")
    s = input("Esperar a que terminen de ejecutarse los procesos? [S/n]")
    if s == 'N' or s == 'n':
        pool.terminate()
        print("Se han detenido todos los procesos")
        
    else:
        pool.close()
        print("Esperando procesos...")
        pool.join()
        print("Todos los procesos se han terminado.")
    
    print("Saliendo")
        
if __name__ == '__main__':
    main()
