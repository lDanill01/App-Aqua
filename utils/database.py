import json
import os
from typing import List, Dict, Optional

class DatabaseProdutos:
    """
    Classe para gerenciar o banco de dados de produtos de ração.
    Fornece métodos para buscar produtos por semana e obter informações detalhadas.
    """
    
    def __init__(self, caminho_arquivo: str):
        """
        Inicializa o database carregando o arquivo JSON.
        
        Args:
            caminho_arquivo: Caminho para o arquivo JSON (ex: 'data/produtos_racao.json')
        """
        self.caminho_arquivo = caminho_arquivo
        self.dados = self._carregar()
        self.configuracoes = self.dados.get('configuracoes', [])
    
    def _carregar(self) -> Dict:
        """Carrega o arquivo JSON do banco de dados."""
        try:
            # Tenta carregar o arquivo
            if not os.path.exists(self.caminho_arquivo):
                raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")
            
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            print(f"✓ Database carregado com sucesso: {self.caminho_arquivo}")
            return dados
        
        except FileNotFoundError as e:
            print(f"✗ Erro: {e}")
            return {"configuracoes": []}
        except json.JSONDecodeError as e:
            print(f"✗ Erro ao decodificar JSON: {e}")
            return {"configuracoes": []}
    
    def obter_produto(self, semana: int) -> str:
        """
        Retorna o nome do produto para uma semana específica.
        
        Args:
            semana: Número da semana (1-57)
        
        Returns:
            Nome do produto ou "Não definido" se não encontrar
        """
        for config in self.configuracoes:
            if config['semanas_inicio'] <= semana <= config['semanas_fim']:
                return config['produto']
        return "Não definido"
    
    def obter_detalhes_produto(self, semana: int) -> Dict:
        """
        Retorna todos os detalhes do produto para uma semana específica.
        
        Args:
            semana: Número da semana (1-57)
        
        Returns:
            Dicionário com todas as informações do produto
        """
        for config in self.configuracoes:
            if config['semanas_inicio'] <= semana <= config['semanas_fim']:
                return config
        return {}
    
    def obter_todos_produtos(self, num_semanas: int) -> List[str]:
        """
        Retorna lista de produtos para todas as semanas.
        
        Args:
            num_semanas: Número total de semanas (ex: 57)
        
        Returns:
            Lista com o nome do produto para cada semana
        """
        return [self.obter_produto(i) for i in range(1, num_semanas + 1)]
    
    def obter_todos_detalhes(self, num_semanas: int) -> List[Dict]:
        """
        Retorna detalhes completos de todos os produtos por semana.
        
        Args:
            num_semanas: Número total de semanas (ex: 57)
        
        Returns:
            Lista de dicionários com todos os detalhes
        """
        return [self.obter_detalhes_produto(i) for i in range(1, num_semanas + 1)]
    
    def obter_proteina(self, semana: int) -> float:
        """Retorna o percentual de proteína do produto da semana."""
        detalhes = self.obter_detalhes_produto(semana)
        return detalhes.get('proteina', 0)
    
    def obter_granulometria(self, semana: int) -> str:
        """Retorna a granulometria do produto da semana."""
        detalhes = self.obter_detalhes_produto(semana)
        return detalhes.get('granulometria', 'N/A')
    
    def obter_preco(self, semana: int) -> float:
        """Retorna o preço (por 1000 peixes) do produto da semana."""
        detalhes = self.obter_detalhes_produto(semana)
        return detalhes.get('preco', 0)
    
    def obter_observacao(self, semana: int) -> str:
        """Retorna a observação do produto da semana."""
        detalhes = self.obter_detalhes_produto(semana)
        return detalhes.get('observacao', '')
    
    def listar_todos_registros(self) -> List[Dict]:
        """Retorna todos os registros do database."""
        return self.configuracoes
    
    def obter_registros_por_intervalo(self, semana_ini: int, semana_fim: int) -> List[Dict]:
        """
        Retorna registros que cobrem um intervalo de semanas.
        
        Args:
            semana_ini: Semana inicial
            semana_fim: Semana final
        
        Returns:
            Lista de registros que cobrem o intervalo
        """
        registros = []
        for config in self.configuracoes:
            # Verifica se o registro se sobrepõe ao intervalo
            if (config['semanas_inicio'] <= semana_fim and 
                config['semanas_fim'] >= semana_ini):
                registros.append(config)
        return registros
    
    def validar_cobertura(self, num_semanas: int) -> Dict:
        """
        Valida se todas as semanas têm um produto definido.
        
        Args:
            num_semanas: Número total de semanas a validar
        
        Returns:
            Dicionário com informações sobre cobertura e lacunas
        """
        semanas_cobertas = set()
        semanas_sem_cobertura = []
        
        for config in self.configuracoes:
            for s in range(config['semanas_inicio'], config['semanas_fim'] + 1):
                if s <= num_semanas:
                    semanas_cobertas.add(s)
        
        for s in range(1, num_semanas + 1):
            if s not in semanas_cobertas:
                semanas_sem_cobertura.append(s)
        
        return {
            'total_semanas': num_semanas,
            'semanas_cobertas': len(semanas_cobertas),
            'semanas_sem_cobertura': semanas_sem_cobertura,
            'cobertura_percentual': (len(semanas_cobertas) / num_semanas) * 100,
            'valido': len(semanas_sem_cobertura) == 0
        }
    
    def imprimir_relatorio(self, num_semanas: int = 57) -> None:
        """Imprime um relatório completo do database."""
        print("\n" + "="*80)
        print("RELATÓRIO DO DATABASE DE PRODUTOS")
        print("="*80)
        print(f"Versão: {self.dados.get('versao', 'N/A')}")
        print(f"Última Atualização: {self.dados.get('ultima_atualizacao', 'N/A')}")
        print(f"Total de Registros: {len(self.configuracoes)}")
        
        # Validação
        validacao = self.validar_cobertura(num_semanas)
        print(f"\nCobertura: {validacao['cobertura_percentual']:.1f}%")
        print(f"Semanas Cobertas: {validacao['semanas_cobertas']}/{validacao['total_semanas']}")
        
        if validacao['semanas_sem_cobertura']:
            print(f"⚠ Semanas sem cobertura: {validacao['semanas_sem_cobertura']}")
        else:
            print("✓ Todas as semanas possuem produtos definidos!")
        
        print("\nRegistros:")
        print("-"*80)
        for config in self.configuracoes:
            print(f"ID {config['id']}: Semanas {config['semanas_inicio']}-{config['semanas_fim']}")
            print(f"  Produto: {config['produto']}")
            print(f"  Proteína: {config['proteina']}% | Granulometria: {config['granulometria']}")
            print(f"  Preço: R$ {config['preco']:.2f} | {config['observacao']}")
            print()
        print("="*80 + "\n")