# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 16:09:27 2023

@author: juanh
"""

from multiprocessing import Pool

import functions


threads_tracking = set()


pool = Pool()

commands_por_palabra = ["Agregar palabra",
                        "Quitar palabra",
                        "Imprimir palabras",
                        "Buscar hilos",
                        "Limpiar palabras",
                        "Descargar hilo",
                        "Descargar todos los hilos",
                        "Seguir todos los hilos",
                        "Imprimir todos los hilos",
                        "Regresar"]

commands_menu_principal = ["Buscar hilos con palabras clave",
                           "Track hilo",
                           "Descarga hilo",
                           "Imprime hilos seguidos",
                           "Terminar hilos",
                           "Salir"]


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


def track_hilo(tablero, hilo):
    if hilo not in threads_tracking:
        pool.apply_async(
            func=functions.track_thread,
            args=(tablero, hilo),
            callback=callback_exito,
            error_callback=callback_error)
        threads_tracking.add(hilo)


def track_hilo_manual():
    t = input("Tablero: ")
    h = input("Hilo a seguir: ")
    if h not in threads_tracking:
        track_hilo(t, h)


def track_hilos(hilos):
    t = input("Tablero: ")
    for hilo in hilos:
        print(f"Siguiento hilo {hilo}")
        track_hilo(t, hilo)
        hilos.remove(hilo)


def imprime_hilos(hilos):
    if len(hilos) == 0:
        print("No hay hilos")
    else:
        print("Hilos: ")
        imprime_elementos(hilos)
    print()


def agregar_palabra(palabras):
    p = input("Palabra: ")
    palabras.add(p)


def eliminar_palabra(palabras):
    p = input("Palabra: ")
    if p in palabras:
        palabras.remove(p)

    else:
        print(f"{p} no se encuentra en el conjunto")


def buscar_hilos(hilos, palabras):
    if len(palabras) == 0:
        print("No hay palabras agregadas.")
        return

    tablero = input("Tablero: ")
    if functions.exists_board_by_id(tablero):
        h = functions.get_threads_by_keywords(tablero, palabras)

        if len(h) == 0:
            print("No se han encontrado hilos con esos palabras")

        else:
            print(f"Se han encontrado {len(h)} hilos")
            s = input("Agregar? (S/n)")
            if s != 'N' and s != 'n':
                hilos.update(h)
                print("Se agregaron los hilos")
            else:
                print("No se agregó nada")


def descargar_hilo(tablero, hilo):
    pool.apply_async(
        func=functions.download_thread,
        args=(tablero, hilo),
        callback=callback_exito,
        error_callback=callback_error
        )


def salir():
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


def descargar_hilo_manual(hilos):
    if len(hilos) == 0:
        print("No hay hilos")
        return

    print("Están registrados los siguientes hilos:")
    imprime_elementos(hilos)

    hilo = input("Id hilo a descargar: ")
    tablero = input("Tablero: ")
    descargar_hilo(hilo)
    hilos.remove(hilo)


def descargar_todos_hilos(hilos):
    for hilo in hilos:
        if hilo not in threads_tracking:
            print(f"Descargando hilo {hilo}")
            descargar_hilo(hilo)
    agregar_hilos_seguidos(hilos)
    limpiar_conjunto(hilos)


def limpiar_conjunto(conjunto):
    conjunto.clear()


def limpiar(elementos):
    s = input(f"""Se van a eliminar {len(elementos)} \
        elementos, continuar? [S/n]""")
    if s != 'N' and s != 'n':
        limpiar_conjunto(elementos)
        print("Se eliminaron los elementos")
        return

    print("No se eliminó nada")


def imprime_informacion_hilo(hilo):
    no = hilo['no']
    sub = hilo['sub'] if 'sub' in hilo else 'No subject'
    com = hilo['com'] if 'com' in hilo else 'No comment'


def informacion_hilo_menu():
    imprime_hilos(threads_tracking)
    s = input("Sobre qué hilo quieres inforamción: ")
    
    # Stupid error. Pls fix later.
    tablero = input("Tablero: ")

    if s in threads_tracking:
        hilo = functions.get_thread_by_id(tablero, hilo)
        imprime_informacion_hilo(hilo)
    else:
        print(f"El hilo {s} no se está siguiendo")


def se_sigue_hilo():
    imprime_hilos()
    s = input("Hilo: ")
    return s in threads_tracking


def buscar_hilos_por_palabras_menu():
    palabras = set()
    hilos_tmp = set()
    while True:
        imprime_menu(commands_por_palabra)
        seleccion = input("Selección: ")
        if seleccion == '1':
            agregar_palabra(palabras)

        elif seleccion == '2':
            eliminar_palabra(palabras)

        elif seleccion == '3':
            imprime_elementos(palabras)

        elif seleccion == '4':
            buscar_hilos(hilos_tmp, palabras)

        elif seleccion == '5':
            limpiar_conjunto(palabras)

        elif seleccion == '6':
            descargar_hilo_manual(hilos_tmp)

        elif seleccion == '7':
            descargar_todos_hilos(hilos_tmp)

        elif seleccion == '8':
            track_hilos(hilos_tmp)

        elif seleccion == '9':
            imprime_hilos(hilos_tmp)

        elif seleccion == '0':
            break


def descargar_hilo_principal():
    hilo = input("Hilo: ")
    tablero = input("Tablero: ")
    print(f"Intentando descargar {hilo} en /{tablero}/")
    descargar_hilo(tablero, hilo)


def main():
    while True:
        imprime_menu(commands_menu_principal)
        seleccion = input("Selección: ")
        if seleccion == '1':
            buscar_hilos_por_palabras_menu()

        elif seleccion == '2':
            track_hilo_manual()

        elif seleccion == '3':
            descargar_hilo_principal()

        elif seleccion == '4':
            imprime_hilos(threads_tracking)

        # Todo
        elif seleccion == '5':
            terminar_hilo()

        elif seleccion == '6':
            informacion_hilo_menu()

        elif seleccion == '0':
            salir()
            break


if __name__ == '__main__':
    main()
