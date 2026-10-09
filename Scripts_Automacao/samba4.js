'use strict';
'require view';
'require fs';
'require ui';
'require dom';
'require form';
'require tools.widgets as widgets';

var I18N = {
	en: {
  "⚙️ Servidor Samba 4:": "⚙️ Samba 4 Server:",
  "Servidor Online": "Server Online",
  "Servidor Parado": "Server Stopped",
  "⚡ Samba 4 Engine • SMB 3.1.1 & 2.1 • Apple macOS/iOS": "⚡ Samba 4 Engine • SMB 3.1.1 & 2.1 • Apple macOS/iOS",
  "⏸️ Pausar (Volta no Boot)": "⏸️ Pause (Restarts on Boot)",
  "🔄 Reiniciar": "🔄 Restart",
  "⏹️ Desativar": "⏹️ Disable",
  "▶️ Ligar": "▶️ Start",
  "Para o serviço agora, mas mantém habilitado para religar no próximo boot do roteador": "Stops the service now, but keeps it enabled to start on next boot",
  "Desativa o servidor permanentemente (inclusive na inicialização do sistema)": "Disables the server permanently (including at system boot)",
  "Pausando Servidor": "Pausing Server",
  "Pausando serviço Samba 4...": "Pausing Samba 4 service...",
  "Iniciando Servidor": "Starting Server",
  "Ativando e iniciando Samba 4...": "Enabling and starting Samba 4...",
  "Reiniciando Servidor": "Restarting Server",
  "Reiniciando serviço Samba 4...": "Restarting Samba 4 service...",
  "Desativando Servidor": "Disabling Server",
  "Parando e desabilitando Samba 4...": "Stopping and disabling Samba 4...",
  "Deseja realmente desativar o servidor Samba 4 permanentemente? Ele não iniciará no boot.": "Do you really want to permanently disable Samba 4? It will not start on boot.",
  "Prevenir Desligamento / Hibernação Automática do HD": "Prevent HDD Sleep / Spin-Down",
  "⚡ Ativado: Mantém o motor do HD girando 24/7. Elimina congelamentos de 5 a 10s ao abrir arquivos na rede.": "⚡ Active: Keeps HDD motor spinning 24/7. Eliminates 5-10s freeze when opening network files.",
  "💤 Desativado: Economia de energia. O HD suspenderá o motor após 10 a 15 minutos ocioso.": "💤 Inactive: Energy saving. HDD will spin down after 10 to 15 minutes of idle time.",
  "⚡ Always-On Ativo (Nunca Desliga)": "⚡ Always-On Active (Never Sleeps)",
  "💤 Repouso Automático (~10-15 min)": "💤 Auto Sleep (~10-15 min)",
  "Ajustando Modo de Energia do Disco": "Adjusting Disk Power Mode",
  "Ativando modo Always-On para prevenir hibernação do HD...": "Activating Always-On mode to prevent HDD sleep...",
  "Desativando otimização; permitindo repouso de energia...": "Deactivating optimization; allowing power saving sleep...",
  "✓ Modo Always-On ativado: O HD externo permanecerá 100% ativo sem desligar o motor (resposta instantânea na rede).": "✓ Always-On mode activated: External HDD will remain 100% active without spinning down (instant network response).",
  "✓ Modo de repouso ativado: O HD entrará em suspensão automática após 10 a 15 minutos de inatividade para economizar energia.": "✓ Sleep mode activated: HDD will automatically enter sleep after 10-15 minutes of inactivity to save power.",
  "Erro ao ajustar modo: %s": "Error adjusting mode: %s",
  "🎛️ Redes & Interfaces Autorizadas (Samba 4)": "🎛️ Authorized Networks & Interfaces (Samba 4)",
  "Controle por Toggle Switch em quais redes os arquivos ficam disponíveis. As regras de firewall são sincronizadas automaticamente.": "Control via Toggle Switch which networks can access files. Firewall rules are synchronized automatically.",
  "⚡ Sincronização Automática com Firewall": "⚡ Automatic Firewall Sync",
  "Rede Principal (LAN)": "Main Network (LAN)",
  "Wi-Fi 2.4/5GHz e portas Ethernet da rede doméstica": "Wi-Fi 2.4/5GHz and home Ethernet ports",
  "Rede de Convidados (Guest)": "Guest Network",
  "Wi-Fi de Visitas. Conexão isolada para visitantes": "Visitor Wi-Fi. Isolated connection for guests",
  "Rede IoT (Dispositivos Inteligentes)": "IoT Network (Smart Devices)",
  "Rede de Smart TVs, consoles e automação residencial": "Smart TVs, consoles and home automation network",
  "Acesso Remoto Externo (WAN)": "Remote External Access (WAN)",
  "Acesso via Internet pública fora de casa (porta 445)": "Public Internet access outside home (port 445)",
  "🛡️ Rede Principal (Sempre Ativa)": "🛡️ Main Network (Always Active)",
  "🔒 Bloqueado no Firewall (Isolado)": "🔒 Blocked in Firewall (Isolated)",
  "🛡️ Blindado (Apenas LAN / Local)": "🛡️ Shielded (LAN / Local Only)",
  "🟢 Liberado no Firewall": "🟢 Allowed in Firewall",
  "⚠️ Porta 445 Liberada": "⚠️ Port 445 Exposed",
  "Atualizando Rede & Firewall": "Updating Network & Firewall",
  "Liberando acesso na rede %s e atualizando firewall...": "Allowing access on network %s and updating firewall...",
  "Bloqueando acesso na rede %s no firewall...": "Blocking access on network %s in firewall...",
  "✓ Interface %s %s com sucesso!": "✓ Interface %s %s successfully!",
  "liberada": "enabled",
  "bloqueada": "blocked",
  "Erro ao atualizar interface: %s": "Error updating interface: %s",
  "Blindando Firewall": "Shielding Firewall",
  "Fechando porta 445 na WAN e blindando o servidor...": "Closing port 445 on WAN and shielding server...",
  "✓ Servidor blindado com sucesso! A porta 445 na WAN foi fechada e o acesso externo bloqueado.": "✓ Server successfully shielded! Port 445 on WAN was closed and external access blocked.",
  "Erro ao bloquear WAN: %s": "Error blocking WAN: %s",
  "⚠️ AVISO: Acesso remoto via WAN liberado na porta 445. Certifique-se de manter senhas fortes em todas as contas.": "⚠️ WARNING: Remote access via WAN opened on port 445. Ensure strong passwords on all accounts.",
  "Erro ao liberar WAN: %s": "Error enabling WAN: %s",
  "🚨 Alerta Crítico de Segurança: Acesso Remoto WAN": "🚨 Critical Security Alert: Remote WAN Access",
  "⚠️ Atenção: Abertura da Porta SMB 445 para a Internet!": "⚠️ Warning: Opening SMB Port 445 to the Internet!",
  "Ao liberar o acesso WAN, o servidor de arquivos Samba ficará exposto a conexões vindas de fora da sua rede local (Internet pública).": "Opening WAN access will expose the Samba file server to connections from outside your local network (public Internet).",
  "Robôs e scanners automatizados na Internet detectam portas 445 abertas 24/7 e realizam tentativas contínuas de invasão por força bruta.": "Automated Internet bots and scanners detect open 445 ports 24/7 and attempt brute-force attacks.",
  "Se qualquer conta cadastrada possuir senha fraca ou fácil de adivinhar, seus arquivos podem ser roubados ou vazados na Internet.": "If any account has a weak or guessable password, your files could be stolen or leaked online.",
  "Muitos provedores de Internet (ISPs) bloqueiam a porta 445 por padrão por motivos de segurança.": "Many Internet service providers (ISPs) block port 445 by default for security reasons.",
  "💡 Boas Práticas Recomendadas:": "💡 Recommended Best Practices:",
  "✓ 1. Mantenha o Acesso Convidado (Sem Senha) estritamente DESATIVADO.": "✓ 1. Keep Guest Access (No Password) strictly DISABLED.",
  "✓ 2. Utilize senhas longas com letras, números e símbolos em todas as contas cadastradas.": "✓ 2. Use long passwords with letters, numbers, and symbols on all registered accounts.",
  "🛡️ 3. Dica de Especialista: Para acesso remoto seguro, prefira utilizar uma VPN (WireGuard/OpenVPN) em vez de expor o Samba diretamente na Internet pública.": "🛡️ 3. Expert Tip: For secure remote access, prefer using a VPN (WireGuard/OpenVPN) rather than exposing Samba directly to the public Internet.",
  "Estou ciente dos riscos de segurança e vazamento na Internet e autorizo abrir a porta 445 na WAN.": "I am aware of security and Internet leak risks and authorize opening port 445 on WAN.",
  "🛡️ Cancelar e Manter Blindado (Recomendado)": "🛡️ Cancel and Keep Shielded (Recommended)",
  "⚠️ Entendo os Riscos, Liberar Porta WAN": "⚠️ I Understand Risks, Open WAN Port",
  "📦 Armazenamento USB Conectado:": "📦 Connected USB Storage:",
  "Tamanho:": "Size:",
  "Ponto de Montagem:": "Mount Point:",
  "Livre:": "Free:",
  "Usado:": "Used:",
  "Montado": "Mounted",
  "Não montado": "Not mounted",
  "⚡ Testar Velocidade": "⚡ Benchmark Speed",
  "🔍 Diagnóstico / FSCK": "🔍 Diagnostics / FSCK",
  "⏏️ Ejetar": "⏏️ Eject",
  "🗑️ Formatar Disco": "🗑️ Format Disk",
  "Desmontando Disco": "Unmounting Disk",
  "Desmontando com segurança %s...": "Safely unmounting %s...",
  "✓ Ponto de montagem %s ejetado com segurança. O disco pode ser desconectado.": "✓ Mount point %s safely ejected. The disk can now be disconnected.",
  "Erro ao ejetar: %s": "Error ejecting: %s",
  "Montando Disco": "Mounting Disk",
  "Montando partição %s...": "Mounting partition %s...",
  "✓ Partição %s montada com sucesso!": "✓ Partition %s mounted successfully!",
  "Erro ao montar: %s": "Error mounting: %s",
  "⏏️ Ejetar / Desmontar": "⏏️ Eject / Unmount",
  "▶️ Montar": "▶️ Mount",
  "Executando Teste de Velocidade": "Running Speed Benchmark",
  "Testando taxas de leitura e escrita real em %s...": "Testing real read/write throughput on %s...",
  "⚡ Teste de Desempenho USB": "⚡ USB Benchmark Results",
  "Taxa de Leitura Sequencial:": "Sequential Read Speed:",
  "Taxa de Gravação Sequencial:": "Sequential Write Speed:",
  "IOPS (Operações por Segundo):": "IOPS (Operations Per Second):",
  "Latência Média:": "Average Latency:",
  "Entendi / Fechar": "Got it / Close",
  "Executando Verificação FSCK": "Running FSCK Verification",
  "Analisando integridade do sistema de arquivos %s...": "Checking filesystem integrity on %s...",
  "🔍 Diagnóstico do Sistema de Arquivos": "🔍 Filesystem Diagnostics",
  "⚠️ ATENÇÃO: Formatação de Disco USB": "⚠️ WARNING: USB Disk Formatting",
  "Você está prestes a formatar o dispositivo ": "You are about to format the device ",
  ". TODOS OS ARQUIVOS E DADOS SERÃO PERMANENTEMENTE APAGADOS!": ". ALL FILES AND DATA WILL BE PERMANENTLY ERASED!",
  "Rótulo do Volume (Nome do Disco):": "Volume Label (Disk Name):",
  "Para autorizar, digite \"SIM\" abaixo:": "To authorize, type \"YES\" below:",
  "Cancelar": "Cancel",
  "🗑️ Sim, Formatar Disco Agora": "🗑️ Yes, Format Disk Now",
  "Formatando Disco": "Formatting Disk",
  "Formatando %s com sistema de arquivos ExFAT...": "Formatting %s with ExFAT filesystem...",
  "✓ Disco %s formatado com sucesso como ExFAT!": "✓ Disk %s successfully formatted as ExFAT!",
  "Erro ao formatar disco: %s": "Error formatting disk: %s",
  "👥 Contas de Acesso & Senhas (Samba 4)": "👥 Access Accounts & Passwords (Samba 4)",
  "Gerencie contas e controle visualmente permissões de escrita ou somente leitura via toggle switch.": "Manage accounts and visually control write or read-only permissions via toggle switch.",
  "➕ Nova Conta de Rede": "➕ New Network Account",
  "💡 Segurança & Isolamento da Conta \"root\":": "💡 Security & Isolation of the \"root\" Account:",
  "O usuário root exibido abaixo pertence exclusivamente ao serviço de arquivos Samba 4 (SMB). Ele não tem qualquer vínculo com a conta root nativa do sistema operacional Linux. Alterar ou manter a senha aqui NÃO altera nem afeta o SSH, Telnet ou o acesso administrativo do painel LuCI.": "The root user displayed below belongs exclusively to the Samba 4 file sharing service (SMB). It has no link whatsoever to the native Linux root account. Changing or keeping this password does NOT alter or affect SSH, Telnet, or LuCI panel administrator login.",
  "👑 Administrador Master": "👑 Master Administrator",
  "⭐ Administrador": "⭐ Administrator",
  "👤 Usuário Autorizado": "👤 Authorized User",
  "🔑 Senha Padrão: ": "🔑 Default Password: ",
  "Esta conta está usando a senha padrão de fábrica root0100.": "This account is using the factory default password root0100.",
  "🔒 Senha Personalizada": "🔒 Custom Password",
  "A senha desta conta foi alterada e personalizada.": "This account password was customized by user.",
  "✏️ Leitura e Gravação": "✏️ Read and Write",
  "🔒 Somente Leitura": "🔒 Read-Only",
  "✓ Permissão da conta \"%s\" atualizada: Leitura e Gravação (Acesso Total).": "✓ Permission for account \"%s\" updated: Read and Write (Full Access).",
  "✓ Permissão da conta \"%s\" atualizada: Somente Leitura (Gravação Bloqueada).": "✓ Permission for account \"%s\" updated: Read-Only (Write Blocked).",
  "Erro ao alterar permissão: %s": "Error changing permission: %s",
  "Alterar senha da conta %s": "Change password for account %s",
  "🔑 Alterar Senha": "🔑 Change Password",
  "Remover conta %s": "Remove account %s",
  "Deseja realmente remover o usuário \"%s\"?": "Do you really want to remove user \"%s\"?",
  "Removendo Usuário": "Removing User",
  "Removendo conta %s...": "Removing account %s...",
  "Usuário %s removido com sucesso.": "User %s successfully removed.",
  "Erro ao remover usuário: %s": "Error removing user: %s",
  "🗑️ Excluir": "🗑️ Delete",
  "🔒 Protegido": "🔒 Protected",
  "Conta exclusiva para compartilhamento de rede (SMB). Não possui vínculo com o root nativo do Linux e NÃO afeta o acesso SSH, Telnet ou login do painel.": "Exclusive account for SMB network sharing. Has no link to native Linux root and does NOT affect SSH, Telnet, or panel login.",
  "🔑 Alterar Senha de Rede: %s": "🔑 Change Network Password: %s",
  "Defina uma nova senha para a conta ": "Set a new password for account ",
  ". Esta senha é usada para login na rede via Windows, Mac, iPhone, iPad e Android.": ". This password is used to log in via Windows, Mac, iPhone, iPad, and Android.",
  "⚠️ Aviso de Segurança: ": "⚠️ Security Notice: ",
  "Esta alteração afeta exclusivamente o acesso às pastas de rede (SMB/Samba 4). As senhas do terminal SSH, Telnet e de administração do painel LuCI não são afetadas.": "This change exclusively affects SMB/Samba 4 network share access. Terminal SSH, Telnet, and LuCI admin passwords are not affected.",
  "Nova Senha de Rede:": "New Network Password:",
  "Nova senha para %s": "New password for %s",
  "💾 Salvar Nova Senha": "💾 Save New Password",
  "Atualizando Senha": "Updating Password",
  "Gravando nova senha do usuário \"%s\"...": "Saving new password for user \"%s\"...",
  "✓ Senha do usuário \"%s\" atualizada com sucesso!": "✓ Password for user \"%s\" updated successfully!",
  "Erro ao atualizar senha: %s": "Error updating password: %s",
  "➕ Cadastrar Nova Conta de Rede": "➕ Register New Network Account",
  "Nome de Usuário:": "Username:",
  "Apenas letras, números, underline (_) ou hífen (-).": "Only letters, numbers, underscore (_), or hyphen (-).",
  "Senha de Rede:": "Network Password:",
  "Senha da nova conta": "New account password",
  "Permissão Inicial:": "Initial Permission:",
  "✏️ Leitura e Gravação (Acesso Total)": "✏️ Read and Write (Full Access)",
  "🔒 Somente Leitura (Sem Gravação)": "🔒 Read-Only (No Write Access)",
  "➕ Criar Usuário": "➕ Create User",
  "Criando Conta": "Creating Account",
  "Cadastrando usuário \"%s\" no Samba 4...": "Registering user \"%s\" in Samba 4...",
  "✓ Usuário \"%s\" criado com sucesso!": "✓ User \"%s\" created successfully!",
  "Erro ao cadastrar usuário: %s": "Error registering user: %s",
  "Mostrar / Ocultar Senha": "Show / Hide Password",
  "Mostrar ou ocultar senha": "Show or hide password",
  "Digite a senha": "Enter password",
  "🌐 Como Acessar os Arquivos na Rede:": "🌐 How to Access Files on the Network:",
  "❓ Dúvidas / Ajuda no Windows": "❓ Questions / Windows Help",
  "🪟 Windows (Explorador de Arquivos):": "🪟 Windows (File Explorer):",
  "Pressione Win+R e cole o endereço no Windows.": "Press Win+R and paste the address in Windows.",
  "🍎 iPhone / iPad / Mac / Android:": "🍎 iPhone / iPad / Mac / Android:",
  "No iOS: App Arquivos > \"...\" > Conectar ao Servidor. No Mac: Finder > Cmd+K.": "On iOS: Files app > \"...\" > Connect to Server. On Mac: Finder > Cmd+K.",
  "✓ Acesso interno direto via IP %s.": "✓ Direct internal access via IP %s.",
  "Sempre Ativo": "Always Active",
  "Liberado": "Enabled",
  "Acesso Remoto Blindado & Bloqueado": "Remote Access Shielded & Blocked",
  "O firewall impede conexões da Internet. Para acessar fora de casa, ligue o switch na seção de Redes acima.": "The firewall blocks Internet connections. To access outside home, turn on the switch in the Networks section above.",
  "🔒 Segurança máxima: Tráfego da porta 445 100% rejeitado no firewall.": "🔒 Maximum security: Port 445 traffic is 100% rejected in the firewall.",
  "Acesso Remoto Externo (WAN / Internet)": "Remote External Access (WAN / Internet)",
  "Blindado / Desativado": "Shielded / Disabled",
  "🔒 Segurança Ativa: Acesso anônimo restrito a leitura • Gravação exclusiva para contas autorizadas • Descoberta automática via Bonjour e WSDD.": "🔒 Active Security: Anonymous access restricted to read-only • Writing reserved for authorized accounts • Auto-discovery via Bonjour and WSDD.",
  "Status: 💤 Nenhum cliente conectado (em repouso)": "Status: 💤 No client connected (idle)",
  "Status: 🟢 %s cliente(s) conectado(s):": "Status: 🟢 %s connected client(s):",
  "🪟 Guia de Conexão e Solução de Problemas no Windows": "🪟 Windows Connection & Troubleshooting Guide",
  "ℹ️ O Windows 10 e Windows 11 já vêm 100% prontos de fábrica!": "ℹ️ Windows 10 and Windows 11 come 100% ready out of the box!",
  "Os protocolos SMBv2 e SMBv3 são nativos e ativados por padrão em qualquer computador moderno. Você NÃO precisa digitar nenhum comando nem habilitar nada para acessar.": "SMBv2 and SMBv3 protocols are native and enabled by default on any modern computer. You do NOT need to type any commands or enable anything to connect.",
  "🚀 Passo a Passo Simples para Conectar:": "🚀 Simple Step-by-Step to Connect:",
  "No seu teclado Windows, pressione ": "On your Windows keyboard, press ",
  " (janela Executar).": " (Run prompt).",
  "Cole o endereço: ": "Paste the address: ",
  " e dê Enter.": " and press Enter.",
  "Quando pedir usuário e senha, informe uma conta cadastrada no painel (ex: ": "When prompted for username and password, enter an account registered in the panel (e.g., ",
  " ou ": " or ",
  "Marque a opção \"Lembrar minhas credenciais\" para não precisar digitar novamente.": "Check the \"Remember my credentials\" option so you don't have to type it again.",
  "⚙️ Diagnóstico Avançado (Apenas caso tenha alterado o SMB no Windows anteriormente):": "⚙️ Advanced Diagnostics (Only if you previously altered SMB settings in Windows):",
  "Se você desativou recursos do Windows no passado e precisa checar/ativar:": "If you disabled Windows features in the past and need to check/enable them:",
  "Compartilhamento de Arquivos USB (Samba 4)": "USB File Sharing (Samba 4)",
  "Serviço de compartilhamento Samba 4 com suporte nativo a Windows, macOS e iOS (Apple AAPL).": "High-performance Samba 4 SMB file sharing service with native Apple macOS and iOS support.",
  "Configurações Gerais do Servidor": "General Server Settings",
  "Nome do Servidor na Rede": "Server Network Name",
  "Nome de identificação do roteador exibido na rede local (Windows, macOS, etc.).": "Router identification name displayed on the local network (Windows, macOS, etc.).",
  "Grupo de Trabalho (Workgroup)": "Workgroup",
  "Nome do grupo de trabalho de rede SMB (padrão: WORKGROUP).": "SMB network workgroup name (default: WORKGROUP).",
  "Permitir SMBv1 Legado": "Allow Legacy SMBv1",
  "Ative apenas se conectar consoles antigos ou TVs legadas sem suporte a SMBv2/v3 (não recomendado por segurança).": "Enable only if connecting legacy game consoles or older TVs without SMBv2/v3 support (not recommended for security).",
  "Pastas Compartilhadas": "Shared Folders",
  "Gerencie o ponto de montagem e as permissões de acesso das pastas na rede local.": "Manage mount points and access permissions for network shares.",
  "Nome do Compartilhamento": "Share Name",
  "Caminho no Disco": "Disk Path",
  "Acesso Convidado (Sem Senha)": "Guest Access (No Password)",
  "Bloquear Gravação para Visitantes (Somente Leitura)": "Block Guest Writing (Read-Only)",
  "Usuários com Permissão de Gravação": "Users with Write Permission",
  "/mnt (Todos os Discos USB Conectados)": "/mnt (All Connected USB Disks)",
  "🟢 Montado": "🟢 Mounted",
  "🔴 Desmontado": "🔴 Unmounted",
  "Desmontar partição com segurança": "Safely unmount partition",
  "Montar partição no sistema": "Mount partition in system",
  "Verificar integridade do sistema de arquivos e diagnosticar o disco": "Check filesystem integrity and diagnose disk",
  "Testar velocidade de leitura e gravação no USB 3.0": "Benchmark USB 3.0 read and write speeds",
  "Formatar o disco com sistema de arquivos EXT4": "Format disk with EXT4 filesystem",
  "Alterar Senha": "Change Password",
  "Excluir": "Delete",
  "Nova Conta de Rede": "New Network Account",
  "Senha Padrão: ": "Default Password: ",
  "Senha Personalizada": "Custom Password",
  "Segurança & Isolamento da Conta \"root\":": "Security & Isolation of the \"root\" Account:",
  "Porta 445 Liberada": "Port 445 Exposed",
  "Atenção: Abertura da Porta SMB 445 para a Internet!": "Warning: Opening SMB Port 445 to the Internet!",
  "Aviso de Segurança: ": "Security Notice: ",
  "Dúvidas / Ajuda no Windows": "Questions / Windows Help",
  "IP não atribuído": "IP not assigned",
  "Tamanho: ": "Size: ",
  "Ponto de Montagem: ": "Mount Point: ",
  "Livre: ": "Free: ",
  "Usado: ": "Used: ",
  "Nenhum": "None",
  "Status: ": "Status: ",
  "%s cliente(s) ativo(s): ": "%s active client(s): ",
  "💤 Nenhum cliente conectado (em repouso)": "💤 No client connected (idle)",
  "🪟 Windows (Explorador via Internet):": "🪟 Windows (Internet Explorer/Run):",
  "Pressione Win+R e acesse de fora de casa pelo IP público.": "Press Win+R and access from outside home via public IP.",
  "Conecte remotamente de qualquer lugar pelo celular ou notebook.": "Connect remotely from anywhere using your phone or laptop.",
  "⚠️ Requer que o provedor não filtre a porta 445 e uso obrigatório de senha forte.": "⚠️ Requires ISP not blocking port 445 and mandatory use of strong passwords.",
  "⚠️ Aberto na WAN (Porta 445)": "⚠️ Exposed on WAN (Port 445)",
  "🔄 Montar": "🔄 Mount",
  "Detectando sistema de arquivos e montando partição...": "Detecting filesystem and mounting partition...",
  "Verificando Integridade do Disco": "Checking Disk Integrity",
  "Executando diagnóstico de integridade no disco...": "Running integrity diagnostics on disk...",
  "Diagnóstico concluído.": "Diagnostics completed.",
  "Diagnóstico do Sistema de Arquivos": "Filesystem Diagnostics",
  "Resultado da Verificação (%s):": "Verification Result (%s):",
  "Fechar": "Close",
  "Erro no diagnóstico: %s": "Error in diagnostics: %s",
  "Testando Velocidade USB 3.0": "Testing USB 3.0 Speed",
  "Gravando bloco de teste no disco para medir taxa de transferência...": "Writing test block to disk to benchmark throughput...",
  "Resultado do Teste de Desempenho": "Performance Benchmark Result",
  "Concluído com sucesso": "Successfully completed",
  "Taxa de transferência real registrada no disco %s (%s).": "Real throughput recorded on disk %s (%s).",
  "Erro ao testar velocidade: %s": "Error testing speed: %s",
  "⚠️ Zona de Perigo: Formatar Disco": "⚠️ Danger Zone: Format Disk",
  "ATENÇÃO: PERDA TOTAL DE DADOS!": "WARNING: TOTAL DATA LOSS!",
  "Esta ação apagará permanentemente todos os arquivos e pastas da partição %s.": "This action will permanently delete all files and folders on partition %s.",
  "Nome do Disco (Rótulo / Label):": "Disk Name (Label):",
  "Sistema de Arquivos:": "Filesystem:",
  "EXT4 - Linux Nativo (Recomendado)": "EXT4 - Native Linux (Recommended)",
  "Digite SIM para confirmar": "Type YES to confirm",
  "🗑️ Confirmar Formatação": "🗑️ Confirm Formatting",
  "Formatando %s em EXT4 de alto desempenho... Aguarde.": "Formatting %s to high-performance EXT4... Please wait.",
  "✓ O disco %s foi formatado com sucesso em EXT4 e remontado!": "✓ Disk %s was successfully formatted to EXT4 and remounted!",
  "Erro na formatação: %s": "Error formatting: %s",
  "Sincronizando cache de escrita e desmontando partição...": "Flushing write cache and unmounting partition...",
  "O disco %s foi ejetado com segurança! Você já pode desconectar o cabo USB.": "Disk %s safely ejected! You may now unplug the USB cable.",
  "Ejetando Disco com Segurança": "Safely Ejecting Disk",
  "Erro ao desmontar: %s": "Error unmounting: %s",
  "🟢 Servidor Online": "🟢 Server Online",
  "🟡 Servidor Pausado": "🟡 Server Paused",
  "🔴 Desativado": "🔴 Disabled",
  "🔵 Temporário": "🔵 Temporary",
  "Informe a senha para o novo usuário.": "Please enter a password for the new user.",
  "Informe um nome de usuário válido (apenas letras, números, hífen ou underline).": "Please enter a valid username (letters, numbers, hyphen or underscore only).",
  "Por favor, informe uma senha válida.": "Please enter a valid password.",
  "Mostrar Senha": "Show Password",
  "Ocultar Senha": "Hide Password",
  "Aplicando Regras de Firewall": "Applying Firewall Rules",
  "Liberando porta 445 na WAN e recarregando firewall...": "Opening port 445 on WAN and reloading firewall...",
  "Visível na Rede": "Visible on Network"
},
	es: {
  "⚙️ Servidor Samba 4:": "⚙️ Servidor Samba 4:",
  "Servidor Online": "Servidor en Línea",
  "Servidor Parado": "Servidor Detenido",
  "⚡ Samba 4 Engine • SMB 3.1.1 & 2.1 • Apple macOS/iOS": "⚡ Samba 4 Engine • SMB 3.1.1 & 2.1 • Apple macOS/iOS",
  "⏸️ Pausar (Volta no Boot)": "⏸️ Pausar (Vuelve al Reiniciar)",
  "🔄 Reiniciar": "🔄 Reiniciar",
  "⏹️ Desativar": "⏹️ Desactivar",
  "▶️ Ligar": "▶️ Iniciar",
  "Para o serviço agora, mas mantém habilitado para religar no próximo boot do roteador": "Detiene el servicio ahora, pero lo mantiene habilitado para el próximo inicio del router",
  "Desativa o servidor permanentemente (inclusive na inicialização do sistema)": "Desactiva el servidor permanentemente (incluso en el inicio del sistema)",
  "Pausando Servidor": "Pausando Servidor",
  "Pausando serviço Samba 4...": "Deteniendo el servicio Samba 4 temporalmente...",
  "Iniciando Servidor": "Iniciando Servidor",
  "Ativando e iniciando Samba 4...": "Activando e iniciando Samba 4...",
  "Reiniciando Servidor": "Reiniciando Servidor",
  "Reiniciando serviço Samba 4...": "Reiniciando el servicio Samba 4...",
  "Desativando Servidor": "Desactivando Servidor",
  "Parando e desabilitando Samba 4...": "Deteniendo y deshabilitando Samba 4...",
  "Deseja realmente desativar o servidor Samba 4 permanentemente? Ele não iniciará no boot.": "¿Realmente desea desactivar el servidor Samba 4 permanentemente? No se iniciará al encender.",
  "Prevenir Desligamento / Hibernação Automática do HD": "Prevenir Suspensión / Hibernación del Disco",
  "⚡ Ativado: Mantém o motor do HD girando 24/7. Elimina congelamentos de 5 a 10s ao abrir arquivos na rede.": "⚡ Activado: Mantiene el motor del disco girando 24/7. Elimina congelamientos de 5 a 10s al abrir archivos en red.",
  "💤 Desativado: Economia de energia. O HD suspenderá o motor após 10 a 15 minutos ocioso.": "💤 Inactivo: Ahorro de energía. El disco suspenderá el motor tras 10 a 15 minutos inactivo.",
  "⚡ Always-On Ativo (Nunca Desliga)": "⚡ Always-On Activo (Nunca se apaga)",
  "💤 Repouso Automático (~10-15 min)": "💤 Suspensión Automática (~10-15 min)",
  "Ajustando Modo de Energia do Disco": "Ajustando Modo de Energía del Disco",
  "Ativando modo Always-On para prevenir hibernação do HD...": "Activando modo Always-On para prevenir suspensión del disco...",
  "Desativando otimização; permitindo repouso de energia...": "Desactivando optimización; permitiendo reposo de energía...",
  "✓ Modo Always-On ativado: O HD externo permanecerá 100% ativo sem desligar o motor (resposta instantânea na rede).": "✓ Modo Always-On activado: El disco externo permanecerá 100% activo sin apagar el motor (respuesta instantánea en red).",
  "✓ Modo de repouso ativado: O HD entrará em suspensão automática após 10 a 15 minutos de inatividade para economizar energia.": "✓ Modo de suspensión activado: El disco entrará en reposo tras 10 a 15 minutos de inactividad para ahorrar energía.",
  "Erro ao ajustar modo: %s": "Error al ajustar modo: %s",
  "🎛️ Redes & Interfaces Autorizadas (Samba 4)": "🎛️ Redes e Interfaces Autorizadas (Samba 4)",
  "Controle por Toggle Switch em quais redes os arquivos ficam disponíveis. As regras de firewall são sincronizadas automaticamente.": "Controle mediante Toggle Switch en qué redes estarán disponibles los archivos. Las reglas de firewall se sincronizan automáticamente.",
  "⚡ Sincronização Automática com Firewall": "⚡ Sincronización Automática con Firewall",
  "Rede Principal (LAN)": "Red Principal (LAN)",
  "Wi-Fi 2.4/5GHz e portas Ethernet da rede doméstica": "Wi-Fi 2.4/5GHz y puertos Ethernet de la red doméstica",
  "Rede de Convidados (Guest)": "Red de Invitados (Guest)",
  "Wi-Fi de Visitas. Conexão isolada para visitantes": "Wi-Fi de Visitas. Conexión aislada para invitados",
  "Rede IoT (Dispositivos Inteligentes)": "Red IoT (Dispositivos Inteligentes)",
  "Rede de Smart TVs, consoles e automação residencial": "Red de Smart TVs, consolas y domótica",
  "Acesso Remoto Externo (WAN)": "Acceso Remoto Externo (WAN)",
  "Acesso via Internet pública fora de casa (porta 445)": "Acceso mediante Internet pública fuera de casa (puerto 445)",
  "🛡️ Rede Principal (Sempre Ativa)": "🛡️ Red Principal (Siempre Activa)",
  "🔒 Bloqueado no Firewall (Isolado)": "🔒 Bloqueado en Firewall (Aislado)",
  "🛡️ Blindado (Apenas LAN / Local)": "🛡️ Blindado (Solo LAN / Local)",
  "🟢 Liberado no Firewall": "🟢 Permitido en Firewall",
  "⚠️ Porta 445 Liberada": "⚠️ Puerto 445 Abierto",
  "Atualizando Rede & Firewall": "Actualizando Red y Firewall",
  "Liberando acesso na rede %s e atualizando firewall...": "Permitiendo acceso en la red %s y actualizando firewall...",
  "Bloqueando acesso na rede %s no firewall...": "Bloqueando acceso en la red %s en firewall...",
  "✓ Interface %s %s com sucesso!": "✓ ¡Interfaz %s %s con éxito!",
  "liberada": "habilitada",
  "bloqueada": "bloqueada",
  "Erro ao atualizar interface: %s": "Error al actualizar interfaz: %s",
  "Blindando Firewall": "Blindando Firewall",
  "Fechando porta 445 na WAN e blindando o servidor...": "Cerrando puerto 445 en WAN y blindando el servidor...",
  "✓ Servidor blindado com sucesso! A porta 445 na WAN foi fechada e o acesso externo bloqueado.": "✓ ¡Servidor blindado con éxito! Se cerró el puerto 445 en WAN y se bloqueó el acceso externo.",
  "Erro ao bloquear WAN: %s": "Error al bloquear WAN: %s",
  "⚠️ AVISO: Acesso remoto via WAN liberado na porta 445. Certifique-se de manter senhas fortes em todas as contas.": "⚠️ AVISO: Acceso remoto por WAN habilitado en el puerto 445. Asegúrese de usar contraseñas seguras en todas las cuentas.",
  "Erro ao liberar WAN: %s": "Error al habilitar WAN: %s",
  "🚨 Alerta Crítico de Segurança: Acesso Remoto WAN": "🚨 Alerta Crítica de Seguridad: Acceso Remoto WAN",
  "⚠️ Atenção: Abertura da Porta SMB 445 para a Internet!": "⚠️ Atención: ¡Apertura del Puerto SMB 445 hacia Internet pública!",
  "Ao liberar o acesso WAN, o servidor de arquivos Samba ficará exposto a conexões vindas de fora da sua rede local (Internet pública).": "Al habilitar el acceso WAN, el servidor de archivos Samba quedará expuesto a conexiones desde fuera de su red local (Internet pública).",
  "Robôs e scanners automatizados na Internet detectam portas 445 abertas 24/7 e realizam tentativas contínuas de invasão por força bruta.": "Robots y escáneres automáticos en Internet detectan puertos 445 abiertos 24/7 e intentan ataques por fuerza bruta.",
  "Se qualquer conta cadastrada possuir senha fraca ou fácil de adivinhar, seus arquivos podem ser roubados ou vazados na Internet.": "Si cualquier cuenta posee una contraseña débil o fácil de adivinar, sus archivos podrían ser robados o filtrados en Internet.",
  "Muitos provedores de Internet (ISPs) bloqueiam a porta 445 por padrão por motivos de segurança.": "Muchos proveedores de Internet (ISP) bloquean el puerto 445 por defecto por motivos de seguridad.",
  "💡 Boas Práticas Recomendadas:": "💡 Prácticas Recomendadas:",
  "✓ 1. Mantenha o Acesso Convidado (Sem Senha) estritamente DESATIVADO.": "✓ 1. Mantenga el Acceso de Invitados (Sin Contraseña) estrictamente DESACTIVADO.",
  "✓ 2. Utilize senhas longas com letras, números e símbolos em todas as contas cadastradas.": "✓ 2. Utilice contraseñas largas con letras, números y símbolos en todas las cuentas.",
  "🛡️ 3. Dica de Especialista: Para acesso remoto seguro, prefira utilizar uma VPN (WireGuard/OpenVPN) em vez de expor o Samba diretamente na Internet pública.": "🛡️ 3. Consejo de Experto: Para acceso remoto seguro, prefiera utilizar una VPN (WireGuard/OpenVPN) en lugar de exponer Samba directamente a Internet pública.",
  "Estou ciente dos riscos de segurança e vazamento na Internet e autorizo abrir a porta 445 na WAN.": "Soy consciente de los riesgos de seguridad y filtración en Internet y autorizo abrir el puerto 445 en la WAN.",
  "🛡️ Cancelar e Manter Blindado (Recomendado)": "🛡️ Cancelar y Mantener Blindado (Recomendado)",
  "⚠️ Entendo os Riscos, Liberar Porta WAN": "⚠️ Entiendo los Riesgos, Habilitar Puerto WAN",
  "📦 Armazenamento USB Conectado:": "📦 Almacenamiento USB Conectado:",
  "Tamanho:": "Tamaño:",
  "Ponto de Montagem:": "Punto de Montaje:",
  "Livre:": "Libre:",
  "Usado:": "Usado:",
  "Montado": "Montado",
  "Não montado": "No montado",
  "⚡ Testar Velocidade": "⚡ Probar Velocidad",
  "🔍 Diagnóstico / FSCK": "🔍 Diagnóstico / FSCK",
  "⏏️ Ejetar": "⏏️ Expulsar",
  "🗑️ Formatar Disco": "🗑️ Formatear Disco",
  "Desmontando Disco": "Desmontando Disco",
  "Desmontando com segurança %s...": "Desmontando con seguridad %s...",
  "✓ Ponto de montagem %s ejetado com segurança. O disco pode ser desconectado.": "✓ Punto de montaje %s expulsado con seguridad. El disco puede desconectarse.",
  "Erro ao ejetar: %s": "Error al expulsar: %s",
  "Montando Disco": "Montando Disco",
  "Montando partição %s...": "Montando partición %s...",
  "✓ Partição %s montada com sucesso!": "✓ ¡Partición %s montada con éxito!",
  "Erro ao montar: %s": "Error al montar: %s",
  "⏏️ Ejetar / Desmontar": "⏏️ Expulsar / Desmontar",
  "▶️ Montar": "▶️ Montar",
  "Executando Teste de Velocidade": "Ejecutando Prueba de Velocidad",
  "Testando taxas de leitura e escrita real em %s...": "Probando velocidades de lectura y escritura real en %s...",
  "⚡ Teste de Desempenho USB": "⚡ Resultados de Rendimiento USB",
  "Taxa de Leitura Sequencial:": "Velocidad de Lectura Secuencial:",
  "Taxa de Gravação Sequencial:": "Velocidad de Escritura Secuencial:",
  "IOPS (Operações por Segundo):": "IOPS (Operaciones por Segundo):",
  "Latência Média:": "Latencia Media:",
  "Entendi / Fechar": "Entendido / Cerrar",
  "Executando Verificação FSCK": "Ejecutando Verificación FSCK",
  "Analisando integridade do sistema de arquivos %s...": "Analizando integridad del sistema de archivos %s...",
  "🔍 Diagnóstico do Sistema de Arquivos": "🔍 Diagnóstico del Sistema de Archivos",
  "⚠️ ATENÇÃO: Formatação de Disco USB": "⚠️ ATENCIÓN: Formateo de Disco USB",
  "Você está prestes a formatar o dispositivo ": "Está a punto de formatear el dispositivo ",
  ". TODOS OS ARQUIVOS E DADOS SERÃO PERMANENTEMENTE APAGADOS!": ". ¡TODOS LOS ARCHIVOS Y DATOS SE BORRARÁN PERMANENTEMENTE!",
  "Rótulo do Volume (Nome do Disco):": "Etiqueta del Volumen (Nombre del Disco):",
  "Para autorizar, digite \"SIM\" abaixo:": "Para autorizar, escriba \"SIM\" abajo:",
  "Cancelar": "Cancelar",
  "🗑️ Sim, Formatar Disco Agora": "🗑️ Sí, Formatear Disco Ahora",
  "Formatando Disco": "Formateando Disco",
  "Formatando %s com sistema de arquivos ExFAT...": "Formateando %s con sistema de archivos ExFAT...",
  "✓ Disco %s formatado com sucesso como ExFAT!": "✓ ¡Disco %s formateado con éxito como ExFAT!",
  "Erro ao formatar disco: %s": "Error al formatear disco: %s",
  "👥 Contas de Acesso & Senhas (Samba 4)": "👥 Cuentas de Acceso y Contraseñas (Samba 4)",
  "Gerencie contas e controle visualmente permissões de escrita ou somente leitura via toggle switch.": "Administre cuentas y controle visualmente permisos de escritura o solo lectura mediante toggle switch.",
  "➕ Nova Conta de Rede": "➕ Nueva Cuenta de Red",
  "💡 Segurança & Isolamento da Conta \"root\":": "💡 Seguridad y Aislamiento de la Cuenta \"root\":",
  "O usuário root exibido abaixo pertence exclusivamente ao serviço de arquivos Samba 4 (SMB). Ele não tem qualquer vínculo com a conta root nativa do sistema operacional Linux. Alterar ou manter a senha aqui NÃO altera nem afeta o SSH, Telnet ou o acesso administrativo do painel LuCI.": "El usuario root que se muestra a continuación pertenece exclusivamente al servicio de archivos Samba 4 (SMB). No tiene ningún vínculo con la cuenta root nativa del sistema operativo Linux. Cambiar o mantener la contraseña aquí NO altera ni afecta el acceso SSH, Telnet ni el inicio de sesión de administración del panel LuCI.",
  "👑 Administrador Master": "👑 Administrador Maestro",
  "⭐ Administrador": "⭐ Administrador",
  "👤 Usuário Autorizado": "👤 Usuario Autorizado",
  "🔑 Senha Padrão: ": "🔑 Contraseña Predeterminada: ",
  "Esta conta está usando a senha padrão de fábrica root0100.": "Esta cuenta utiliza la contraseña predeterminada de fábrica root0100.",
  "🔒 Senha Personalizada": "🔒 Contraseña Personalizada",
  "A senha desta conta foi alterada e personalizada.": "La contraseña de esta cuenta fue personalizada por el usuario.",
  "✏️ Leitura e Gravação": "✏️ Lectura y Escritura",
  "🔒 Somente Leitura": "🔒 Solo Lectura",
  "✓ Permissão da conta \"%s\" atualizada: Leitura e Gravação (Acesso Total).": "✓ Permiso de la cuenta \"%s\" actualizado: Lectura y Escritura (Acceso Total).",
  "✓ Permissão da conta \"%s\" atualizada: Somente Leitura (Gravação Bloqueada).": "✓ Permiso de la cuenta \"%s\" actualizado: Solo Lectura (Escritura Bloqueada).",
  "Erro ao alterar permissão: %s": "Error al cambiar permiso: %s",
  "Alterar senha da conta %s": "Cambiar contraseña de la cuenta %s",
  "🔑 Alterar Senha": "🔑 Cambiar Contraseña",
  "Remover conta %s": "Eliminar cuenta %s",
  "Deseja realmente remover o usuário \"%s\"?": "¿Realmente desea eliminar el usuario \"%s\"?",
  "Removendo Usuário": "Eliminando Usuario",
  "Removendo conta %s...": "Eliminando cuenta %s...",
  "Usuário %s removido com sucesso.": "Usuario %s eliminado con éxito.",
  "Erro ao remover usuário: %s": "Error al eliminar usuario: %s",
  "🗑️ Excluir": "🗑️ Eliminar",
  "🔒 Protegido": "🔒 Protegido",
  "Conta exclusiva para compartilhamento de rede (SMB). Não possui vínculo com o root nativo do Linux e NÃO afeta o acesso SSH, Telnet ou login do painel.": "Cuenta exclusiva para compartir en red (SMB). No tiene vínculo con el root nativo de Linux y NO afecta el acceso SSH, Telnet ni el inicio de sesión del panel.",
  "🔑 Alterar Senha de Rede: %s": "🔑 Cambiar Contraseña de Red: %s",
  "Defina uma nova senha para a conta ": "Defina una nueva contraseña para la cuenta ",
  ". Esta senha é usada para login na rede via Windows, Mac, iPhone, iPad e Android.": ". Esta contraseña se utiliza para iniciar sesión en red mediante Windows, Mac, iPhone, iPad y Android.",
  "⚠️ Aviso de Segurança: ": "⚠️ Aviso de Seguridad: ",
  "Esta alteração afeta exclusivamente o acesso às pastas de rede (SMB/Samba 4). As senhas do terminal SSH, Telnet e de administração do painel LuCI não são afetadas.": "Este cambio afecta exclusivamente el acceso a las carpetas de red (SMB/Samba 4). Las contraseñas de SSH, Telnet y administración de LuCI no se ven afectadas.",
  "Nova Senha de Rede:": "Nueva Contraseña de Red:",
  "Nova senha para %s": "Nueva contraseña para %s",
  "💾 Salvar Nova Senha": "💾 Guardar Nueva Contraseña",
  "Atualizando Senha": "Actualizando Contraseña",
  "Gravando nova senha do usuário \"%s\"...": "Guardando nueva contraseña del usuario \"%s\"...",
  "✓ Senha do usuário \"%s\" atualizada com sucesso!": "✓ ¡Contraseña del usuario \"%s\" actualizada con éxito!",
  "Erro ao atualizar senha: %s": "Error al actualizar contraseña: %s",
  "➕ Cadastrar Nova Conta de Rede": "➕ Registrar Nueva Cuenta de Red",
  "Nome de Usuário:": "Nombre de Usuario:",
  "Apenas letras, números, underline (_) ou hífen (-).": "Solo letras, números, guión bajo (_) o guión (-).",
  "Senha de Rede:": "Contraseña de Red:",
  "Senha da nova conta": "Contraseña de la nueva cuenta",
  "Permissão Inicial:": "Permiso Inicial:",
  "✏️ Leitura e Gravação (Acesso Total)": "✏️ Lectura y Escritura (Acceso Total)",
  "🔒 Somente Leitura (Sem Gravação)": "🔒 Solo Lectura (Sin Escritura)",
  "➕ Criar Usuário": "➕ Crear Usuario",
  "Criando Conta": "Creando Cuenta",
  "Cadastrando usuário \"%s\" no Samba 4...": "Registrando usuario \"%s\" en Samba 4...",
  "✓ Usuário \"%s\" criado com sucesso!": "✓ ¡Usuario \"%s\" creado con éxito!",
  "Erro ao cadastrar usuário: %s": "Error al registrar usuario: %s",
  "Mostrar / Ocultar Senha": "Mostrar / Ocultar Contraseña",
  "Mostrar ou ocultar senha": "Mostrar u ocultar contraseña",
  "Digite a senha": "Escriba la contraseña",
  "🌐 Como Acessar os Arquivos na Rede:": "🌐 ¿Cómo Acceder a los Archivos en la Red?:",
  "❓ Dúvidas / Ajuda no Windows": "❓ Dudas / Ayuda en Windows",
  "🪟 Windows (Explorador de Arquivos):": "🪟 Windows (Explorador de Archivos):",
  "Pressione Win+R e cole o endereço no Windows.": "Presione Win+R y pegue la dirección en Windows.",
  "🍎 iPhone / iPad / Mac / Android:": "🍎 iPhone / iPad / Mac / Android:",
  "No iOS: App Arquivos > \"...\" > Conectar ao Servidor. No Mac: Finder > Cmd+K.": "En iOS: App Archivos > \"...\" > Conectar al Servidor. En Mac: Finder > Cmd+K.",
  "✓ Acesso interno direto via IP %s.": "✓ Acceso interno directo mediante IP %s.",
  "Sempre Ativo": "Siempre Activo",
  "Liberado": "Habilitado",
  "Acesso Remoto Blindado & Bloqueado": "Acceso Remoto Blindado y Bloqueado",
  "O firewall impede conexões da Internet. Para acessar fora de casa, ligue o switch na seção de Redes acima.": "El firewall bloquea las conexiones desde Internet. Para acceder fuera de casa, active el switch en la sección de Redes arriba.",
  "🔒 Segurança máxima: Tráfego da porta 445 100% rejeitado no firewall.": "🔒 Máxima seguridad: El tráfico del puerto 445 se rechaza al 100% en el firewall.",
  "Acesso Remoto Externo (WAN / Internet)": "Acceso Remoto Externo (WAN / Internet)",
  "Blindado / Desativado": "Blindado / Desactivado",
  "🔒 Segurança Ativa: Acesso anônimo restrito a leitura • Gravação exclusiva para contas autorizadas • Descoberta automática via Bonjour e WSDD.": "🔒 Seguridad Activa: Acceso anónimo restringido a lectura • Escritura exclusiva para cuentas autorizadas • Detección automática mediante Bonjour y WSDD.",
  "Status: 💤 Nenhum cliente conectado (em repouso)": "Estado: 💤 Ningún cliente conectado (en reposo)",
  "Status: 🟢 %s cliente(s) conectado(s):": "Estado: 🟢 %s cliente(s) conectado(s):",
  "🪟 Guia de Conexão e Solução de Problemas no Windows": "🪟 Guía de Conexión y Solución de Problemas en Windows",
  "ℹ️ O Windows 10 e Windows 11 já vêm 100% prontos de fábrica!": "ℹ️ ¡Windows 10 y Windows 11 vienen 100% listos de fábrica!",
  "Os protocolos SMBv2 e SMBv3 são nativos e ativados por padrão em qualquer computador moderno. Você NÃO precisa digitar nenhum comando nem habilitar nada para acessar.": "Los protocolos SMBv2 y SMBv3 son nativos y están activados por defecto en cualquier computadora moderna. NO necesita escribir ningún comando ni habilitar nada para conectarse.",
  "🚀 Passo a Passo Simples para Conectar:": "🚀 Pasos Sencillos para Conectarse:",
  "No seu teclado Windows, pressione ": "En su teclado Windows, presione ",
  " (janela Executar).": " (ventana Ejecutar).",
  "Cole o endereço: ": "Pegue la dirección: ",
  " e dê Enter.": " y presione Enter.",
  "Quando pedir usuário e senha, informe uma conta cadastrada no painel (ex: ": "Cuando solicite usuario y contraseña, ingrese una cuenta registrada en el panel (ej: ",
  " ou ": " o ",
  "Marque a opção \"Lembrar minhas credenciais\" para não precisar digitar novamente.": "Marque la opción \"Recordar mis credenciales\" para no tener que ingresarlas de nuevo.",
  "⚙️ Diagnóstico Avançado (Apenas caso tenha alterado o SMB no Windows anteriormente):": "⚙️ Diagnóstico Avanzado (Solo si modificó los ajustes de SMB en Windows previamente):",
  "Se você desativou recursos do Windows no passado e precisa checar/ativar:": "Si deshabilitó funciones de Windows en el pasado y necesita verificar/activar:",
  "Compartilhamento de Arquivos USB (Samba 4)": "Compartición de Archivos USB (Samba 4)",
  "Serviço de compartilhamento Samba 4 com suporte nativo a Windows, macOS e iOS (Apple AAPL).": "Servicio de compartición SMB 3.1.1 y 2.1 basado en el Kernel Linux de alto rendimiento.",
  "Configurações Gerais do Servidor": "Configuración General del Servidor",
  "Nome do Servidor na Rede": "Nombre del Servidor en la Red",
  "Nome de identificação do roteador exibido na rede local (Windows, macOS, etc.).": "Nombre de identificación del router mostrado en la red local (Windows, macOS, etc.).",
  "Grupo de Trabalho (Workgroup)": "Grupo de Trabajo (Workgroup)",
  "Nome do grupo de trabalho de rede SMB (padrão: WORKGROUP).": "Nombre del grupo de trabajo de red SMB (predeterminado: WORKGROUP).",
  "Permitir SMBv1 Legado": "Permitir SMBv1 Legado",
  "Ative apenas se conectar consoles antigos ou TVs legadas sem suporte a SMBv2/v3 (não recomendado por segurança).": "Active solo si conecta consolas antiguas o televisores legados sin soporte SMBv2/v3 (no recomendado por seguridad).",
  "Pastas Compartilhadas": "Carpetas Compartidas",
  "Gerencie o ponto de montagem e as permissões de acesso das pastas na rede local.": "Administre el punto de montaje y los permisos de acceso de las carpetas en la red local.",
  "Nome do Compartilhamento": "Nombre del Recurso Compartido",
  "Caminho no Disco": "Ruta en el Disco",
  "Acesso Convidado (Sem Senha)": "Acceso de Invitados (Sin Contraseña)",
  "Bloquear Gravação para Visitantes (Somente Leitura)": "Bloquear Escritura a Visitantes (Solo Lectura)",
  "Usuários com Permissão de Gravação": "Usuarios con Permiso de Escritura",
  "/mnt (Todos os Discos USB Conectados)": "/mnt (Todos los Discos USB Conectados)",
  "🟢 Montado": "🟢 Montado",
  "🔴 Desmontado": "🔴 Desmontado",
  "Desmontar partição com segurança": "Desmontar partición con seguridad",
  "Montar partição no sistema": "Montar partición en el sistema",
  "Verificar integridade do sistema de arquivos e diagnosticar o disco": "Verificar integridad del sistema de archivos y diagnosticar el disco",
  "Testar velocidade de leitura e gravação no USB 3.0": "Probar velocidad de lectura y escritura en USB 3.0",
  "Formatar o disco com sistema de arquivos EXT4": "Formatear el disco con sistema de archivos EXT4",
  "Alterar Senha": "Cambiar Contraseña",
  "Excluir": "Eliminar",
  "Nova Conta de Rede": "Nueva Cuenta de Red",
  "Senha Padrão: ": "Contraseña Predeterminada: ",
  "Senha Personalizada": "Contraseña Personalizada",
  "Segurança & Isolamento da Conta \"root\":": "Seguridad y Aislamiento de la Cuenta \"root\":",
  "Porta 445 Liberada": "Puerto 445 Abierto",
  "Atenção: Abertura da Porta SMB 445 para a Internet!": "¡Atención: Apertura del Puerto SMB 445 hacia Internet pública!",
  "Aviso de Segurança: ": "Aviso de Seguridad: ",
  "Dúvidas / Ajuda no Windows": "Dudas / Ayuda en Windows",
  "IP não atribuído": "IP no asignada",
  "Tamanho: ": "Tamaño: ",
  "Ponto de Montagem: ": "Punto de Montaje: ",
  "Livre: ": "Libre: ",
  "Usado: ": "Usado: ",
  "Nenhum": "Ninguno",
  "Status: ": "Estado: ",
  "%s cliente(s) ativo(s): ": "%s cliente(s) activo(s): ",
  "💤 Nenhum cliente conectado (em repouso)": "💤 Ningún cliente conectado (en reposo)",
  "🪟 Windows (Explorador via Internet):": "🪟 Windows (Explorador vía Internet):",
  "Pressione Win+R e acesse de fora de casa pelo IP público.": "Presione Win+R y acceda desde fuera de casa por la IP pública.",
  "Conecte remotamente de qualquer lugar pelo celular ou notebook.": "Conéctese de forma remota desde cualquier lugar con su teléfono o portátil.",
  "⚠️ Requer que o provedor não filtre a porta 445 e uso obrigatório de senha forte.": "⚠️ Requiere que el proveedor no bloquee el puerto 445 y el uso obligatorio de contraseñas seguras.",
  "⚠️ Aberto na WAN (Porta 445)": "⚠️ Abierto en WAN (Puerto 445)",
  "🔄 Montar": "🔄 Montar",
  "Detectando sistema de arquivos e montando partição...": "Detectando sistema de archivos y montando partición...",
  "Verificando Integridade do Disco": "Comprobando Integridad del Disco",
  "Executando diagnóstico de integridade no disco...": "Ejecutando diagnóstico de integridad en el disco...",
  "Diagnóstico concluído.": "Diagnóstico concluido.",
  "Diagnóstico do Sistema de Arquivos": "Diagnóstico del Sistema de Archivos",
  "Resultado da Verificação (%s):": "Resultado de la Verificación (%s):",
  "Fechar": "Cerrar",
  "Erro no diagnóstico: %s": "Error en diagnóstico: %s",
  "Testando Velocidade USB 3.0": "Probando Velocidad USB 3.0",
  "Gravando bloco de teste no disco para medir taxa de transferência...": "Escribiendo bloque de prueba en el disco para medir velocidad...",
  "Resultado do Teste de Desempenho": "Resultado de la Prueba de Rendimiento",
  "Concluído com sucesso": "Completado con éxito",
  "Taxa de transferência real registrada no disco %s (%s).": "Tasa de transferencia real registrada en el disco %s (%s).",
  "Erro ao testar velocidade: %s": "Error al probar velocidad: %s",
  "⚠️ Zona de Perigo: Formatar Disco": "⚠️ Zona de Peligro: Formatear Disco",
  "ATENÇÃO: PERDA TOTAL DE DADOS!": "¡ATENCIÓN: PÉRDIDA TOTAL DE DATOS!",
  "Esta ação apagará permanentemente todos os arquivos e pastas da partição %s.": "Esta acción borrará permanentemente todos los archivos y carpetas de la partición %s.",
  "Nome do Disco (Rótulo / Label):": "Nombre del Disco (Etiqueta / Label):",
  "Sistema de Arquivos:": "Sistema de Archivos:",
  "EXT4 - Linux Nativo (Recomendado)": "EXT4 - Linux Nativo (Recomendado)",
  "Digite SIM para confirmar": "Escriba SIM para confirmar",
  "🗑️ Confirmar Formatação": "🗑️ Confirmar Formateo",
  "Formatando %s em EXT4 de alto desempenho... Aguarde.": "Formateando %s en EXT4 de alto rendimiento... Espere.",
  "✓ O disco %s foi formatado com sucesso em EXT4 e remontado!": "✓ ¡El disco %s se formateó con éxito en EXT4 y se volvió a montar!",
  "Erro na formatação: %s": "Error en el formateo: %s",
  "Sincronizando cache de escrita e desmontando partição...": "Sincronizando caché de escritura y desmontando partición...",
  "O disco %s foi ejetado com segurança! Você já pode desconectar o cabo USB.": "¡El disco %s fue expulsado con seguridad! Ya puede desconectar el cable USB.",
  "Ejetando Disco com Segurança": "Expulsando Disco con Seguridad",
  "Erro ao desmontar: %s": "Error al desmontar: %s",
  "🟢 Servidor Online": "🟢 Servidor en Línea",
  "🟡 Servidor Pausado": "🟡 Servidor Pausado",
  "🔴 Desativado": "🔴 Desactivado",
  "🔵 Temporário": "🔵 Temporal",
  "Informe a senha para o novo usuário.": "Ingrese la contraseña para el nuevo usuario.",
  "Informe um nome de usuário válido (apenas letras, números, hífen ou underline).": "Ingrese un nombre de usuario válido (solo letras, números, guión o guión bajo).",
  "Por favor, informe uma senha válida.": "Por favor, introduzca una contraseña válida.",
  "Mostrar Senha": "Mostrar Contraseña",
  "Ocultar Senha": "Ocultar Contraseña",
  "Aplicando Regras de Firewall": "Aplicando Reglas de Firewall",
  "Liberando porta 445 na WAN e recarregando firewall...": "Abriendo puerto 445 en WAN y recargando firewall...",
  "Visível na Rede": "Visible en la Red"
}
};

