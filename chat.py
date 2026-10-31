
import itertools
import sys
import threading
import time

from src.agent import TeoAgent


def show_loading(stop_event):
    for dots in itertools.cycle([".", "..", "..."]):
        if stop_event.is_set():
            break

        sys.stdout.write(f"\rTéo está pensando{dots}   ")
        sys.stdout.flush()

        if stop_event.wait(0.5):
            break

    sys.stdout.write("\r" + " " * 35 + "\r")
    sys.stdout.flush()


def main():
    agent = TeoAgent()

    print("Téo: Oi! Como posso te ajudar?")

    while True:
        message = input("\nVocê: ").strip()

        if message.lower() in ["sair", "exit", "quit"]:
            print("Téo: Até mais!")
            break

        stop_event = threading.Event()
        loading = threading.Thread(
            target=show_loading,
            args=(stop_event,),
            daemon=True
        )

        start = time.perf_counter()
        loading.start()

        try:
            answer = agent.chat(message)
        finally:
            stop_event.set()
            loading.join()

        elapsed = time.perf_counter() - start

        print(f"\nTéo: {answer}")
        print(f"\nTempo de resposta: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
