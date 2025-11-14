import reflex as rx
import subprocess
import asyncio
import logging
import sys
from typing import TypedDict, Literal

log_file_path = "titanpulse_debloat_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file_path)],
)


class DebloatOption(TypedDict):
    id: str
    name: str
    icon: str
    default: bool
    command: str


class DebloatCategory(TypedDict):
    id: str
    name: str
    icon: str
    options: list[DebloatOption]


class DebloatState(rx.State):
    theme: str = "light"
    is_running: bool = False
    progress: int = 0
    log_output: list[str] = [
        "Benvenuto in TitanPulse Debloat Tool.",
        "Seleziona le opzioni e avvia il processo.",
    ]
    total_steps: int = 0
    collapsed_categories: dict[str, bool] = {
        "gaming": False,
        "network": True,
        "cleanup": True,
        "privacy": True,
        "performance": True,
        "system": True,
        "context_menu": True,
        "ui_tweaks": True,
    }
    option_states: dict[str, bool] = {}
    debloat_categories: list[DebloatCategory] = [
        {
            "id": "gaming",
            "name": "Gaming Optimization",
            "icon": "gamepad-2",
            "options": [
                {
                    "id": "game_dvr",
                    "name": "Disabilita Game DVR",
                    "icon": "video-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU:\\System\\GameConfigStore" -Name "GameDVR_Enabled" -Value 0; Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" -Name "AllowGameDVR" -Value 0 -Force',
                },
                {
                    "id": "hags",
                    "name": "Abilita HAGS",
                    "icon": "gpu",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" -Name "HwSchMode" -Value 2 -Type DWord -Force',
                },
                {
                    "id": "game_mode",
                    "name": "Abilita Game Mode",
                    "icon": "gamepad",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\GameBar" -Name "AllowAutoGameMode" -Value 1 -Force',
                },
                {
                    "id": "nagle_algorithm",
                    "name": "Disabilita Nagle Algorithm",
                    "icon": "network",
                    "default": False,
                    "command": 'Get-NetAdapter -Physical | ForEach-Object { $iface = $_.Name; $regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\$($iface.Guid)"; Set-ItemProperty -Path $regPath -Name "TcpAckFrequency" -Value 1 -Force; Set-ItemProperty -Path $regPath -Name "TCPNoDelay" -Value 1 -Force }',
                },
                {
                    "id": "power_throttling",
                    "name": "Disabilita Power Throttling",
                    "icon": "battery-charging",
                    "default": True,
                    "command": "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR IDLEDISABLE 000; powercfg /setactive SCHEME_CURRENT",
                },
                {
                    "id": "disable_vbs",
                    "name": "Disabilita VBS",
                    "icon": "shield-off",
                    "default": False,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard" -Name "EnableVirtualizationBasedSecurity" -Value 0 -Force',
                },
                {
                    "id": "mouse_precision",
                    "name": "Ottimizza Mouse Precision",
                    "icon": "mouse",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU:\\Control Panel\\Mouse" -Name "MouseSpeed" -Value "1"; Set-ItemProperty -Path "HKCU:\\Control Panel\\Mouse" -Name "MouseThreshold1" -Value "0"; Set-ItemProperty -Path "HKCU:\\Control Panel\\Mouse" -Name "MouseThreshold2" -Value "0"',
                },
                {
                    "id": "fullscreen_optimizations",
                    "name": "Disabilita Fullscreen Optimizations",
                    "icon": "monitor",
                    "default": False,
                    "command": 'Set-ItemProperty -Path "HKCU:\\System\\GameConfigStore" -Name "GameDVR_FSEBehaviorMode" -Value 2 -Force',
                },
            ],
        },
        {
            "id": "network",
            "name": "Ottimizzazione Rete & Ping",
            "icon": "network",
            "options": [
                {
                    "id": "optimize_dns",
                    "name": "Ottimizza DNS (Cloudflare)",
                    "icon": "globe",
                    "default": True,
                    "command": 'Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -ne "Loopback Pseudo-Interface 1" } | Set-DnsClientServerAddress -ServerAddresses ("1.1.1.1","1.0.0.1")',
                },
                {
                    "id": "disable_ipv6",
                    "name": "Disabilita IPv6",
                    "icon": "wifi-off",
                    "default": False,
                    "command": "Get-NetAdapterBinding -ComponentID ms_tcpip6 | Disable-NetAdapterBinding -PassThru",
                },
                {
                    "id": "network_throttling",
                    "name": "Disabilita Network Throttling",
                    "icon": "activity",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" -Name "NetworkThrottlingIndex" -Value 0xFFFFFFFF -Force',
                },
                {
                    "id": "disable_p2p_updates",
                    "name": "Disabilita Windows Update P2P",
                    "icon": "users",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\DeliveryOptimization\\Config" -Name "DODownloadMode" -Value 0 -Force',
                },
                {
                    "id": "flush_dns",
                    "name": "Flush DNS Cache",
                    "icon": "refresh-cw",
                    "default": True,
                    "command": "ipconfig /flushdns",
                },
                {
                    "id": "disable_autotuning",
                    "name": "Disabilita Auto-Tuning Rete",
                    "icon": "sliders-horizontal",
                    "default": False,
                    "command": "netsh int tcp set global autotuninglevel=disabled",
                },
                {
                    "id": "disable_rss",
                    "name": "Disabilita RSS",
                    "icon": "rss",
                    "default": False,
                    "command": "Get-NetAdapterRss | Disable-NetAdapterRss",
                },
                {
                    "id": "disable_lso",
                    "name": "Disabilita Large Send Offload",
                    "icon": "upload-cloud",
                    "default": False,
                    "command": "Get-NetAdapterLso | Disable-NetAdapterLso",
                },
            ],
        },
        {
            "id": "cleanup",
            "name": "Pulizia & Manutenzione",
            "icon": "trash-2",
            "options": [
                {
                    "id": "clean_temp",
                    "name": "Pulisci File Temporanei",
                    "icon": "folder-x",
                    "default": True,
                    "command": "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path C:\\Windows\\Temp\\* -Recurse -Force -ErrorAction SilentlyContinue",
                },
                {
                    "id": "clean_update_cache",
                    "name": "Pulisci Windows Update Cache",
                    "icon": "package-x",
                    "default": True,
                    "command": "Stop-Service wuauserv; Remove-Item -Path C:\\Windows\\SoftwareDistribution\\Download\\* -Recurse -Force -ErrorAction SilentlyContinue; Start-Service wuauserv",
                },
                {
                    "id": "remove_prefetch",
                    "name": "Rimuovi Prefetch",
                    "icon": "fast-forward",
                    "default": False,
                    "command": "Remove-Item -Path C:\\Windows\\Prefetch\\* -Recurse -Force -ErrorAction SilentlyContinue",
                },
                {
                    "id": "empty_recycle_bin",
                    "name": "Svuota Cestino",
                    "icon": "trash",
                    "default": True,
                    "command": "Clear-RecycleBin -Force -ErrorAction SilentlyContinue",
                },
                {
                    "id": "clean_windows_logs",
                    "name": "Pulisci Windows Event Logs",
                    "icon": "file-text",
                    "default": False,
                    "command": "wevtutil cl System; wevtutil cl Application; wevtutil cl Security; wevtutil cl Setup",
                },
                {
                    "id": "remove_thumbnail_cache",
                    "name": "Rimuovi Thumbnail Cache",
                    "icon": "image-off",
                    "default": True,
                    "command": "Stop-Process -Name explorer -Force; Remove-Item -Path $env:LOCALAPPDATA\\Microsoft\\Windows\\Explorer\\thumbcache_*.db -Force -ErrorAction SilentlyContinue; Start-Process explorer",
                },
                {
                    "id": "disable_hibernation",
                    "name": "Disabilita Hibernation File",
                    "icon": "power-off",
                    "default": True,
                    "command": "powercfg /hibernate off",
                },
                {
                    "id": "dism_cleanup",
                    "name": "Esegui DISM Cleanup",
                    "icon": "hard-drive",
                    "default": False,
                    "command": "DISM /Online /Cleanup-Image /RestoreHealth",
                },
                {
                    "id": "sfc_scan",
                    "name": "Esegui SFC Scannow",
                    "icon": "scan-line",
                    "default": False,
                    "command": "sfc /scannow",
                },
            ],
        },
        {
            "id": "privacy",
            "name": "Privacy & Telemetria",
            "icon": "shield-check",
            "options": [
                {
                    "id": "disable_telemetry",
                    "name": "Disabilita Telemetria Microsoft",
                    "icon": "shield-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Name "AllowTelemetry" -Value 0 -Force',
                },
                {
                    "id": "block_cortana",
                    "name": "Blocca Cortana",
                    "icon": "mic-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" -Name "AllowCortana" -Value 0 -Force',
                },
                {
                    "id": "disable_timeline",
                    "name": "Disabilita Timeline Attività",
                    "icon": "clock-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" -Name "EnableActivityFeed" -Value 0 -Force',
                },
                {
                    "id": "block_feedback",
                    "name": "Blocca Feedback Windows",
                    "icon": "message-square-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Siuf\\Rules" -Name "NumberOfSIUFInPeriod" -Value 0 -Force',
                },
                {
                    "id": "disable_start_ads",
                    "name": "Disabilita Pubblicità Start Menu",
                    "icon": "megaphone-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SilentInstalledAppsEnabled" -Value 0; Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "ContentDeliveryAllowed" -Value 0',
                },
                {
                    "id": "disable_suggestions",
                    "name": "Disabilita Suggestions & Tips",
                    "icon": "lightbulb-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SubscribedContent-338389Enabled" -Value 0; Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SystemPaneSuggestionsEnabled" -Value 0',
                },
                {
                    "id": "disable_advertising_id",
                    "name": "Disabilita Advertising ID",
                    "icon": "ad-circle-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" -Name "Enabled" -Value 0',
                },
                {
                    "id": "block_location",
                    "name": "Blocca Location Tracking",
                    "icon": "map-pin-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" -Name "DisableLocation" -Value 1 -Force',
                },
            ],
        },
        {
            "id": "performance",
            "name": "Performance & Servizi",
            "icon": "rocket",
            "options": [
                {
                    "id": "disable_search_indexing",
                    "name": "Disabilita Windows Search Indexing",
                    "icon": "search-slash",
                    "default": False,
                    "command": "Stop-Service -Name WSearch; Set-Service -Name WSearch -StartupType Disabled",
                },
                {
                    "id": "disable_animations",
                    "name": "Disabilita Animazioni Visuali",
                    "icon": "eye-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name "VisualFXSetting" -Value 3; Set-ItemProperty -Path "HKCU:\\Control Panel\\Desktop\\WindowMetrics" -Name "MinAnimate" -Value "0"',
                },
                {
                    "id": "high_performance_mode",
                    "name": "Modalità Alte Prestazioni",
                    "icon": "zap",
                    "default": True,
                    "command": "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
                },
                {
                    "id": "manual_services",
                    "name": "Servizi Superflui in Manuale",
                    "icon": "sliders-horizontal",
                    "default": False,
                    "command": 'Set-Service -Name "SysMain" -StartupType Manual; Set-Service -Name "DiagTrack" -StartupType Manual',
                },
                {
                    "id": "disable_print_spooler",
                    "name": "Disabilita Servizio Stampa",
                    "icon": "printer",
                    "default": False,
                    "command": "Stop-Service -Name Spooler; Set-Service -Name Spooler -StartupType Disabled",
                },
                {
                    "id": "disable_fax_service",
                    "name": "Disabilita Servizio Fax",
                    "icon": "file-x",
                    "default": False,
                    "command": "Stop-Service -Name Fax; Set-Service -Name Fax -StartupType Disabled",
                },
                {
                    "id": "optimize_trim",
                    "name": "Ottimizza SSD TRIM",
                    "icon": "disc-2",
                    "default": True,
                    "command": "fsutil behavior set DisableDeleteNotify 0",
                },
            ],
        },
        {
            "id": "system",
            "name": "Sistema & Sicurezza",
            "icon": "shield",
            "options": [
                {
                    "id": "restore_point",
                    "name": "Crea Punto di Ripristino",
                    "icon": "history",
                    "default": True,
                    "command": 'Checkpoint-Computer -Description "TitanPulse Debloat" -RestorePointType "MODIFY_SETTINGS"',
                },
                {
                    "id": "disable_defender",
                    "name": "Disabilita Windows Defender",
                    "icon": "shield-alert",
                    "default": False,
                    "command": "Set-MpPreference -DisableRealtimeMonitoring $true",
                },
                {
                    "id": "disable_uac",
                    "name": "Disabilita UAC (User Account Control)",
                    "icon": "user-x",
                    "default": False,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "EnableLUA" -Value 0 -Force',
                },
                {
                    "id": "disable_smartscreen",
                    "name": "Disabilita SmartScreen",
                    "icon": "shield-half",
                    "default": False,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" -Name "EnableSmartScreen" -Value 0 -Force',
                },
                {
                    "id": "disable_autoupdate",
                    "name": "Disabilita Aggiornamenti Automatici",
                    "icon": "arrow-down-circle",
                    "default": False,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "NoAutoUpdate" -Value 1 -Force',
                },
                {
                    "id": "update_windows",
                    "name": "Forza Aggiornamento Windows",
                    "icon": "arrow-up-circle",
                    "default": False,
                    "command": "Install-Module PSWindowsUpdate -Force -AcceptLicense; Get-WindowsUpdate -Install -AcceptAll",
                },
            ],
        },
        {
            "id": "context_menu",
            "name": "Pulizia Menu Contestuale",
            "icon": "mouse-pointer-click",
            "options": [
                {
                    "id": "remove_share_context",
                    "name": "Rimuovi 'Condividi'",
                    "icon": "share-2",
                    "default": True,
                    "command": 'Remove-Item -Path "HKCR:\\*\\shellex\\ContextMenuHandlers\\ModernSharing" -Force -Recurse -ErrorAction SilentlyContinue',
                },
                {
                    "id": "remove_3dprint_context",
                    "name": "Rimuovi 'Stampa 3D'",
                    "icon": "printer",
                    "default": True,
                    "command": 'Remove-Item -Path "HKCR:\\SystemFileAssociations\\.3mf\\Shell\\Print3D" -Force -Recurse -ErrorAction SilentlyContinue',
                },
                {
                    "id": "remove_paint3d_context",
                    "name": "Rimuovi 'Modifica con Paint 3D'",
                    "icon": "brush",
                    "default": True,
                    "command": 'Remove-Item -Path "HKCR:\\SystemFileAssociations\\.bmp\\Shell\\3D Edit" -Force -Recurse -ErrorAction SilentlyContinue',
                },
                {
                    "id": "remove_edit_photos_context",
                    "name": "Rimuovi 'Modifica con Foto'",
                    "icon": "image",
                    "default": True,
                    "command": 'Remove-Item -Path "HKCR:\\SystemFileAssociations\\.bmp\\Shell\\Edit" -Force -Recurse -ErrorAction SilentlyContinue',
                },
                {
                    "id": "add_copy_to_folder_context",
                    "name": "Aggiungi 'Copia in'",
                    "icon": "copy",
                    "default": False,
                    "command": 'New-Item -Path "HKCR\\AllFilesystemObjects\\shellex\\ContextMenuHandlers\\CopyTo" -Value "{C2FBB630-2971-11d1-A18C-00C04FD75D13}" -Force',
                },
                {
                    "id": "add_move_to_folder_context",
                    "name": "Aggiungi 'Sposta in'",
                    "icon": "move",
                    "default": False,
                    "command": 'New-Item -Path "HKCR\\AllFilesystemObjects\\shellex\\ContextMenuHandlers\\MoveTo" -Value "{C2FBB631-2971-11d1-A18C-00C04FD75D13}" -Force',
                },
            ],
        },
        {
            "id": "ui_tweaks",
            "name": "UI/UX Tweaks",
            "icon": "wand-2",
            "options": [
                {
                    "id": "show_file_extensions",
                    "name": "Mostra Estensioni File",
                    "icon": "file-type",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name "HideFileExt" -Value 0',
                },
                {
                    "id": "show_hidden_files",
                    "name": "Mostra File Nascosti",
                    "icon": "folder-open",
                    "default": False,
                    "command": 'Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name "Hidden" -Value 1',
                },
                {
                    "id": "disable_lockscreen_blur",
                    "name": "Disabilita Blur Scherm. Accesso",
                    "icon": "eye",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" -Name "DisableAcrylicBackgroundOnLogon" -Value 1 -Force',
                },
                {
                    "id": "classic_file_explorer",
                    "name": "Usa Esplora File Classico (Win10)",
                    "icon": "folder-closed",
                    "default": False,
                    "command": 'New-ItemProperty -Path "HKCU\\Software\\Classes\\CLSID\\{d93ed569-3b3e-4bff-8355-3c44f6a52bb5}\\InprocServer32" -Name "(Default)" -Value "" -PropertyType String -Force',
                },
                {
                    "id": "disable_widgets",
                    "name": "Disabilita Widget",
                    "icon": "layout-grid",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name "TaskbarDa" -Value 0',
                },
                {
                    "id": "disable_chat",
                    "name": "Disabilita Chat (Teams) da Taskbar",
                    "icon": "message-circle-off",
                    "default": True,
                    "command": 'Set-ItemProperty -Path "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name "TaskbarMn" -Value 0',
                },
            ],
        },
    ]

    def _initialize_option_states(self):
        """Initializes the option_states dictionary if it's empty."""
        if not self.option_states:
            new_states = {}
            for category in self.debloat_categories:
                for option in category["options"]:
                    new_states[option["id"]] = option["default"]
            self.option_states = new_states

    @rx.event
    def on_load(self):
        self._initialize_option_states()
        return

    @rx.event
    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"

    def _run_command(self, command: str) -> str:
        try:
            kwargs = {
                "capture_output": True,
                "text": True,
                "check": True,
                "shell": True,
            }
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            result = subprocess.run(f'powershell -Command "{command}"', **kwargs)
            return (
                result.stdout.strip()
                if result.stdout
                else "Comando eseguito con successo."
            )
        except subprocess.CalledProcessError as e:
            logging.exception(e)
            error_message = f"Errore: {(e.stderr.strip() if e.stderr else 'Unknown PowerShell error')}"
            return error_message

    async def _update_progress_and_log(self, message: str, increment: int):
        async with self:
            self.log_output.append(message)
            logging.info(message)
            if self.total_steps > 0:
                current_progress = self.progress + int(
                    increment / self.total_steps * 100
                )
                self.progress = min(current_progress, 100)

    @rx.event
    def toggle_category(self, category_id: str):
        self.collapsed_categories[category_id] = not self.collapsed_categories[
            category_id
        ]

    @rx.event
    def toggle_option(self, option_id: str):
        self.option_states[option_id] = not self.option_states[option_id]

    @rx.event(background=True)
    async def start_debloat(self):
        async with self:
            if self.is_running:
                return
            self.is_running = True
            self.progress = 0
            self.log_output = ["Avvio processo di debloat..."]
            logging.info("=" * 20 + " New Debloat Session " + "=" * 20)
            selected_options = []
            for category in self.debloat_categories:
                for option in category["options"]:
                    if self.option_states.get(option["id"]):
                        selected_options.append(option)
            selected_options.sort(key=lambda opt: opt["id"] != "restore_point")
            self.total_steps = len(selected_options)
        await asyncio.sleep(0.1)
        if self.total_steps == 0:
            async with self:
                self.log_output.append(
                    "Nessuna opzione selezionata. Processo annullato."
                )
                self.is_running = False
            return
        for option in selected_options:
            await self._update_progress_and_log(f"Esecuzione: {option['name']}...", 0)
            output = self._run_command(option["command"])
            await self._update_progress_and_log(f"Risultato: {output}", 1)
            await asyncio.sleep(0.2)
        async with self:
            self.progress = 100
            self.log_output.append("Processo di debloat completato.")
            logging.info("Processo di debloat completato.")
            self.is_running = False