function getActiveLang() {
	var l = (document.documentElement.lang || '').toLowerCase();
	if ((!l || l === 'auto') && document.body) {
		var m = document.body.className.match(/lang_([a-zA-Z_-]+)/);
		if (m) l = m[1].toLowerCase();
	}
	if ((!l || l === 'auto') && window.L && L.env && L.env.lang) {
		l = L.env.lang.toLowerCase();
	}
	if (!l || l === 'auto') {
		l = (navigator.language || navigator.userLanguage || '').toLowerCase();
	}
	if (l.indexOf('es') === 0) return 'es';
	if (l.indexOf('pt') === 0 || l === 'pt_br' || l === 'pt-br') return 'pt_br';
	return 'en';
}

function _(str) {
	if (!str || typeof str !== 'string') return str;
	var lang = getActiveLang();
	if (lang === 'en' && I18N.en && I18N.en[str]) return I18N.en[str];
	if (lang === 'es' && I18N.es && I18N.es[str]) return I18N.es[str];
	return str;
}

return view.extend({
	load: function() {
		return Promise.all([
			L.resolveDefault(fs.exec('/sbin/block', ['info']), {}),
			L.resolveDefault(fs.exec('/bin/df', ['-h']), {}),
			L.resolveDefault(fs.exec('/bin/netstat', ['-tn']), {}),
			L.resolveDefault(fs.read('/etc/samba/smbpasswd'), ''),
			L.resolveDefault(fs.exec('/usr/sbin/samba4-disk-tool', ['listusers']), {}),
			L.resolveDefault(fs.exec('/usr/sbin/samba4-disk-tool', ['server_status']), {}),
			L.resolveDefault(fs.exec('/usr/sbin/samba4-disk-tool', ['get_permissions']), {}),
			L.resolveDefault(fs.exec('/usr/sbin/samba4-disk-tool', ['get_interfaces_status']), {}),
			L.resolveDefault(fs.exec('/usr/sbin/smbd', ['-V']), {}),
			L.resolveDefault(fs.exec('/sbin/modinfo', ['samba4']), {})
		]);
	},

	render: function(stats) {
		var block_out = (stats[0] && stats[0].stdout) ? stats[0].stdout : '';
		var df_out = (stats[1] && stats[1].stdout) ? stats[1].stdout : '';
		var netstat_out = (stats[2] && stats[2].stdout) ? stats[2].stdout : '';
		var users_db = stats[3] || '';
		var listusers_out = (stats[4] && stats[4].stdout) ? stats[4].stdout : '';
		var srv_status_raw = (stats[5] && stats[5].stdout) ? stats[5].stdout : '{}';
		var user_perms_raw = (stats[6] && stats[6].stdout) ? stats[6].stdout : '{}';
		var ifaces_status_raw = (stats[7] && stats[7].stdout) ? stats[7].stdout : '{}';

		var serverState = { running: 1, enabled: 1, keepalive: 0 };
		try {
			serverState = JSON.parse(srv_status_raw.trim());
		} catch(e) {}

		var userPerms = {};
		try {
			userPerms = JSON.parse(user_perms_raw.trim());
		} catch(e) {}

		var ifacesData = { interfaces: [] };
		try {
			ifacesData = JSON.parse(ifaces_status_raw.trim());
		} catch(e) {}

		var ifacesList = ifacesData.interfaces || [];
		if (ifacesList.length === 0) {
			ifacesList = [
				{ name: 'lan', label: 'Rede Principal (LAN)', ip: '192.168.76.1', enabled: 1, is_core: 1, icon: '🏠', desc: 'Wi-Fi 2.4/5GHz e portas Ethernet da rede doméstica' },
				{ name: 'guest', label: 'Rede de Convidados (Guest)', ip: '192.168.2.1', enabled: 0, is_core: 0, icon: '📶', desc: 'Wi-Fi de Visitas. Conexão isolada para visitantes' },
				{ name: 'iot', label: 'Rede IoT (Dispositivos Inteligentes)', ip: '192.168.3.1', enabled: 0, is_core: 0, icon: '🤖', desc: 'Rede de Smart TVs, consoles e automação residencial' },
				{ name: 'wan', label: 'Acesso Remoto Externo (WAN)', ip: 'indisponivel', enabled: 0, is_core: 0, icon: '🌐', desc: 'Acesso via Internet pública fora de casa (porta 445)' }
			];
		}

		var wanIface = null;
		for (var ifi = 0; ifi < ifacesList.length; ifi++) {
			if (ifacesList[ifi].name === 'wan') {
				wanIface = ifacesList[ifi];
				break;
			}
		}
		var isWanOn = wanIface ? !!(wanIface.enabled) : false;
		var wanIp = (wanIface && wanIface.ip && wanIface.ip !== 'indisponivel') ? wanIface.ip : 'IP_WAN';

		// 1. Clientes com conexões ativas na porta 445 SMB
		var activeClients = [];
		var net_lines = netstat_out.split(/\r?\n/);
		for (var n = 0; n < net_lines.length; n++) {
			if (net_lines[n].indexOf(':445') !== -1 && net_lines[n].indexOf('ESTABLISHED') !== -1) {
				var tokens = net_lines[n].trim().split(/\s+/);
				if (tokens.length >= 5) {
					var clientIp = tokens[4].split(':')[0];
					if (clientIp && activeClients.indexOf(clientIp) === -1) {
						activeClients.push(clientIp);
					}
				}
			}
		}

		// 2. Usuários cadastrados no banco samba4pwd.db
		var dbUsers = [];
		var userHashes = {};
		var user_lines = users_db.split(/\r?\n/);
		for (var u = 0; u < user_lines.length; u++) {
			var parts = user_lines[u].split(':');
			var uname = parts[0] ? parts[0].trim() : '';
			var uhash = parts[3] ? parts[3].trim() : (parts[1] ? parts[1].trim() : '');
			if (uname) {
				if (dbUsers.indexOf(uname) === -1) dbUsers.push(uname);
				userHashes[uname] = uhash;
			}
		}
		if (dbUsers.length === 0) {
			dbUsers = ['root'];
			userHashes['root'] = '259360501E64A8FA345D9A90F73129C7';
		}

		// 3. Discos USB conectados
		var disks = [];
		var block_lines = block_out.split(/\r?\n/);
		for (var i = 0; i < block_lines.length; i++) {
			var line = block_lines[i];
			if (line.indexOf('/dev/sd') !== -1) {
				var parts = line.split(':');
				var dev = parts[0].trim();
				var meta = {};
				var btokens = (parts[1] || '').trim().split(/\s+/);
				for (var t = 0; t < btokens.length; t++) {
					var kv = btokens[t].split('=');
					if (kv.length === 2) {
						meta[kv[0]] = kv[1].replace(/"/g, '');
					}
				}
				var size = '128 GB', used = '0 MB', avail = 'Livre', pct = '0%';
				var df_lines = df_out.split(/\r?\n/);
				for (var d = 0; d < df_lines.length; d++) {
					if (df_lines[d].indexOf(dev) !== -1) {
						var dparts = df_lines[d].trim().split(/\s+/);
						if (dparts.length >= 6) {
							size = dparts[1]; used = dparts[2]; avail = dparts[3]; pct = dparts[4];
						}
					}
				}
				disks.push({
					dev: dev,
					mount: meta.MOUNT || '',
					type: (meta.TYPE || 'desconhecido').toUpperCase(),
					uuid: meta.UUID || '',
					size: size,
					used: used,
					avail: avail,
					pct: pct
				});
			}
		}

		// Helper: Switch Toggle Interativo (Estilo iOS / Material)
		function createToggleSwitch(isChecked, onChange) {
			var checkbox = E('input', {
				'type': 'checkbox',
				'checked': isChecked ? 'checked' : null,
				'style': 'opacity: 0; width: 0; height: 0; position: absolute; margin: 0;'
			});

			var knob = E('span', {
				'style': 'position: absolute; content: ""; height: 18px; width: 18px; left: ' + (isChecked ? '21px' : '3px') + '; bottom: 3px; background-color: #ffffff; transition: all 0.25s ease; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.3); pointer-events: none;'
			});

			var track = E('span', {
				'style': 'position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: ' + (isChecked ? '#28a745' : '#adb5bd') + '; transition: all 0.25s ease; border-radius: 24px;'
			}, [knob]);

			var wrapper = E('label', {
				'style': 'position: relative; display: inline-block; width: 42px; height: 24px; margin: 0; cursor: pointer; vertical-align: middle; flex-shrink: 0;'
			}, [checkbox, track]);

			checkbox.addEventListener('change', function() {
				var checked = checkbox.checked;
				track.style.backgroundColor = checked ? '#28a745' : '#adb5bd';
				knob.style.left = checked ? '21px' : '3px';
				if (typeof onChange === 'function') {
					onChange(checked);
				}
			});

			return {
				wrapper: wrapper,
				input: checkbox,
				setChecked: function(val) {
					checkbox.checked = !!val;
					track.style.backgroundColor = val ? '#28a745' : '#adb5bd';
					knob.style.left = val ? '21px' : '3px';
				}
			};
		}

		// Helper: Campo de Senha com Botão de Olho (Revelar/Ocultar)
		function createPasswordField(placeholderText) {
			var passInput = E('input', {
				'type': 'password',
				'class': 'cbi-input-text',
				'placeholder': placeholderText || _('Digite a senha'),
				'autocomplete': 'new-password',
				'style': 'flex: 1 1 auto; padding: 7px 12px; font-size: 1.05em;'
			});

			var eyeBtn = E('button', {
				'type': 'button',
				'class': 'cbi-button cbi-button-neutral',
				'aria-label': _('Mostrar ou ocultar senha'),
				'title': _('Mostrar / Ocultar Senha'),
				'style': 'padding: 7px 14px; font-size: 1.25em; line-height: 1; border-top-left-radius: 0; border-bottom-left-radius: 0; margin-left: -1px; cursor: pointer; background: #e9ecef; border: 1px solid #ced4da;',
				'click': function(ev) {
					ev.preventDefault();
					if (passInput.type === 'password') {
						passInput.type = 'text';
						eyeBtn.textContent = '🙈';
						eyeBtn.setAttribute('title', _('Ocultar Senha'));
					} else {
						passInput.type = 'password';
						eyeBtn.textContent = '👁️';
						eyeBtn.setAttribute('title', _('Mostrar Senha'));
					}
				}
			}, '👁️');

			var container = E('div', {
				'style': 'display: flex; align-items: stretch; width: 100%;'
			}, [passInput, eyeBtn]);

			return {
				container: container,
				input: passInput,
				toggle: eyeBtn
			};
		}

		// Modal: Confirmação Estrita de Abertura da WAN (Internet)
		function showWanConfirmModal(onConfirm, onCancel) {
			var checkAck = E('input', {
				'type': 'checkbox',
				'id': 'chk_wan_ack',
				'style': 'transform: scale(1.3); margin-right: 12px; margin-top: 3px; cursor: pointer;'
			});

			var confirmBtn = E('button', {
				'id': 'btn_confirm_wan',
				'class': 'cbi-button cbi-button-remove',
				'disabled': 'disabled',
				'style': 'padding: 8px 16px; font-weight: bold; background: #dc3545; border-color: #dc3545; color: #fff; opacity: 0.4; cursor: not-allowed;',
				'click': function() {
					ui.hideModal();
					onConfirm();
				}
			}, _('⚠️ Entendo os Riscos, Liberar Porta WAN'));

			checkAck.addEventListener('change', function() {
				if (checkAck.checked) {
					confirmBtn.removeAttribute('disabled');
					confirmBtn.style.opacity = '1';
					confirmBtn.style.cursor = 'pointer';
				} else {
					confirmBtn.setAttribute('disabled', 'disabled');
					confirmBtn.style.opacity = '0.4';
					confirmBtn.style.cursor = 'not-allowed';
				}
			});

			ui.showModal(_('🚨 Alerta Crítico de Segurança: Acesso Remoto WAN'), [
				E('div', { 'style': 'padding: 6px;' }, [
					E('div', { 'style': 'background: #fff3cd; border: 1px solid #ffeeba; border-left: 5px solid #dc3545; padding: 14px; border-radius: 6px; margin-bottom: 14px;' }, [
						E('h4', { 'style': 'color: #721c24; margin: 0 0 8px 0; font-size: 1.1em; display: flex; align-items: center; gap: 6px;' }, [
							'⚠️ ', _('Atenção: Abertura da Porta SMB 445 para a Internet!')
						]),
						E('p', { 'style': 'margin: 0 0 8px 0; color: #856404; font-size: 0.95em; line-height: 1.45;' }, [
							_('Ao liberar o acesso WAN, o servidor de arquivos Samba ficará exposto a conexões vindas de fora da sua rede local (Internet pública).')
						]),
						E('ul', { 'style': 'margin: 0; padding-left: 20px; color: #721c24; font-size: 0.9em; line-height: 1.5;' }, [
							E('li', {}, _('Robôs e scanners automatizados na Internet detectam portas 445 abertas 24/7 e realizam tentativas contínuas de invasão por força bruta.')),
							E('li', {}, _('Se qualquer conta cadastrada possuir senha fraca ou fácil de adivinhar, seus arquivos podem ser roubados ou vazados na Internet.')),
							E('li', {}, _('Muitos provedores de Internet (ISPs) bloqueiam a porta 445 por padrão por motivos de segurança.'))
						])
					]),
					E('div', { 'style': 'background: #e9ecef; padding: 12px; border-radius: 6px; margin-bottom: 14px;' }, [
						E('strong', { 'style': 'color: #343a40; display: block; margin-bottom: 6px;' }, _('💡 Boas Práticas Recomendadas:')),
						E('div', { 'style': 'font-size: 0.88em; color: #495057; line-height: 1.45;' }, [
							E('p', { 'style': 'margin: 0 0 4px 0;' }, _('✓ 1. Mantenha o Acesso Convidado (Sem Senha) estritamente DESATIVADO.')),
							E('p', { 'style': 'margin: 0 0 4px 0;' }, _('✓ 2. Utilize senhas longas com letras, números e símbolos em todas as contas cadastradas.')),
							E('p', { 'style': 'margin: 0;' }, _('🛡️ 3. Dica de Especialista: Para acesso remoto seguro, prefira utilizar uma VPN (WireGuard/OpenVPN) em vez de expor o Samba diretamente na Internet pública.'))
						])
					]),
					E('div', { 'style': 'display: flex; align-items: flex-start; margin-bottom: 16px; padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px;' }, [
						checkAck,
						E('label', { 'for': 'chk_wan_ack', 'style': 'cursor: pointer; font-size: 0.95em; font-weight: bold; color: #212529;' }, [
							_('Estou ciente dos riscos de segurança e vazamento na Internet e autorizo abrir a porta 445 na WAN.')
						])
					]),
					E('div', { 'style': 'display: flex; justify-content: flex-end; gap: 8px;' }, [
						E('button', {
							'class': 'cbi-button cbi-button-apply',
							'style': 'padding: 8px 16px; font-weight: bold;',
							'click': function() {
								ui.hideModal();
								onCancel();
							}
						}, _('🛡️ Cancelar e Manter Blindado (Recomendado)')),
						confirmBtn
					])
				])
			]);
		}

		// Modal: Guia e Solução de Problemas de Conexão no Windows
		function showWindowsHelpModal() {
			ui.showModal(_('🪟 Guia de Conexão e Solução de Problemas no Windows'), [
				E('div', { 'style': 'padding: 6px;' }, [
					E('div', { 'style': 'background: #e7f3fe; border: 1px solid #b8daff; border-left: 5px solid #007bff; padding: 12px; border-radius: 6px; margin-bottom: 12px;' }, [
						E('h4', { 'style': 'color: #004085; margin: 0 0 6px 0; font-size: 1.05em;' }, _('ℹ️ O Windows 10 e Windows 11 já vêm 100% prontos de fábrica!')),
						E('p', { 'style': 'margin: 0; color: #004085; font-size: 0.9em; line-height: 1.45;' }, [
							_('Os protocolos SMBv2 e SMBv3 são nativos e ativados por padrão em qualquer computador moderno. Você NÃO precisa digitar nenhum comando nem habilitar nada para acessar.')
						])
					]),
					E('div', { 'style': 'background: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; border-radius: 6px; margin-bottom: 12px;' }, [
						E('strong', { 'style': 'display: block; margin-bottom: 8px; color: #212529;' }, _('🚀 Passo a Passo Simples para Conectar:')),
						E('ol', { 'style': 'margin: 0; padding-left: 20px; font-size: 0.9em; color: #495057; line-height: 1.6;' }, [
							E('li', {}, [E('span', {}, _('No seu teclado Windows, pressione ')), E('strong', {}, 'Win + R'), E('span', {}, _(' (janela Executar).'))]),
							E('li', {}, [E('span', {}, _('Cole o endereço: ')), E('strong', { 'style': 'font-family: monospace; color: #0056b3;' }, '\\\\192.168.76.1\\disk'), E('span', {}, _(' e dê Enter.'))]),
							E('li', {}, [E('span', {}, _('Quando pedir usuário e senha, informe uma conta cadastrada no painel (ex: ')), E('strong', {}, 'root'), E('span', {}, ').')]),
							E('li', {}, _('Marque a opção "Lembrar minhas credenciais" para não precisar digitar novamente.'))
						])
					]),
					E('div', { 'style': 'background: #fff3cd; border: 1px solid #ffeeba; padding: 12px; border-radius: 6px; margin-bottom: 12px;' }, [
						E('strong', { 'style': 'display: block; margin-bottom: 6px; color: #856404;' }, _('⚙️ Diagnóstico Avançado (Apenas caso tenha alterado o SMB no Windows anteriormente):')),
						E('p', { 'style': 'font-size: 0.85em; color: #856404; margin: 0 0 6px 0;' }, _('Se você desativou recursos do Windows no passado e precisa checar/ativar:')),
						E('div', { 'style': 'font-size: 0.82em; font-family: monospace; background: #212529; color: #00ff66; padding: 8px; border-radius: 4px; margin-bottom: 6px; white-space: pre-wrap;' }, [
							'# No PowerShell (como Administrador):\n',
							'Get-SmbClientConfiguration | Select EnableSMB2Protocol\n',
							'Set-SmbClientConfiguration -EnableSMB2Protocol $true -Force'
						]),
						E('div', { 'style': 'font-size: 0.82em; font-family: monospace; background: #212529; color: #00ff66; padding: 8px; border-radius: 4px; white-space: pre-wrap;' }, [
							'# No Prompt de Comando (CMD):\n',
							'powershell -Command "Set-SmbClientConfiguration -EnableSMB2Protocol $true -Force"\n',
							'# Ou via DISM nativo no CMD:\n',
							'dism /online /enable-feature /featurename:SMB2Protocol'
						])
					]),
					E('div', { 'style': 'display: flex; justify-content: flex-end;' }, [
						E('button', {
							'class': 'cbi-button cbi-button-apply',
							'style': 'padding: 6px 16px; font-weight: bold;',
							'click': function() {
								ui.hideModal();
							}
						}, _('Entendi / Fechar'))
					])
				])
			]);
		}

		// Modal: Alterar Senha de Usuário
		function showChangePasswordModal(username) {
			var pwdField = createPasswordField(_('Nova senha para %s').format(username));

			var submitBtn = E('button', {
				'class': 'cbi-button cbi-button-apply',
				'style': 'padding: 8px 16px; font-weight: bold;',
				'click': function() {
					var val = pwdField.input.value.trim();
					if (!val) {
						alert(_('Por favor, informe uma senha válida.'));
						pwdField.input.focus();
						return;
					}
					ui.showModal(_('Atualizando Senha'), [
						E('p', { 'class': 'spinning' }, _('Gravando nova senha do usuário "%s"...').format(username))
					]);
					fs.exec('/usr/sbin/samba4-disk-tool', ['setuser', username, val]).then(function() {
						ui.hideModal();
						ui.addNotification(null, E('p', _('✓ Senha do usuário "%s" atualizada com sucesso!').format(username)), 'info');
						window.location.reload();
					}).catch(function(err) {
						ui.hideModal();
						ui.addNotification(null, E('p', _('Erro ao atualizar senha: %s').format(err.message)), 'error');
					});
				}
			}, _('💾 Salvar Nova Senha'));

			ui.showModal(_('🔑 Alterar Senha de Rede: %s').format(username), [
				E('div', { 'style': 'padding: 6px;' }, [
					E('p', { 'style': 'margin-bottom: 12px; color: #495057; font-size: 0.95em;' }, [
						_('Defina uma nova senha para a conta '),
						E('strong', { 'style': 'color: #007bff; font-size: 1.1em;' }, username),
						_('. Esta senha é usada para login na rede via Windows, Mac, iPhone, iPad e Android.')
					]),
					(username === 'root' ? E('div', {
						'style': 'background: #fff3cd; border-left: 4px solid #ffc107; padding: 9px 12px; margin-bottom: 14px; font-size: 0.88em; color: #856404; border-radius: 0 4px 4px 0; line-height: 1.4;'
					}, [
						'⚠️ ', E('strong', {}, _('Aviso de Segurança: ')),
						_('Esta alteração afeta exclusivamente o acesso às pastas de rede (SMB/Samba 4). As senhas do terminal SSH, Telnet e de administração do painel LuCI não são afetadas.')
					]) : E('div', {})),
					E('div', { 'style': 'margin-bottom: 16px;' }, [
						E('label', { 'style': 'font-weight: bold; display: block; margin-bottom: 6px;' }, _('Nova Senha de Rede:')),
						pwdField.container
					]),
					E('div', { 'style': 'display: flex; justify-content: flex-end; gap: 8px; margin-top: 15px;' }, [
						E('button', {
							'class': 'cbi-button cbi-button-neutral',
							'click': function() { ui.hideModal(); }
						}, _('Cancelar')),
						submitBtn
					])
				])
			]);
			setTimeout(function() { pwdField.input.focus(); }, 120);
		}

		// Modal: Adicionar Nova Conta
		function showAddUserModal() {
			var userInput = E('input', {
				'type': 'text',
				'class': 'cbi-input-text',
				'placeholder': 'ex: backup, familia, visitante',
				'autocomplete': 'off',
				'style': 'width: 100%; padding: 7px 12px; font-size: 1.05em;'
			});
			var pwdField = createPasswordField(_('Senha da nova conta'));

			var initialWrite = true;
			var permModalLabel = E('span', { 'style': 'font-size: 0.9em; font-weight: bold; color: #28a745;' }, _('✏️ Leitura e Gravação (Acesso Total)'));
			var permModalToggle = createToggleSwitch(true, function(chk) {
				initialWrite = chk;
				permModalLabel.textContent = chk ? _('✏️ Leitura e Gravação (Acesso Total)') : _('🔒 Somente Leitura (Sem Gravação)');
				permModalLabel.style.color = chk ? '#28a745' : '#e06b00';
			});

			var submitBtn = E('button', {
				'class': 'cbi-button cbi-button-apply',
				'style': 'padding: 8px 16px; font-weight: bold;',
				'click': function() {
					var u = userInput.value.trim().replace(/[^a-zA-Z0-9_.-]/g, '');
					var p = pwdField.input.value.trim();
					if (!u) {
						alert(_('Informe um nome de usuário válido (apenas letras, números, hífen ou underline).'));
						userInput.focus();
						return;
					}
					if (!p) {
						alert(_('Informe a senha para o novo usuário.'));
						pwdField.input.focus();
						return;
					}
					ui.showModal(_('Criando Conta'), [
						E('p', { 'class': 'spinning' }, _('Cadastrando usuário "%s" no Samba 4...').format(u))
					]);
					fs.exec('/usr/sbin/samba4-disk-tool', ['setuser', u, p]).then(function() {
						if (!initialWrite) {
							return fs.exec('/usr/sbin/samba4-disk-tool', ['set_permission', u, 'ro']);
						}
					}).then(function() {
						ui.hideModal();
						ui.addNotification(null, E('p', _('✓ Usuário "%s" criado com sucesso!').format(u)), 'info');
						window.location.reload();
					}).catch(function(err) {
						ui.hideModal();
						ui.addNotification(null, E('p', _('Erro ao cadastrar usuário: %s').format(err.message)), 'error');
					});
				}
			}, _('➕ Criar Usuário'));

			ui.showModal(_('➕ Cadastrar Nova Conta de Rede'), [
				E('div', { 'style': 'padding: 6px;' }, [
					E('div', { 'style': 'margin-bottom: 14px;' }, [
						E('label', { 'style': 'font-weight: bold; display: block; margin-bottom: 6px;' }, _('Nome de Usuário:')),
						userInput,
						E('small', { 'style': 'color: #6c757d;' }, _('Apenas letras, números, underline (_) ou hífen (-).'))
					]),
					E('div', { 'style': 'margin-bottom: 14px;' }, [
						E('label', { 'style': 'font-weight: bold; display: block; margin-bottom: 6px;' }, _('Senha de Rede:')),
						pwdField.container
					]),
					E('div', { 'style': 'margin-bottom: 16px;' }, [
						E('label', { 'style': 'font-weight: bold; display: block; margin-bottom: 6px;' }, _('Permissão Inicial:')),
						E('div', { 'style': 'display: flex; align-items: center; gap: 10px; background: #f8f9fa; padding: 6px 12px; border-radius: 6px; border: 1px solid #e9ecef;' }, [
							permModalToggle.wrapper,
							permModalLabel
						])
					]),
					E('div', { 'style': 'display: flex; justify-content: flex-end; gap: 8px; margin-top: 15px;' }, [
						E('button', {
							'class': 'cbi-button cbi-button-neutral',
							'click': function() { ui.hideModal(); }
						}, _('Cancelar')),
						submitBtn
					])
				])
			]);
			setTimeout(function() { userInput.focus(); }, 120);
		}

		// 4. Painel de Controle de Energia, Estado do Servidor Samba 4 e Acesso WAN
		var srvBadge = null;
		if (serverState.running && serverState.enabled) {
			srvBadge = E('span', { 'style': 'background: #28a745; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85em;' }, _('🟢 Servidor Online'));
		} else if (!serverState.running && serverState.enabled) {
			srvBadge = E('span', { 'style': 'background: #ffc107; color: #212529; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85em;' }, _('🟡 Servidor Pausado'));
		} else if (!serverState.running && !serverState.enabled) {
			srvBadge = E('span', { 'style': 'background: #dc3545; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85em;' }, _('🔴 Desativado'));
		} else {
			srvBadge = E('span', { 'style': 'background: #17a2b8; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85em;' }, _('🔵 Temporário'));
		}

		var btnStart = E('button', {
			'class': 'cbi-button cbi-button-apply',
			'style': 'flex: 1 1 auto; min-width: 100px; text-align: center; padding: 6px 12px;',
			'click': function(ev) {
				ev.preventDefault();
				ui.showModal(_('Iniciando Servidor'), [E('p', { 'class': 'spinning' }, _('Ativando e iniciando Samba 4...'))]);
				fs.exec('/usr/sbin/samba4-disk-tool', ['server_start']).then(function() {
					window.location.reload();
				});
			}
		}, _('▶️ Ligar'));

		var btnPause = E('button', {
			'class': 'cbi-button cbi-button-neutral',
			'style': 'flex: 1 1 auto; min-width: 130px; text-align: center; padding: 6px 12px; background: #ffc107; color: #212529; font-weight: bold;',
			'title': _('Para o serviço agora, mas mantém habilitado para religar no próximo boot do roteador'),
			'click': function(ev) {
				ev.preventDefault();
				ui.showModal(_('Pausando Servidor'), [E('p', { 'class': 'spinning' }, _('Pausando serviço Samba 4...'))]);
				fs.exec('/usr/sbin/samba4-disk-tool', ['server_pause']).then(function() {
					window.location.reload();
				});
			}
		}, _('⏸️ Pausar (Volta no Boot)'));

		var btnRestart = E('button', {
			'class': 'cbi-button cbi-button-action',
			'style': 'flex: 1 1 auto; min-width: 95px; text-align: center; padding: 6px 12px;',
			'click': function(ev) {
				ev.preventDefault();
				ui.showModal(_('Reiniciando Servidor'), [E('p', { 'class': 'spinning' }, _('Reiniciando serviço Samba 4...'))]);
				fs.exec('/usr/sbin/samba4-disk-tool', ['server_restart']).then(function() {
					window.location.reload();
				});
			}
		}, _('🔄 Reiniciar'));

		var btnDisable = E('button', {
			'class': 'cbi-button cbi-button-remove',
			'style': 'flex: 1 1 auto; min-width: 95px; text-align: center; padding: 6px 12px;',
			'title': _('Desativa o servidor permanentemente (inclusive na inicialização do sistema)'),
			'click': function(ev) {
				ev.preventDefault();
				if (confirm(_('Deseja realmente desativar o servidor Samba 4 permanentemente? Ele não iniciará no boot.'))) {
					ui.showModal(_('Desativando Servidor'), [E('p', { 'class': 'spinning' }, _('Parando e desabilitando Samba 4...'))]);
					fs.exec('/usr/sbin/samba4-disk-tool', ['server_disable']).then(function() {
						window.location.reload();
					});
				}
			}
		}, _('⏹️ Desativar'));

		// Toggle 1: Otimização do Motor do HD
		var keepaliveCheckbox = E('input', {
			'type': 'checkbox',
			'id': 'chk_keepalive',
			'checked': serverState.keepalive ? 'checked' : null,
			'style': 'transform: scale(1.3); cursor: pointer; margin-right: 12px; margin-top: 3px;'
		});

		var keepaliveBadge = E('span', { 'style': 'background: ' + (serverState.keepalive ? '#28a745' : '#6c757d') + '; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 0.82em; font-weight: bold; white-space: nowrap;' },
			serverState.keepalive ? _('⚡ Always-On Ativo (Nunca Desliga)') : _('💤 Repouso Automático (~10-15 min)'));

		keepaliveCheckbox.addEventListener('change', function() {
			var isChecked = keepaliveCheckbox.checked;
			ui.showModal(_('Ajustando Modo de Energia do Disco'), [
				E('p', { 'class': 'spinning' }, isChecked ? _('Ativando modo Always-On para prevenir hibernação do HD...') : _('Desativando otimização; permitindo repouso de energia...'))
			]);
			fs.exec('/usr/sbin/samba4-disk-tool', ['keepalive_set', isChecked ? '1' : '0']).then(function() {
				ui.hideModal();
				keepaliveBadge.textContent = isChecked ? _('⚡ Always-On Ativo (Nunca Desliga)') : _('💤 Repouso Automático (~10-15 min)');
				keepaliveBadge.style.background = isChecked ? '#28a745' : '#6c757d';
				ui.addNotification(null, E('p', isChecked ?
					_('✓ Modo Always-On ativado: O HD externo permanecerá 100% ativo sem desligar o motor (resposta instantânea na rede).') :
					_('✓ Modo de repouso ativado: O HD entrará em suspensão automática após 10 a 15 minutos de inatividade para economizar energia.')), 'info');
			}).catch(function(err) {
				ui.hideModal();
				ui.addNotification(null, E('p', _('Erro ao ajustar modo: %s').format(err.message)), 'error');
			});
		});

		var keepaliveBox = E('div', { 'style': 'background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 5px; padding: 12px; display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 10px;' }, [
			E('div', { 'style': 'display: flex; align-items: flex-start; flex: 1 1 260px;' }, [
				keepaliveCheckbox,
				E('label', { 'for': 'chk_keepalive', 'style': 'cursor: pointer;' }, [
					E('strong', { 'style': 'font-size: 1em; color: #212529;' }, _('Prevenir Desligamento / Hibernação Automática do HD')),
					E('div', { 'style': 'margin-top: 4px; font-size: 0.88em; color: #495057; line-height: 1.45;' }, [
						E('p', { 'style': 'margin: 0 0 3px 0;' }, _('⚡ Ativado: Mantém o motor do HD girando 24/7. Elimina congelamentos de 5 a 10s ao abrir arquivos na rede.')),
						E('p', { 'style': 'margin: 0; color: #6c757d;' }, _('💤 Desativado: Economia de energia. O HD suspenderá o motor após 10 a 15 minutos ocioso.'))
					])
				])
			]),
			E('div', { 'style': 'align-self: center;' }, keepaliveBadge)
		]);

		var serverControlCard = E('div', {
			'style': 'background: #ffffff; border: 1px solid #dee2e6; border-radius: 6px; padding: 14px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'
		}, [
			E('div', { 'style': 'display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #eee;' }, [
				E('div', { 'style': 'display: flex; align-items: center; gap: 8px; flex-wrap: wrap;' }, [
					E('strong', { 'style': 'font-size: 1.05em;' }, _('⚙️ Servidor Samba 4:')),
					srvBadge,
					E('span', { 'style': 'background: #6c757d; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 0.82em; font-weight: 500;' }, _('⚡ Samba 4 Engine • SMB 3.1.1 & 2.1 • Apple macOS/iOS'))
				]),
				E('div', { 'style': 'display: flex; align-items: center; flex-wrap: wrap; gap: 6px; flex: 1 1 auto; justify-content: flex-end;' }, [
					(!serverState.running || !serverState.enabled) ? btnStart : '',
					serverState.running ? btnPause : '',
					serverState.running ? btnRestart : '',
					(serverState.running || serverState.enabled) ? btnDisable : ''
				])
			]),
			keepaliveBox
		]);

		// 5. Painel Inteligente de Redes & Interfaces Autorizadas (Samba 4) com Sincronização de Firewall
		var ifaceRows = [];
		for (var k = 0; k < ifacesList.length; k++) {
			(function(iface) {
				var isCore = !!(iface.is_core);
				var isIfaceOn = !!(iface.enabled);
				var ifaceName = iface.name;
				var ifaceLabel = (ifaceName === 'lan') ? _('Rede Principal (LAN)') : ((ifaceName === 'guest') ? _('Rede de Convidados (Guest)') : ((ifaceName === 'iot') ? _('Rede IoT (Dispositivos Inteligentes)') : _('Acesso Remoto Externo (WAN)')));
				var ifaceIp = (iface.ip && iface.ip !== 'indisponivel') ? iface.ip : _('IP não atribuído');
				var ifaceIcon = iface.icon || '🌐';
				var ifaceDesc = (ifaceName === 'lan') ? _('Wi-Fi 2.4/5GHz e portas Ethernet da rede doméstica') : ((ifaceName === 'guest') ? _('Wi-Fi de Visitas. Conexão isolada para visitantes') : ((ifaceName === 'iot') ? _('Rede de Smart TVs, consoles e automação residencial') : _('Acesso via Internet pública fora de casa (porta 445)')));

				var ifBadge = null;
				if (isCore) {
					ifBadge = E('span', {
						'style': 'background: #28a745; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 0.82em; font-weight: bold; white-space: nowrap;'
					}, _('🛡️ Rede Principal (Sempre Ativa)'));
				} else if (ifaceName === 'wan') {
					ifBadge = E('span', {
						'style': 'background: ' + (isIfaceOn ? '#dc3545' : '#6c757d') + '; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 0.82em; font-weight: bold; white-space: nowrap;'
					}, isIfaceOn ? _('⚠️ Aberto na WAN (Porta 445)') : _('🛡️ Blindado (Apenas LAN / Local)'));
				} else {
					ifBadge = E('span', {
						'style': 'background: ' + (isIfaceOn ? '#28a745' : '#6c757d') + '; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 0.82em; font-weight: bold; white-space: nowrap;'
					}, isIfaceOn ? _('🟢 Liberado no Firewall') : _('🔒 Bloqueado no Firewall (Isolado)'));
				}

				var ifToggle = null;
				if (isCore) {
					// LAN is core, always active
					ifToggle = createToggleSwitch(true, null);
					ifToggle.input.setAttribute('disabled', 'disabled');
					ifToggle.wrapper.style.opacity = '0.7';
					ifToggle.wrapper.style.cursor = 'default';
				} else if (ifaceName === 'wan') {
					// WAN requires security confirmation modal
					ifToggle = createToggleSwitch(isIfaceOn, function(newChecked) {
						if (newChecked) {
							showWanConfirmModal(function() {
								ui.showModal(_('Aplicando Regras de Firewall'), [
									E('p', { 'class': 'spinning' }, _('Liberando porta 445 na WAN e recarregando firewall...'))
								]);
								fs.exec('/usr/sbin/samba4-disk-tool', ['set_interface_access', 'wan', '1']).then(function() {
									ui.hideModal();
									ui.addNotification(null, E('p', _('⚠️ AVISO: Acesso remoto via WAN liberado na porta 445. Certifique-se de manter senhas fortes em todas as contas.')), 'warning');
									window.location.reload();
								}).catch(function(err) {
									ui.hideModal();
									ifToggle.setChecked(false);
									ui.addNotification(null, E('p', _('Erro ao liberar WAN: %s').format(err.message)), 'error');
								});
							}, function() {
								ifToggle.setChecked(false);
							});
						} else {
							ui.showModal(_('Blindando Firewall'), [
								E('p', { 'class': 'spinning' }, _('Fechando porta 445 na WAN e blindando o servidor...'))
							]);
							fs.exec('/usr/sbin/samba4-disk-tool', ['set_interface_access', 'wan', '0']).then(function() {
								ui.hideModal();
								ui.addNotification(null, E('p', _('✓ Servidor blindado com sucesso! A porta 445 na WAN foi fechada e o acesso externo bloqueado.')), 'info');
								window.location.reload();
							}).catch(function(err) {
								ui.hideModal();
								ifToggle.setChecked(true);
								ui.addNotification(null, E('p', _('Erro ao bloquear WAN: %s').format(err.message)), 'error');
							});
						}
					});
				} else {
					// Guest or IoT
					ifToggle = createToggleSwitch(isIfaceOn, function(newChecked) {
						var actionVal = newChecked ? '1' : '0';
						var actionTxt = newChecked ? _('Liberando acesso na rede %s e atualizando firewall...').format(ifaceLabel) : _('Bloqueando acesso na rede %s no firewall...').format(ifaceLabel);
						ui.showModal(_('Atualizando Rede & Firewall'), [
							E('p', { 'class': 'spinning' }, actionTxt)
						]);
						fs.exec('/usr/sbin/samba4-disk-tool', ['set_interface_access', ifaceName, actionVal]).then(function() {
							ui.hideModal();
							ui.addNotification(null, E('p', _('✓ Interface %s %s com sucesso!').format(ifaceLabel, newChecked ? 'liberada' : 'bloqueada')), 'info');
							window.location.reload();
						}).catch(function(err) {
							ui.hideModal();
							ifToggle.setChecked(!newChecked);
							ui.addNotification(null, E('p', _('Erro ao atualizar interface: %s').format(err.message)), 'error');
						});
					});
				}

				ifaceRows.push(E('div', {
					'style': 'background: ' + (ifaceName === 'wan' && isIfaceOn ? '#fff8f8' : (isIfaceOn ? '#ffffff' : '#fcfcfc')) + '; border: 1px solid ' + (ifaceName === 'wan' && isIfaceOn ? '#f5c6cb' : '#e9ecef') + '; border-radius: 6px; padding: 12px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;'
				}, [
					E('div', { 'style': 'display: flex; align-items: center; gap: 12px; flex: 1 1 280px;' }, [
						ifToggle.wrapper,
						E('div', {}, [
							E('div', { 'style': 'display: flex; align-items: center; gap: 8px; flex-wrap: wrap;' }, [
								E('strong', { 'style': 'font-size: 1.02em; color: ' + (ifaceName === 'wan' && isIfaceOn ? '#721c24' : '#212529') + ';' }, [ifaceIcon + ' ', ifaceLabel]),
								E('span', { 'style': 'font-family: monospace; font-size: 0.85em; background: #e9ecef; color: #495057; padding: 2px 6px; border-radius: 3px;' }, ifaceIp)
							]),
							E('div', { 'style': 'font-size: 0.85em; color: #6c757d; margin-top: 3px;' }, ifaceDesc)
						])
					]),
					E('div', { 'style': 'align-self: center;' }, ifBadge)
				]));
			})(ifacesList[k]);
		}

		var interfacesCard = E('div', {
			'style': 'background: #ffffff; border: 1px solid #dee2e6; border-radius: 6px; padding: 14px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'
		}, [
			E('div', { 'style': 'margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;' }, [
				E('div', {}, [
					E('strong', { 'style': 'font-size: 1.05em; color: #212529;' }, _('🎛️ Redes & Interfaces Autorizadas (Samba 4)')),
					E('div', { 'style': 'font-size: 0.85em; color: #6c757d; margin-top: 2px;' }, _('Controle por Toggle Switch em quais redes os arquivos ficam disponíveis. As regras de firewall são sincronizadas automaticamente.'))
				]),
				E('span', { 'style': 'background: #17a2b8; color: #fff; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 500;' }, _('⚡ Sincronização Automática com Firewall'))
			]),
			E('div', {}, ifaceRows)
		]);

		// 5. Renderizar Discos USB Conectados
		var diskRows = [];
		if (disks.length === 0) {
			diskRows.push(E('div', { 'style': 'padding: 16px; color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; margin-bottom: 16px;' }, [
				E('strong', {}, 'ℹ️ Nenhum disco USB detectado no momento.'),
				E('p', { 'style': 'margin: 6px 0 0 0;' }, 'Conecte um HD Externo, SSD ou Pendrive na porta USB 3.0 do roteador. Suporte nativo para exFAT, NTFS, FAT32 e EXT4.')
			]));
		} else {
			var diskCards = [];
			for (var k = 0; k < disks.length; k++) {
				(function(dk) {
					var isMounted = !!(dk.mount && dk.mount.length > 0);
					var statusBadge = E('span', {
						'style': 'padding: 2px 8px; border-radius: 4px; background: ' + (isMounted ? '#28a745' : '#dc3545') + '; color: #fff; font-size: 0.82em; font-weight: bold;'
					}, isMounted ? _('🟢 Montado') : _('🔴 Desmontado'));

					var ejectMountBtn = isMounted ?
						E('button', {
							'class': 'cbi-button cbi-button-remove',
							'style': 'flex: 1 1 auto; min-width: 95px; text-align: center; padding: 6px 10px;',
							'title': _('Desmontar partição com segurança'),
							'click': function(ev) {
								ev.preventDefault();
								ui.showModal(_('Ejetando Disco com Segurança'), [
									E('p', { 'class': 'spinning' }, _('Sincronizando cache de escrita e desmontando partição...'))
								]);
								fs.exec('/usr/sbin/samba4-disk-tool', ['umount_disk', dk.dev]).then(function() {
									ui.hideModal();
									ui.addNotification(null, E('p', _('O disco %s foi ejetado com segurança! Você já pode desconectar o cabo USB.').format(dk.dev)), 'info');
									window.location.reload();
								}).catch(function(err) {
									ui.hideModal();
									ui.addNotification(null, E('p', _('Erro ao desmontar: %s').format(err.message)), 'error');
								});
							}
						}, _('⏏️ Ejetar')) :
						E('button', {
							'class': 'cbi-button cbi-button-apply',
							'style': 'flex: 1 1 auto; min-width: 95px; text-align: center; padding: 6px 10px;',
							'title': _('Montar partição no sistema'),
							'click': function(ev) {
								ev.preventDefault();
								ui.showModal(_('Montando Disco'), [
									E('p', { 'class': 'spinning' }, _('Detectando sistema de arquivos e montando partição...'))
								]);
								fs.exec('/usr/sbin/samba4-disk-tool', ['mount_disk', dk.dev]).then(function() {
									ui.hideModal();
									window.location.reload();
								}).catch(function(err) {
									ui.hideModal();
									ui.addNotification(null, E('p', _('Erro ao montar: %s').format(err.message)), 'error');
								});
							}
						}, _('🔄 Montar'));

					var checkfsBtn = E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'style': 'flex: 1 1 auto; min-width: 125px; text-align: center; padding: 6px 10px; background: #6f42c1; color: #fff;',
						'title': _('Verificar integridade do sistema de arquivos e diagnosticar o disco'),
						'click': function(ev) {
							ev.preventDefault();
							ui.showModal(_('Verificando Integridade do Disco'), [
								E('p', { 'class': 'spinning' }, _('Executando diagnóstico de integridade no disco...'))
							]);
							fs.exec('/usr/sbin/samba4-disk-tool', ['checkfs', dk.dev]).then(function(res) {
								ui.hideModal();
								var out = (res && res.stdout) ? res.stdout.trim() : _('Diagnóstico concluído.');
								ui.showModal(_('Diagnóstico do Sistema de Arquivos'), [
									E('div', { 'style': 'padding: 5px;' }, [
										E('div', { 'style': 'margin-bottom: 10px; font-weight: bold; color: #343a40;' }, _('Resultado da Verificação (%s):').format(dk.dev)),
										E('pre', { 'style': 'background: #212529; color: #28a745; padding: 12px; border-radius: 6px; font-size: 0.88em; max-height: 220px; overflow-y: auto; white-space: pre-wrap;' }, out),
										E('div', { 'style': 'text-align: right; margin-top: 15px;' }, [
											E('button', {
												'class': 'cbi-button cbi-button-apply',
												'click': function() { ui.hideModal(); window.location.reload(); }
											}, _('Fechar'))
										])
									])
								]);
							}).catch(function(err) {
								ui.hideModal();
								ui.addNotification(null, E('p', _('Erro no diagnóstico: %s').format(err.message)), 'error');
							});
						}
					}, _('🔍 Diagnóstico / FSCK'));

					var speedBtn = isMounted ? E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'style': 'flex: 1 1 auto; min-width: 120px; text-align: center; padding: 6px 10px; background: #17a2b8; color: #fff;',
						'title': _('Testar velocidade de leitura e gravação no USB 3.0'),
						'click': function(ev) {
							ev.preventDefault();
							ui.showModal(_('Testando Velocidade USB 3.0'), [
								E('p', { 'class': 'spinning' }, _('Gravando bloco de teste no disco para medir taxa de transferência...'))
							]);
							fs.exec('/usr/sbin/samba4-disk-tool', ['benchmark', dk.mount]).then(function(res) {
								ui.hideModal();
								var out = (res && res.stdout) ? res.stdout : '';
								var match = out.match(/([0-9\.]+\s*[M|k|G]?B\/s)/i);
								var speedStr = match ? match[1] : 'Concluído com sucesso';
								ui.showModal(_('Resultado do Teste de Desempenho'), [
									E('div', { 'style': 'text-align: center; padding: 15px;' }, [
										E('div', { 'style': 'font-size: 2em; margin-bottom: 10px;' }, '⚡'),
										E('h3', { 'style': 'color: #28a745; margin: 0 0 10px 0;' }, speedStr),
										E('p', {}, _('Taxa de transferência real registrada no disco %s (%s).').format(dk.dev, dk.type)),
										E('div', { 'style': 'margin-top: 15px;' }, [
											E('button', {
												'class': 'cbi-button cbi-button-apply',
												'click': function() { ui.hideModal(); }
											}, _('Fechar'))
										])
									])
								]);
							}).catch(function(err) {
								ui.hideModal();
								ui.addNotification(null, E('p', _('Erro ao testar velocidade: %s').format(err.message)), 'error');
							});
						}
					}, _('⚡ Testar Velocidade')) : '';

					var formatBtn = E('button', {
						'class': 'cbi-button cbi-button-remove',
						'style': 'flex: 1 1 auto; min-width: 110px; text-align: center; padding: 6px 10px; background: #dc3545; border-color: #dc3545; color: #fff; font-weight: bold;',
						'title': _('Formatar o disco com sistema de arquivos EXT4'),
						'click': function(ev) {
							ev.preventDefault();

							var labelInput = E('input', {
								'type': 'text',
								'class': 'cbi-input-text',
								'value': 'Predator_Storage',
								'style': 'width: 100%; margin-top: 5px; font-weight: bold;'
							});

							var confirmInput = E('input', {
								'type': 'text',
								'class': 'cbi-input-text',
								'placeholder': _('Digite SIM para confirmar'),
								'style': 'width: 100%; margin-top: 8px; font-size: 1.15em; text-align: center; font-weight: bold; border: 2px solid #dc3545; color: #dc3545;'
							});

							var submitFormatBtn = E('button', {
								'class': 'cbi-button cbi-button-remove',
								'disabled': 'disabled',
								'style': 'opacity: 0.4; cursor: not-allowed; font-weight: bold; font-size: 1em; padding: 8px 14px; flex: 2 1 auto; white-space: nowrap; text-align: center;',
								'click': function() {
									var lbl = labelInput.value.trim() || 'Predator_Storage';
									ui.showModal(_('Formatando Disco'), [
										E('p', { 'class': 'spinning' }, _('Formatando %s em EXT4 de alto desempenho... Aguarde.').format(dk.dev))
									]);
									fs.exec('/usr/sbin/samba4-disk-tool', ['format', dk.dev, lbl]).then(function() {
										ui.hideModal();
										ui.addNotification(null, E('p', _('✓ O disco %s foi formatado com sucesso em EXT4 e remontado!').format(dk.dev)), 'info');
										window.location.reload();
									}).catch(function(err) {
										ui.hideModal();
										ui.addNotification(null, E('p', _('Erro na formatação: %s').format(err.message)), 'error');
									});
								}
							}, _('🗑️ Confirmar Formatação'));

							confirmInput.addEventListener('input', function() {
								if (confirmInput.value.trim().toUpperCase() === 'SIM') {
									submitFormatBtn.removeAttribute('disabled');
									submitFormatBtn.style.opacity = '1';
									submitFormatBtn.style.cursor = 'pointer';
								} else {
									submitFormatBtn.setAttribute('disabled', 'disabled');
									submitFormatBtn.style.opacity = '0.4';
									submitFormatBtn.style.cursor = 'not-allowed';
								}
							});

							ui.showModal(_('⚠️ Zona de Perigo: Formatar Disco'), [
								E('div', { 'style': 'padding: 5px;' }, [
									E('div', { 'style': 'background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px; padding: 12px; margin-bottom: 12px; color: #721c24;' }, [
										E('strong', {}, _('ATENÇÃO: PERDA TOTAL DE DADOS!')),
										E('p', { 'style': 'margin: 5px 0 0 0;' }, _('Esta ação apagará permanentemente todos os arquivos e pastas da partição %s.').format(dk.dev))
									]),
									E('div', { 'style': 'margin-bottom: 10px;' }, [
										E('label', { 'style': 'font-weight: bold;' }, _('Nome do Disco (Rótulo / Label):')),
										labelInput
									]),
									E('div', { 'style': 'margin-bottom: 12px;' }, [
										E('label', { 'style': 'font-weight: bold;' }, _('Sistema de Arquivos:')),
										E('select', { 'class': 'cbi-input-select', 'style': 'width: 100%; margin-top: 5px;' }, [
											E('option', { 'value': 'ext4' }, _('EXT4 - Linux Nativo (Recomendado)'))
										])
									]),
									E('div', { 'style': 'background: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; padding: 12px; margin-bottom: 12px; text-align: center;' }, [
										E('strong', { 'style': 'color: #856404;' }, _('Para autorizar, digite "SIM" abaixo:')),
										confirmInput
									]),
									E('div', { 'style': 'display: flex; gap: 8px; margin-top: 12px;' }, [
										E('button', {
											'class': 'cbi-button cbi-button-neutral',
											'style': 'padding: 8px 14px; flex: 1 1 auto; white-space: nowrap; text-align: center;',
											'click': function() { ui.hideModal(); }
										}, _('Cancelar')),
										submitFormatBtn
									])
								])
							]);
						}
					}, _('🗑️ Formatar Disco'));

					diskCards.push(E('div', {
						'style': 'background: #ffffff; border: 1px solid #e0e0e0; border-left: 5px solid #28a745; border-radius: 6px; padding: 14px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'
					}, [
						E('div', { 'style': 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;' }, [
							E('div', { 'style': 'display: flex; align-items: center; flex-wrap: wrap; gap: 6px;' }, [
								E('strong', { 'style': 'font-size: 1.15em; color: #212529;' }, '💾 ' + dk.dev),
								E('span', { 'style': 'padding: 2px 8px; border-radius: 4px; background: #007bff; color: #fff; font-size: 0.82em; font-weight: bold;' }, dk.type),
								statusBadge
							]),
							E('div', { 'style': 'display: flex; align-items: center;' }, [
								E('span', { 'style': 'font-size: 0.9em; color: #6c757d; margin-right: 4px;' }, _('Tamanho: ')),
								E('strong', { 'style': 'font-size: 1.1em; color: #212529;' }, dk.size)
							])
						]),
						E('div', { 'style': 'font-size: 0.92em; color: #495057; display: flex; gap: 15px; flex-wrap: wrap; margin: 8px 0;' }, [
							E('div', {}, [_('Ponto de Montagem: '), E('code', { 'style': 'font-size: 0.95em; padding: 2px 5px;' }, dk.mount || _('Nenhum'))]),
							E('div', {}, [_('Livre: '), E('strong', { 'style': 'color: #28a745;' }, dk.avail)]),
							E('div', {}, [_('Usado: '), E('strong', {}, dk.used + ' (' + dk.pct + ')')] ),
							dk.uuid ? E('div', {}, ['UUID: ', E('small', { 'style': 'color: #888;' }, dk.uuid)]) : ''
						]),
						E('div', { 'style': 'display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; padding-top: 10px; border-top: 1px dashed #e9ecef;' }, [
							speedBtn,
							checkfsBtn,
							ejectMountBtn,
							formatBtn
						])
					]));
				})(disks[k]);
			}
			diskRows.push(E('div', { 'style': 'margin-bottom: 15px;' }, diskCards));
		}

		// 6. Gerenciador de Contas de Rede e Senhas com Toggle Switch de Permissão
		var userCards = [];
		for (var uidx = 0; uidx < dbUsers.length; uidx++) {
			(function(username) {
				var isRoot = (username === 'root');
				var badgeColor = isRoot ? '#dc3545' : (username === 'admin' ? '#fd7e14' : '#007bff');
				var roleText = isRoot ? _('👑 Administrador Master') : (username === 'admin' ? _('⭐ Administrador') : _('👤 Usuário Autorizado'));
				var hasWrite = (userPerms[username] !== 'ro');

				var permLabel = E('span', {
					'style': 'font-size: 0.88em; font-weight: bold; color: ' + (hasWrite ? '#28a745' : '#e06b00') + '; white-space: nowrap;'
				}, hasWrite ? _('✏️ Leitura e Gravação') : _('🔒 Somente Leitura'));

				var permToggle = createToggleSwitch(hasWrite, function(newChecked) {
					permLabel.textContent = newChecked ? _('✏️ Leitura e Gravação') : _('🔒 Somente Leitura');
					permLabel.style.color = newChecked ? '#28a745' : '#e06b00';

					fs.exec('/usr/sbin/samba4-disk-tool', ['set_permission', username, newChecked ? 'rw' : 'ro']).then(function() {
						ui.addNotification(null, E('p', newChecked ?
							_('✓ Permissão da conta "%s" atualizada: Leitura e Gravação (Acesso Total).').format(username) :
							_('✓ Permissão da conta "%s" atualizada: Somente Leitura (Gravação Bloqueada).').format(username)
						), 'info');
					}).catch(function(err) {
						permToggle.setChecked(!newChecked);
						permLabel.textContent = !newChecked ? _('✏️ Leitura e Gravação') : _('🔒 Somente Leitura');
						permLabel.style.color = !newChecked ? '#28a745' : '#e06b00';
						ui.addNotification(null, E('p', _('Erro ao alterar permissão: %s').format(err.message)), 'error');
					});
				});

				var permBox = E('div', {
					'style': 'display: inline-flex; align-items: center; gap: 8px; background: #f1f3f5; padding: 4px 10px; border-radius: 18px; border: 1px solid #dee2e6;'
				}, [
					permToggle.wrapper,
					permLabel
				]);

				var changePassBtn = E('button', {
					'class': 'cbi-button cbi-button-action',
					'style': 'padding: 5px 12px; font-size: 0.88em; display: inline-flex; align-items: center; gap: 4px;',
					'title': _('Alterar senha da conta %s').format(username),
					'click': function(ev) {
						ev.preventDefault();
						showChangePasswordModal(username);
					}
				}, ['🔑 ', _('Alterar Senha')]);

				var deleteBtn = (!isRoot) ? E('button', {
					'class': 'cbi-button cbi-button-remove',
					'style': 'padding: 5px 12px; font-size: 0.88em; display: inline-flex; align-items: center; gap: 4px;',
					'title': _('Remover conta %s').format(username),
					'click': function(ev) {
						ev.preventDefault();
						if (confirm(_('Deseja realmente remover o usuário "%s"?').format(username))) {
							ui.showModal(_('Removendo Usuário'), [
								E('p', { 'class': 'spinning' }, _('Removendo conta %s...').format(username))
							]);
							fs.exec('/usr/sbin/samba4-disk-tool', ['deluser', username]).then(function() {
								ui.hideModal();
								ui.addNotification(null, E('p', _('Usuário %s removido com sucesso.').format(username)), 'info');
								window.location.reload();
							}).catch(function(err) {
								ui.hideModal();
								ui.addNotification(null, E('p', _('Erro ao remover usuário: %s').format(err.message)), 'error');
							});
						}
					}
				}, ['🗑️ ', _('Excluir')]) : E('span', { 'style': 'color: #888; font-size: 0.85em; font-weight: bold; padding: 4px 8px;' }, _('🔒 Protegido'));

				var isDefaultPass = (userHashes[username] === '259360501E64A8FA345D9A90F73129C7');
				var passBadge = isDefaultPass ? E('span', {
					'style': 'background: #e8f5e9; color: #1b5e20; border: 1px solid #c8e6c9; padding: 3px 8px; border-radius: 4px; font-size: 0.82em; font-weight: bold; display: inline-flex; align-items: center; gap: 4px;',
					'title': _('Esta conta está usando a senha padrão de fábrica root0100.')
				}, [
					'🔑 ', _('Senha Padrão: '),
					E('code', { 'style': 'background: #ffffff; padding: 1px 5px; border-radius: 3px; font-weight: bold; color: #155724;' }, 'root0100')
				]) : E('span', {
					'style': 'background: #f8f9fa; color: #495057; border: 1px solid #ced4da; padding: 3px 8px; border-radius: 4px; font-size: 0.82em; font-weight: bold; display: inline-flex; align-items: center; gap: 4px;',
					'title': _('A senha desta conta foi alterada e personalizada.')
				}, ['🔒 ', _('Senha Personalizada')]);

				var rootNotice = isRoot ? E('div', {
					'style': 'font-size: 0.82em; color: #6c757d; margin-top: 6px; display: flex; align-items: center; gap: 5px;'
				}, [
					E('span', { 'style': 'color: #007bff; font-weight: bold;' }, 'ℹ️'),
					E('span', {}, _('Conta exclusiva para compartilhamento de rede (SMB). Não possui vínculo com o root nativo do Linux e NÃO afeta o acesso SSH, Telnet ou login do painel.'))
				]) : null;

				userCards.push(E('div', {
					'style': 'padding: 12px 14px; border-bottom: 1px solid #eee;'
				}, [
					E('div', { 'style': 'display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;' }, [
						E('div', { 'style': 'display: flex; align-items: center; gap: 10px; flex-wrap: wrap;' }, [
							E('strong', { 'style': 'font-size: 1.08em; color: #212529;' }, username),
							E('span', { 'style': 'background: ' + badgeColor + '; color: #fff; padding: 3px 9px; border-radius: 4px; font-size: 0.82em; font-weight: bold;' }, roleText),
							passBadge,
							permBox
						]),
						E('div', { 'style': 'display: flex; gap: 6px; align-items: center; flex-wrap: wrap;' }, [
							changePassBtn,
							deleteBtn
						])
					]),
					rootNotice
				]));
			})(dbUsers[uidx]);
		}

		var btnAddUser = E('button', {
			'class': 'cbi-button cbi-button-apply',
			'style': 'padding: 6px 14px; font-size: 0.9em; font-weight: bold; display: inline-flex; align-items: center; gap: 5px;',
			'click': function(ev) {
				ev.preventDefault();
				showAddUserModal();
			}
		}, ['➕ ', _('Nova Conta de Rede')]);

		var accountsCard = E('div', {
			'style': 'background: #ffffff; border: 1px solid #dee2e6; border-radius: 6px; margin-bottom: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden;'
		}, [
			E('div', { 'style': 'background: #f8f9fa; padding: 12px 16px; border-bottom: 1px solid #dee2e6; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;' }, [
				E('div', {}, [
					E('strong', { 'style': 'font-size: 1.05em; color: #212529;' }, _('👥 Contas de Acesso & Senhas (Samba 4)')),
					E('div', { 'style': 'font-size: 0.85em; color: #6c757d; margin-top: 2px;' }, _('Gerencie contas e controle visualmente permissões de escrita ou somente leitura via toggle switch.'))
				]),
				btnAddUser
			]),
			E('div', {
				'style': 'background: #f0f7ff; border-left: 4px solid #007bff; padding: 10px 14px; margin: 12px 14px 10px 14px; border-radius: 0 6px 6px 0; font-size: 0.88em; color: #1c3d5a; line-height: 1.45;'
			}, [
				E('div', { 'style': 'font-weight: bold; margin-bottom: 3px; display: flex; align-items: center; gap: 6px;' }, [
					'💡 ', _('Segurança & Isolamento da Conta "root":')
				]),
				E('p', { 'style': 'margin: 0;' }, _('O usuário root exibido abaixo pertence exclusivamente ao serviço de arquivos Samba 4 (SMB). Ele não tem qualquer vínculo com a conta root nativa do sistema operacional Linux. Alterar ou manter a senha aqui NÃO altera nem afeta o SSH, Telnet ou o acesso administrativo do painel LuCI.'))
			]),
			E('div', {}, userCards)
		]);

		// 7. Guia Rápido de Acesso Multi-Rede Dinâmico (Windows, Apple, Android)
		var accessBoxes = [];

		for (var ai = 0; ai < ifacesList.length; ai++) {
			var aIface = ifacesList[ai];
			var aName = aIface.name;
			var aLabel = aIface.label || aName;
			var aIp = (aIface.ip && aIface.ip !== 'indisponivel') ? aIface.ip : null;
			var aEnabled = !!(aIface.enabled);
			var aIcon = aIface.icon || '🌐';

			if (aName === 'wan') {
				// WAN box: shown active or shielded
				var wanBox = E('div', {
					'style': 'background: ' + (aEnabled ? '#fff8f8' : '#fdfdfe') + '; padding: 14px; border-radius: 6px; border: 1px solid ' + (aEnabled ? '#f5c6cb' : '#dee2e6') + '; flex: 1 1 300px; display: flex; flex-direction: column; justify-content: space-between;'
				}, [
					E('div', {}, [
						E('div', { 'style': 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid ' + (aEnabled ? '#f8d7da' : '#f1f3f5') + '; padding-bottom: 6px;' }, [
							E('strong', { 'style': 'font-size: 1.02em; color: ' + (aEnabled ? '#721c24' : '#495057') + '; display: flex; align-items: center; gap: 6px;' }, [
								'🌐 ', _('Acesso Remoto Externo (WAN / Internet)')
							]),
							E('span', { 'style': 'background: ' + (aEnabled ? '#dc3545' : '#6c757d') + '; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.78em; font-weight: bold;' }, aEnabled ? _('Porta 445 Liberada') : _('Blindado / Desativado'))
						]),
						aEnabled ? E('div', {}, [
							E('div', { 'style': 'margin-bottom: 10px;' }, [
								E('div', { 'style': 'font-size: 0.88em; font-weight: bold; color: #721c24; display: flex; align-items: center; gap: 4px;' }, _('🪟 Windows (Explorador via Internet):')),
								E('div', { 'style': 'margin-top: 3px; background: #ffffff; border: 1px solid #f5c6cb; border-radius: 4px; padding: 6px 10px; font-family: monospace; font-size: 1.05em; color: #dc3545; word-break: break-all;' }, '\\\\' + (aIp || 'IP_WAN') + '\\disk'),
								E('small', { 'style': 'color: #856404; font-size: 0.82em;' }, _('Pressione Win+R e acesse de fora de casa pelo IP público.'))
							]),
							E('div', { 'style': 'margin-bottom: 8px;' }, [
								E('div', { 'style': 'font-size: 0.88em; font-weight: bold; color: #721c24; display: flex; align-items: center; gap: 4px;' }, _('🍎 iPhone / iPad / Mac / Android:')),
								E('div', { 'style': 'margin-top: 3px; background: #ffffff; border: 1px solid #f5c6cb; border-radius: 4px; padding: 6px 10px; font-family: monospace; font-size: 1.05em; color: #dc3545; word-break: break-all;' }, 'smb://' + (aIp || 'IP_WAN') + '/disk'),
								E('small', { 'style': 'color: #856404; font-size: 0.82em;' }, _('Conecte remotamente de qualquer lugar pelo celular ou notebook.'))
							])
						]) : E('div', { 'style': 'padding: 18px 8px; text-align: center; color: #6c757d;' }, [
							E('div', { 'style': 'font-size: 1.8em; margin-bottom: 6px;' }, '🛡️'),
							E('strong', { 'style': 'font-size: 0.95em; color: #343a40; display: block;' }, _('Acesso Remoto Blindado & Bloqueado')),
							E('p', { 'style': 'font-size: 0.85em; margin: 4px 0 0 0; line-height: 1.4;' }, _('O firewall impede conexões da Internet. Para acessar fora de casa, ligue o switch na seção de Redes acima.'))
						])
					]),
					E('div', { 'style': 'margin-top: 6px; padding-top: 6px; border-top: 1px dashed ' + (aEnabled ? '#f5c6cb' : '#e9ecef') + ';' }, [
						aEnabled ?
							E('small', { 'style': 'color: #dc3545; font-size: 0.8em; line-height: 1.4; display: block;' }, _('⚠️ Requer que o provedor não filtre a porta 445 e uso obrigatório de senha forte.')) :
							E('small', { 'style': 'color: #6c757d; font-size: 0.8em;' }, _('🔒 Segurança máxima: Tráfego da porta 445 100% rejeitado no firewall.'))
					])
				]);
				accessBoxes.push(wanBox);
			} else if (aEnabled && aIp) {
				// Internal active interfaces (LAN, Guest, IoT)
				var isLan = (aName === 'lan');
				var boxBadgeColor = isLan ? '#28a745' : '#17a2b8';
				var boxBadgeText = isLan ? _('Sempre Ativo') : _('Liberado');

				var intBox = E('div', {
					'style': 'background: #ffffff; padding: 14px; border-radius: 6px; border: 1px solid #dee2e6; flex: 1 1 300px; display: flex; flex-direction: column; justify-content: space-between;'
				}, [
					E('div', {}, [
						E('div', { 'style': 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #f1f3f5; padding-bottom: 6px;' }, [
							E('strong', { 'style': 'font-size: 1.02em; color: #155724; display: flex; align-items: center; gap: 6px;' }, [
								aIcon + ' ', (aName === 'lan') ? _('Rede Principal (LAN)') : ((aName === 'guest') ? _('Rede de Convidados (Guest)') : ((aName === 'iot') ? _('Rede IoT (Dispositivos Inteligentes)') : _(aLabel)))
							]),
							E('span', { 'style': 'background: ' + boxBadgeColor + '; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.78em; font-weight: bold;' }, boxBadgeText)
						]),
						E('div', { 'style': 'margin-bottom: 10px;' }, [
							E('div', { 'style': 'font-size: 0.88em; font-weight: bold; color: #495057; display: flex; align-items: center; gap: 4px;' }, _('🪟 Windows (Explorador de Arquivos):')),
							E('div', { 'style': 'margin-top: 3px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 6px 10px; font-family: monospace; font-size: 1.05em; color: #0056b3; word-break: break-all;' }, '\\\\' + aIp + '\\disk'),
							E('small', { 'style': 'color: #6c757d; font-size: 0.82em;' }, _('Pressione Win+R e cole o endereço no Windows.'))
						]),
						E('div', { 'style': 'margin-bottom: 8px;' }, [
							E('div', { 'style': 'font-size: 0.88em; font-weight: bold; color: #495057; display: flex; align-items: center; gap: 4px;' }, _('🍎 iPhone / iPad / Mac / Android:')),
							E('div', { 'style': 'margin-top: 3px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 6px 10px; font-family: monospace; font-size: 1.05em; color: #0056b3; word-break: break-all;' }, 'smb://' + aIp + '/disk'),
							E('small', { 'style': 'color: #6c757d; font-size: 0.82em;' }, _('No iOS: App Arquivos > "..." > Conectar ao Servidor. No Mac: Finder > Cmd+K.'))
						])
					]),
					E('div', { 'style': 'margin-top: 6px; padding-top: 6px; border-top: 1px dashed #e9ecef;' }, [
						E('small', { 'style': 'color: #28a745; font-weight: 500;' }, _('✓ Acesso interno direto via IP %s.').format(aIp))
					])
				]);
				accessBoxes.push(intBox);
			}
		}

		var winHelpBtn = E('button', {
			'class': 'cbi-button cbi-button-action',
			'style': 'padding: 5px 12px; font-size: 0.85em; display: inline-flex; align-items: center; gap: 5px;',
			'click': function(ev) {
				ev.preventDefault();
				showWindowsHelpModal();
			}
		}, ['❓ ', _('Dúvidas / Ajuda no Windows')]);

		var accessCard = E('div', {
			'style': 'background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 14px; margin-bottom: 18px;'
		}, [
			E('div', { 'style': 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;' }, [
				E('h4', { 'style': 'margin: 0; font-size: 1.05em; color: #343a40;' }, _('🌐 Como Acessar os Arquivos na Rede:')),
				winHelpBtn
			]),
			E('div', { 'style': 'display: flex; flex-wrap: wrap; gap: 12px;' }, accessBoxes),
			E('div', { 'style': 'display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 10px; border-top: 1px solid #dee2e6; flex-wrap: wrap; gap: 8px;' }, [
				E('div', { 'style': 'font-size: 0.88em; color: #28a745; font-weight: 500;' }, _('🔒 Segurança Ativa: Acesso anônimo restrito a leitura • Gravação exclusiva para contas autorizadas • Descoberta automática via Bonjour e WSDD.')),
				E('div', { 'style': 'font-size: 0.88em; color: #495057;' }, [
					_('Status: '),
					activeClients.length > 0 ?
						E('span', { 'style': 'font-weight: bold; color: #007bff;' }, '👥 ' + _('%s cliente(s) ativo(s): ').format(activeClients.length) + activeClients.join(', ')) :
						E('span', { 'style': 'color: #6c757d;' }, _('💤 Nenhum cliente conectado (em repouso)'))
				])
			])
		]);

		// 8. Formulário Principal LuCI (Configurações Gerais & Pastas Compartilhadas sem Abas Triplas)
		var m = new form.Map('samba4', _('Compartilhamento de Arquivos USB (Samba 4)'), _('Serviço de compartilhamento Samba 4 com suporte nativo a Windows, macOS e iOS (Apple AAPL).'));

		// Seção 1: Configurações Gerais do Servidor (Sem abas!)
		var s = m.section(form.TypedSection, 'samba', _('Configurações Gerais do Servidor'));
		s.anonymous = true;

		var o = s.option(form.Value, 'description', _('Nome do Servidor na Rede'), _('Nome de identificação do roteador exibido na rede local (Windows, macOS, etc.).'));
		o.placeholder = 'OpenRouter';
		o.default = 'OpenRouter';

		o = s.option(form.Value, 'workgroup', _('Grupo de Trabalho (Workgroup)'), _('Nome do grupo de trabalho de rede SMB (padrão: WORKGROUP).'));
		o.placeholder = 'WORKGROUP';
		o.default = 'WORKGROUP';

		s.option(form.Flag, 'allow_legacy_protocols', _('Permitir SMBv1 Legado'), _('Ative apenas se conectar consoles antigos ou TVs legadas sem suporte a SMBv2/v3 (não recomendado por segurança).'));

		// Seção 2: Pastas Compartilhadas no Disco
		s = m.section(form.TableSection, 'sambashare', _('Pastas Compartilhadas'), _('Gerencie o ponto de montagem e as permissões de acesso das pastas na rede local.'));
		s.anonymous = true;
		s.addremove = true;

		o = s.option(form.Value, 'name', _('Nome do Compartilhamento'));
		o.placeholder = 'disk';
		o.default = 'disk';

		o = s.option(form.Value, 'path', _('Caminho no Disco'));
		o.placeholder = '/mnt/sda1';
		o.value('/mnt', _('/mnt (Todos os Discos USB Conectados)'));
		for (var p = 0; p < disks.length; p++) {
			if (disks[p].mount) {
				o.value(disks[p].mount, disks[p].mount + ' (' + disks[p].dev + ' - ' + disks[p].size + ')');
			}
		}

		o = s.option(form.Flag, 'guest_ok', _('Acesso Convidado (Sem Senha)'));
		o.enabled = 'yes';
		o.disabled = 'no';
		o.default = 'yes';
		o.rmempty = false;

		o = s.option(form.Flag, 'read_only', _('Bloquear Gravação (Somente Leitura)'));
		o.enabled = 'yes';
		o.disabled = 'no';
		o.default = 'no';
		o.rmempty = false;

		o = s.option(form.Flag, 'force_root', _('Forçar Usuário Root (Permissão Total na Escrita)'));
		o.enabled = '1';
		o.disabled = '0';
		o.default = '1';
		o.rmempty = false;

		o = s.option(form.Flag, 'timemachine', _('🍎 Compatível com Apple Time Machine (Backup Mac)'));
		o.enabled = '1';
		o.disabled = '0';
		o.default = '0';

		o = s.option(form.Value, 'timemachine_maxsize', _('Limite Apple Time Machine (GB)'));
		o.placeholder = '500';
		o.depends('timemachine', '1');

		o = s.option(form.MultiValue, 'users', _('Usuários com Acesso Restrito (Vazio = Todos)'));
		for (var u = 0; u < dbUsers.length; u++) {
			o.value(dbUsers[u]);
		}
		o.rmempty = true;

		o = s.option(form.Flag, 'browseable', _('Visível na Rede'));
		o.enabled = 'yes';
		o.disabled = 'no';
		o.default = 'yes';

		
		// Seção 3: Editor de Configuração Avançada (Template do Samba)
		s = m.section(form.TypedSection, 'samba', _('⚙️ Ajustes Avançados & Template'));
		s.anonymous = true;
		o = s.option(form.Flag, 'enable_extra_tuning', _('⚡ Otimização de Desempenho (Tuning)'), _('Ativa buffer de 128KB, fake oplocks e envio rápido zero-copy.'));
		o = s.option(form.Flag, 'disable_async_io', _('Forçar E/S Síncrona'), _('Evita operações assíncronas em dispositivos mais lentos.'));
		o = s.option(form.Flag, 'disable_netbios', _('Desativar NetBIOS Legado (Apenas Porta 445)'), _('Desativa portas 137-139 e acelera descoberta SMB moderna.'));
		o = s.option(form.TextValue, '_tmpl', _('Editar Template do Samba (/etc/samba/smb.conf.template)'), _('Edite os parâmetros globais do Samba 4 diretamente aqui.'));
		o.rows = 14;
		o.cfgvalue = function(section_id) { return fs.trimmed('/etc/samba/smb.conf.template'); };
		o.write = function(section_id, formvalue) { return fs.write('/etc/samba/smb.conf.template', formvalue.trim() + '\n'); };

		return m.render().then(function(map_node) {
			return E('div', {}, [
				serverControlCard,
				interfacesCard,
				E('h3', { 'style': 'margin-top: 15px; margin-bottom: 12px;' }, _('📦 Armazenamento USB Conectado:')),
				E('div', {}, diskRows),
				accountsCard,
				accessCard,
				map_node
			]);
		});
	}
});
