# Trabalho_Final_ES/models/dados_alunos.py
import re
import os
from PyPDF2 import PdfReader
from models.model_ia import IAModel
from datetime import datetime

class DadosAlunos:
    def __init__(self, debug=False):
        self.dadosAlunos = []
        self.debug = debug
        self.debug_dir = "debug_logs"
        os.makedirs(self.debug_dir, exist_ok=True)

    def _log_debug(self, message, file_prefix=""):
        """Registra mensagens de debug quando habilitado"""
        if self.debug:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(self.debug_dir, f"{file_prefix}_{timestamp}.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{message}\n")

    def lerProvas(self, provas_paths: list[str]):
        """Lê as provas dos alunos com mecanismos de debug avançados"""
        self._log_debug("Iniciando leitura de provas", "lerProvas")
        
        self.dadosAlunos = []
        resultados_debug = []

        for idx, path in enumerate(provas_paths):
            try:
                self._log_debug(f"\nProcessando arquivo {idx+1}/{len(provas_paths)}: {path}", "file_processing")
                
                # 1. Extração do texto
                reader = PdfReader(path)
                texto_bruto = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
                
                # Debug: Salva texto bruto extraído
                debug_file = os.path.join(self.debug_dir, f"raw_text_{os.path.basename(path)}.txt")
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(texto_bruto)
                self._log_debug(f"Texto bruto salvo em {debug_file}", "extraction")

                # 2. Parse do cabeçalho
                header_data = self._parse_header(texto_bruto, path)
                self._log_debug(f"Cabeçalho identificado: {header_data}", "header")

                # 3. Parse das questões
                respostas, debug_info = self._parse_questoes(texto_bruto)
                resultados_debug.append(debug_info)
                
                # 4. Armazenamento dos dados
                self.dadosAlunos.append({
                    "nome": header_data["nome"],
                    "ra": header_data["ra"],
                    "respostas": respostas,
                    "nota": 0,
                    "justificativas": [""] * len(respostas),
                    "debug_info": debug_info  # Apenas para debug
                })

            except Exception as e:
                error_msg = f"Erro ao processar {path}: {str(e)}"
                self._log_debug(error_msg, "error")
                resultados_debug.append({"arquivo": path, "erro": str(e)})
                continue

        # Gera relatório consolidado de debug
        self._generate_debug_report(resultados_debug)
        print("MODEL: Processamento concluído. Verifique os logs em", self.debug_dir)

    def _parse_header(self, texto_bruto: str, path: str) -> dict:
        """Extrai informações do cabeçalho com múltiplos padrões"""
        padroes = [
            r"Nome:\s*(.*?)\s*RA:\s*(\d+)",
            r"Aluno:\s*(.*?)\s*Matrícula:\s*(\d+)",
            r"Nome do aluno:\s*(.*?)\s*Registro:\s*(\d+)"
        ]

        for padrao in padroes:
            match = re.search(padrao, texto_bruto, re.IGNORECASE | re.DOTALL)
            if match:
                return {"nome": match.group(1).strip(), "ra": match.group(2)}

        # Fallback: usa nome do arquivo se não encontrar padrão
        nome_arquivo = os.path.splitext(os.path.basename(path))[0]
        return {"nome": nome_arquivo, "ra": "0000000"}

    def _parse_questoes(self, texto_bruto: str) -> tuple:
        """Extrai respostas das questões com detalhamento de debug"""
        respostas = []
        debug_info = {
            "questoes": [],
            "erros": []
        }

        # Padrão para identificar questões
        padrao_questao = r"""
            \(\s*(\d+)\s*\)                # Número da questão
            \s*(.*?)\s*                    # Enunciado
            \(\s*([\d.]+)\s*(?:Pontos|pts?)  # Pontos
            \s*\)\s*
            (.*?)                          # Corpo da questão
            (?=\(\s*\d+\s*\)|\Z)          # Lookahead para próxima questão
        """
        
        questoes = re.finditer(padrao_questao, texto_bruto, re.VERBOSE | re.DOTALL | re.IGNORECASE)

        for i, questao in enumerate(questoes, 1):
            try:
                numero = questao.group(1)
                corpo = questao.group(4).strip()
                questao_debug = {
                    "numero": numero,
                    "corpo_original": corpo,
                    "resposta_extraida": None,
                    "tipo": None
                }

                # Verifica tipo de questão
                if re.search(r"^[A-E]\)", corpo, re.MULTILINE):
                    questao_debug["tipo"] = "objetiva"
                    resposta = self._parse_resposta_objetiva(corpo, questao_debug)
                elif "R:" in corpo:
                    questao_debug["tipo"] = "dissertativa"
                    resposta = self._parse_resposta_dissertativa(corpo, questao_debug)
                else:
                    questao_debug["tipo"] = "desconhecido"
                    resposta = "FORMATO_NÃO_RECONHECIDO"

                questao_debug["resposta_extraida"] = resposta
                respostas.append(resposta)
                debug_info["questoes"].append(questao_debug)

            except Exception as e:
                error_msg = f"Erro na questão {i}: {str(e)}"
                debug_info["erros"].append(error_msg)
                respostas.append("ERRO_DE_PROCESSAMENTO")
                continue

        return respostas, debug_info

    def _parse_resposta_objetiva(self, corpo: str, debug_info: dict) -> str:
        """Extrai resposta de questão objetiva com debug detalhado"""
        debug_info["alternativas"] = []
        
        # Padrão para alternativas (A) texto [X] ou A) [X] texto
        padrao_alternativas = r"""
            ([A-E])\)                      # Letra da alternativa
            \s*
            (?:\[(.*?)\]\s*)?             # Marcador [X] opcional
            (.*?)                          # Texto da alternativa
            (?=\s*[A-E]\)|\s*R:|\Z)       # Lookahead
        """
        
        alternativas = re.finditer(padrao_alternativas, corpo, re.VERBOSE | re.IGNORECASE)
        resposta = "N/A"

        for alt in alternativas:
            letra = alt.group(1).upper()
            marcador = alt.group(2) or ""
            texto = alt.group(3).strip()
            
            debug_info["alternativas"].append({
                "letra": letra,
                "marcador": marcador,
                "texto": texto
            })

            # Considera marcado se tiver X, ✓, ou texto em negrito
            if re.search(r"[X✓✔✗]|bold|strong", marcador, re.IGNORECASE):
                resposta = letra

        return resposta

    def _parse_resposta_dissertativa(self, corpo: str, debug_info: dict) -> str:
        """Extrai resposta dissertativa com tratamento de multi-linhas"""
        match = re.search(
            r"R:\s*(.*?)(?=\(\d+\)|\Z)",
            corpo,
            re.DOTALL | re.IGNORECASE
        )
        
        if match:
            resposta = match.group(1).strip()
            # Remove múltiplos espaços e quebras de linha extras
            resposta = ' '.join(resposta.split())
            return resposta
        return ""

    def _generate_debug_report(self, resultados: list):
        """Gera relatório consolidado de debug"""
        report_file = os.path.join(self.debug_dir, "debug_report.html")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("<html><head><title>Relatório de Debug</title></head><body>")
            f.write("<h1>Relatório de Processamento de Provas</h1>")
            
            for idx, resultado in enumerate(resultados):
                f.write(f"<h2>Arquivo {idx+1}</h2>")
                
                if "erro" in resultado:
                    f.write(f"<p style='color:red'><strong>ERRO:</strong> {resultado['erro']}</p>")
                    continue
                
                f.write("<h3>Questões</h3><table border='1'><tr><th>Número</th><th>Tipo</th><th>Resposta</th><th>Detalhes</th></tr>")
                
                for questao in resultado.get("questoes", []):
                    f.write("<tr>")
                    f.write(f"<td>{questao.get('numero', '')}</td>")
                    f.write(f"<td>{questao.get('tipo', '')}</td>")
                    f.write(f"<td>{questao.get('resposta_extraida', '')}</td>")
                    
                    detalhes = "<ul>"
                    if questao.get("tipo") == "objetiva":
                        for alt in questao.get("alternativas", []):
                            detalhes += f"<li>{alt['letra']}) {alt['texto']} [Marcador: {alt['marcador']}]</li>"
                    else:
                        detalhes += f"<li>{questao.get('corpo_original', '')}</li>"
                    detalhes += "</ul>"
                    
                    f.write(f"<td>{detalhes}</td>")
                    f.write("</tr>")
                
                f.write("</table>")
                
                if resultado.get("erros"):
                    f.write("<h3>Erros</h3><ul>")
                    for erro in resultado["erros"]:
                        f.write(f"<li style='color:red'>{erro}</li>")
                    f.write("</ul>")
            
            f.write("</body></html>")

    # ... (métodos calcularNota e validarNota permanecem iguais) ...

    def calcularNota(self, gabarito: list, estrutura_prova: list):
        """Calcula a nota de cada aluno baseado no gabarito"""
        print("MODEL: Iniciando cálculo de notas...")
        if not gabarito:
            print("MODEL: Aviso - Gabarito está vazio. Impossível calcular notas.")
            return
        
        ia = IAModel()

        for aluno in self.dadosAlunos:
            nota_final = 0
            aluno["justificativas"] = [""] * len(estrutura_prova)

            for i, resposta_aluno in enumerate(aluno["respostas"]):
                if i >= len(gabarito) or i >= len(estrutura_prova):
                    continue
                
                questao_atual = estrutura_prova[i]
                resposta_correta = gabarito[i]
                tipo_questao = questao_atual.get('tipo')

                if tipo_questao == 'discursiva':
                    pergunta = questao_atual.get('pergunta', '')
                    pontos_questao = questao_atual.get('pontos', 0)
                    
                    if not resposta_aluno or resposta_aluno == "N/A":
                        aluno['justificativas'][i] = "Sem resposta"
                        continue

                    avaliacao = ia.avaliar_resposta_aluno(
                        pergunta=pergunta,
                        gabarito=resposta_correta,
                        resposta_aluno=resposta_aluno,
                        nota_maxima=pontos_questao
                    )
                    
                    nota_atribuida = min(float(avaliacao.get('nota', 0)), float(pontos_questao))
                    nota_final += nota_atribuida
                    aluno['justificativas'][i] = avaliacao.get('justificativa', '')

                elif tipo_questao == 'multipla_escolha':
                    if resposta_aluno.upper() == resposta_correta.upper():
                        nota_final += questao_atual.get('pontos', 0)
                        aluno['justificativas'][i] = "Resposta correta"
                    else:
                        aluno['justificativas'][i] = f"Resposta incorreta (Esperado: {resposta_correta})"
            
            aluno['nota'] = round(nota_final, 2)
        
        print("MODEL: Notas calculadas com sucesso.")

    @staticmethod
    def validarNota(novo_valor, valor_max_str):
        """Valida se uma nota está no formato correto"""
        if novo_valor == "":
            return True
        try:
            valor_max = float(valor_max_str)
            nota = float(novo_valor)
        except ValueError:
            return False
        return 0 <= nota <= valor_max