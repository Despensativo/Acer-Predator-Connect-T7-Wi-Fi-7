#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logger_t7.py - Logger Centralizado de Operacoes
Acer Predator Connect T7 & X7
Grava relatorios de execucao, comandos, retornos, sucessos e erros na Area de Trabalho.
"""

import os
import sys
import platform
import datetime

def get_desktop_dir():
    # Caminho confiavel da Area de Trabalho no Windows e outros SOs
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        cand = os.path.join(userprofile, "Desktop")
        if os.path.isdir(cand):
            return cand
    home = os.path.expanduser("~")
    cand = os.path.join(home, "Desktop")
    if os.path.isdir(cand):
        return cand
    return home

def get_log_paths():
    desktop = get_desktop_dir()
    p1 = os.path.join(desktop, "LOG_PREDATOR_T7.txt")
    p2 = os.path.join(desktop, "Acer-Predator-Connect-T7", "log_execucao_t7.txt")
    return [p1, p2]

def log_event(action, message, status="INFO", details=None):
    """
    Grava evento nos arquivos de log com data, hora, acao e detalhes.
    status: INFO, OK, AVISO, ERRO
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{now}] [{status:<5}] [{action}] {message}\n"
    if details:
        entry += "  Detalhes:\n"
        for line in str(details).splitlines():
            entry += f"    {line}\n"

    for lp in get_log_paths():
        try:
            os.makedirs(os.path.dirname(lp), exist_ok=True)
            with open(lp, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

def log_init_session(tool_name="Predator T7 Management Suite"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = "=" * 80 + "\n"
    header = (
        sep +
        f"  SESSAO INICIADA: {tool_name}\n" +
        f"  Data/Hora      : {now}\n" +
        f"  Sistema        : {platform.system()} {platform.release()} ({platform.machine()})\n" +
        f"  Python         : {platform.python_version()}\n" +
        sep
    )
    for lp in get_log_paths():
        try:
            os.makedirs(os.path.dirname(lp), exist_ok=True)
            with open(lp, "a", encoding="utf-8") as f:
                f.write(header)
        except Exception:
            pass
