# -*- coding: utf-8 -*-

import configparser
import pymysql
import os
import logging

# Configuração do logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Carregamento do arquivo de configuração
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)


class Consulta:
    @staticmethod
    def info():
        """Retorna informações do banco de dados e host."""
        try:
            return [config['database']['database'], config['database']['host']]
        except KeyError as e:
            logger.error(f"Erro ao acessar configuração: chave {e} não encontrada no config.ini")
            return ["", ""]

    @staticmethod
    def result(pesquisa=""):
        """Busca projetos no banco de dados com base no termo de pesquisa."""
        if not pesquisa:
            return 'noProjects'

        logger.info(f"Iniciando pesquisa para: '{pesquisa}'")

        projetos = []
        try:
            with pymysql.connect(
                user=config['database'].get('user'),
                password=config['database'].get('password'),
                host=config['database'].get('host'),
                database=config['database'].get('database'),
                connect_timeout=5
            ) as cnx:
                with cnx.cursor() as cursor:
                    logger.debug("Conexão com banco de dados estabelecida.")
                    
                    # Se pesquisa for '***', retorna tudo
                    if pesquisa == "***":
                        query = "SELECT project_product, project_title, project_backup_date, project_path FROM project"
                        cursor.execute(query)
                    else:
                        query = """SELECT project_product, project_title, project_backup_date, project_path 
                                   FROM project 
                                   WHERE LOWER(project_product) LIKE %s 
                                      OR LOWER(project_title) LIKE %s 
                                      OR LOWER(project_path) LIKE %s"""
                        termo = f"%{pesquisa.lower()}%"
                        cursor.execute(query, (termo, termo, termo))

                    resultados = cursor.fetchall()

                    if not resultados:
                        logger.info("Nenhum projeto encontrado.")
                        return 'noProjects'

                    projetos = [
                        {
                            'product': str(row[0]) if row[0] else '',
                            'title': str(row[1]) if row[1] else '',
                            'backup_date': str(row[2]) if row[2] else '',
                            'path': str(row[3]) if row[3] else ''
                        }
                        for row in resultados
                    ]

                    logger.info(f"{len(projetos)} projetos encontrados.")
                    return projetos

        except pymysql.MySQLError as err:
            logger.error(f"Erro na conexão ou execução da query: {str(err)}")
            return 'noServer'
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return 'noServer'

# Consulta.result('test')
