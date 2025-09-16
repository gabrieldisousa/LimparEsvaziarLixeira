import ctypes
import sys
import time
import winreg
import win32api
import win32con

# Constantes para notificação do registro
REG_NOTIFY_CHANGE_NAME = 0x00000001
REG_NOTIFY_CHANGE_LAST_SET = 0x00000004

# Caminho no Registro da Lixeira
chave = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\CLSID\{645FF040-5081-101B-9F08-00AA002F954E}"

# Constantes para SHEmptyRecycleBin
SHERB_NOCONFIRMATION = 0x00000001
SHERB_NOPROGRESSUI = 0x00000002
SHERB_NOSOUND = 0x00000004

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    params = " ".join([f'"{x}"' for x in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()

def restaurar_lixeira():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave, 0, winreg.KEY_SET_VALUE) as reg:
            winreg.SetValueEx(reg, None, 0, winreg.REG_SZ, "Lixeira")
            print("[i] Nome da Lixeira restaurado para 'Lixeira'.")
    except Exception as e:
        print("[x] Erro ao restaurar o nome da Lixeira:", e)

def limpar_lixeira():
    try:
        resultado = ctypes.windll.shell32.SHEmptyRecycleBinW(
            None, None,
            SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
        )
        if resultado == 0:
            print("[✓] Lixeira esvaziada com sucesso.")
        elif resultado == 0x8000FFFF:
            print("[!] A Lixeira já está vazia.")
        else:
            print(f"[x] Código de retorno ao esvaziar: {resultado}")
    except Exception as e:
        print("[x] Erro ao esvaziar a Lixeira:", e)

def monitorar_lixeira():
    try:
        reg_handle = win32api.RegOpenKeyEx(
            win32con.HKEY_CURRENT_USER,
            chave,
            0,
            win32con.KEY_NOTIFY
        )

        print("👁️  Monitorando alterações da Lixeira... Pressione Ctrl+C para sair.")

        while True:
            # Aguarda até que ocorra alteração no valor da chave (nome)
            win32api.RegNotifyChangeKeyValue(
                reg_handle,
                False,
                REG_NOTIFY_CHANGE_LAST_SET,
                None,
                False
            )
            print("\n[⚠] Alteração detectada na Lixeira.")
            restaurar_lixeira()
            limpar_lixeira()

    except KeyboardInterrupt:
        print("\n[🛑] Monitoramento encerrado pelo usuário.")
    except Exception as e:
        print("[x] Erro geral:", e)

if __name__ == "__main__":
    if not is_admin():
        print("[!] Privilégio de administrador necessário. Reiniciando como administrador...")
        run_as_admin()

    # Restaurar e limpar antes de iniciar o monitoramento
    restaurar_lixeira()
    limpar_lixeira()

    monitorar_lixeira()
