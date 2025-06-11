import re
from typing import List, Dict


class Aula:
    def __init__(self, nome: str, professor: str, duracao_min: int):
        self.nome = nome
        self.professor = professor
        self.duracao_min = duracao_min


class Intervalo:
    def __init__(self, inicio: int, fim: int):
        self.inicio = inicio
        self.fim = fim

    def conflita(self, outro: 'Intervalo') -> bool:
        return self.inicio < outro.fim and outro.inicio < self.fim


def carregar_aulas(caminho_arquivo: str) -> List[Aula]:
    aulas = []

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            for i, linha in enumerate(arquivo, 1):
                linha = linha.strip()
                if not linha or '-' not in linha:
                    print(f"❌ Linha {i} ignorada: formato inválido ou sem '-': \"{linha}\"")
                    continue

                partes = linha.split('-')
                if len(partes) < 2:
                    print(f"❌ Linha {i} ignorada: esperado 'Aula - Prof. Nome Duração'")
                    continue

                nome_aula = partes[0].strip()
                detalhes = partes[1].strip()

                if not detalhes:
                    print(f"❌ Linha {i} ignorada: nome do professor ausente.")
                    continue

                palavras = detalhes.split()
                nome_professor = palavras[1] if len(palavras) >= 2 else palavras[0]

                match = re.search(r"-?\d+", detalhes)
                if not match:
                    print(f"❌ Linha {i} ignorada: duração ausente ou inválida: \"{linha}\"")
                    continue

                try:
                    duracao = int(match.group())
                    if duracao <= 0:
                        raise ValueError
                except ValueError:
                    print(f"❌ Linha {i} ignorada: duração não positiva: \"{linha}\"")
                    continue

                aulas.append(Aula(nome_aula, nome_professor, duracao))

    except IOError as e:
        print("Erro ao ler o arquivo:", e)

    return aulas


def gerar_cronograma(aulas: List[Aula]) -> List[str]:
    cronograma = []
    agenda_professores: Dict[str, List[Intervalo]] = {}
    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]

    indice = 0
    for dia in dias:
        cronograma.append(f"📅 {dia}")
        indice = alocar_turno(aulas, cronograma, indice, 9, 12, agenda_professores)
        indice = alocar_turno(aulas, cronograma, indice, 13, 17, agenda_professores)
        cronograma.append("17:00 Reunião de professores (obrigatória)")

        if indice >= len(aulas):
            break

    return cronograma


def alocar_turno(aulas: List[Aula], cronograma: List[str], inicio_indice: int,
                 hora_inicio: int, hora_fim: int, agenda: Dict[str, List[Intervalo]]) -> int:

    hora = hora_inicio
    minuto = 0
    fim_turno = hora_fim * 60
    i = inicio_indice

    while i < len(aulas):
        aula = aulas[i]
        inicio = hora * 60 + minuto
        fim = inicio + aula.duracao_min

        if fim > fim_turno:
            break

        intervalo = Intervalo(inicio, fim)
        compromissos = agenda.get(aula.professor, [])

        if any(existing.conflita(intervalo) for existing in compromissos):
            i += 1
            continue

        agenda.setdefault(aula.professor, []).append(intervalo)

        horario_str = f"{hora:02d}:{minuto:02d}"
        cronograma.append(f"{horario_str} {aula.nome} - Prof. {aula.professor} {aula.duracao_min} min")

        minuto += aula.duracao_min
        hora += minuto // 60
        minuto %= 60
        i += 1

    return i


if __name__ == "__main__":
    caminho = "aulas.txt"
    aulas = carregar_aulas(caminho)

    if not aulas:
        print("Nenhuma aula válida encontrada.")
    else:
        for linha in gerar_cronograma(aulas):
            print(linha)
