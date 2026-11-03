# Interface, aplicativos e performance

A instalação original do Android foi preservada. A tela inicial usada no estudo foi o [CleanYourTV](https://github.com/Gathin23/cleanyourtv), com adaptação local ao botão Home da variante. Este repositório referencia o projeto original e não redistribui seu código ou launcher sob a licença MIT daqui.

O inventário foi comparado com a [lista HY320 do CleanYourTV](https://github.com/Gathin23/cleanyourtv/blob/main/examples/hy320/debloat.txt). A lista serviu como pista: cada componente restante foi avaliado pelo que fazia na unidade. O conjunto histórico removido está em `data/packages.json`, sem comando automático de desinstalação.

Foram preservados componentes de HDMI/TV input, ajuste de projeção/keystone, som, controle, teclado e espelhamento AirPlay/Miracast. Apps com nomes pouco claros podem ser dependências do hardware; um nome estranho não basta para classificá-los como dispensáveis ou maliciosos.

O proprietário manteve apps de mídia e jogos, incluindo VLC, Moonlight, Better xCloud e Switch Frame Tap. Pacotes comerciais, assinaturas, credenciais, arquivos do Drive e APKs não são distribuídos. Para obter apps, consulte os canais oficiais de cada projeto e sua compatibilidade com ARM de 32 bits/Android do seu aparelho.

## Performance

A CPU foi mantida dentro das frequências já oferecidas pelo sistema. O teto observado foi `1464000` kHz, e o governador passou de `schedutil` para `performance` em regras específicas dos arquivos de inicialização do fabricante. A proteção térmica ficou habilitada. Não houve overclock, alteração de tensão ou desbloqueio de frequências.

A mudança persistente foi feita em três ocorrências previamente conferidas, em dois arquivos daquela variante. Esses arquivos proprietários completos e um patch automático para outros firmwares não são redistribuídos aqui. Um patch para outra placa precisa de comparação e recuperação próprias.

O projetor apresentou temperaturas elevadas em etapas de carga. Performance não é uma medida de segurança nem garante melhor experiência em toda carga; a referência preservou a limitação térmica e não recomenda removê-la.

## Atualizações e permissões

Os apps selecionados, a interface e o gerenciador de arquivos receberam `REQUEST_INSTALL_PACKAGES=ignore`. Isso reduz instalação de APKs a partir desses apps e pode impedir atualizadores internos. Atualizações pelo ADB autorizado ou pela Play Store permanecem vias separadas; isso não comprova certificação Play Protect.

Desativar pacotes por usuário mantém seus APKs de sistema disponíveis para reversão. Remover cópias antigas de reinstalação também exige guardar cópias verificadas. A lista histórica não foi executada como parte da publicação deste repositório.
