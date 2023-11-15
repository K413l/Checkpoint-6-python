from flask import Flask, request, jsonify
import oracledb

app = Flask(__name__)
conn = oracledb.connect('seu_usuario/sua_senha@localhost:1521/seu_banco_de_dados')
cursor = conn.cursor()

# Rotas da API
@app.route('/medalhas', methods=['GET'])
def obter_medalhas():
    cursor.execute("SELECT * FROM medalhas")
    medalhas = cursor.fetchall()
    medalhas_json = formatar_medalhas_json(medalhas)
    return jsonify(medalhas_json)

@app.route('/medalhas/quadro', methods=['GET'])
def obter_quadro_medalhas():
    cursor.execute("""
        SELECT p.id, p.nome as pais, 
               COUNT(CASE WHEN m.medalha = 'ouro' THEN 1 END) as ouro,
               COUNT(CASE WHEN m.medalha = 'prata' THEN 1 END) as prata,
               COUNT(CASE WHEN m.medalha = 'bronze' THEN 1 END) as bronze,
               COUNT(*) as total
        FROM paises p
        LEFT JOIN medalhas m ON p.id = m.pais_id
        GROUP BY p.id, p.nome
        ORDER BY ouro DESC, prata DESC, bronze DESC
    """)
    quadro_medalhas = cursor.fetchall()
    quadro_medalhas_json = formatar_quadro_medalhas_json(quadro_medalhas)
    return jsonify(quadro_medalhas_json)

@app.route('/medalhas/<int:id_pais>', methods=['GET'])
def obter_medalhas_pais(id_pais):
    cursor.execute("""
        SELECT m.modalidade, m.genero, m.medalha
        FROM medalhas m
        WHERE m.pais_id = :id_pais
    """, {'id_pais': id_pais})
    medalhas_pais = cursor.fetchall()
    medalhas_pais_json = formatar_medalhas_pais_json(medalhas_pais)
    return jsonify(medalhas_pais_json)

def formatar_medalhas_json(medalhas):
    medalhas_json = []
    for medalha in medalhas:
        medalha_dict = {
            "id": medalha[0],
            "modalidade": medalha[1],
            "genero": medalha[2],
            "pais": medalha[3],
            "atletas": medalha[5].split(', '),
            "medalha": medalha[6]
        }
        medalhas_json.append(medalha_dict)
    return medalhas_json

def formatar_quadro_medalhas_json(quadro_medalhas):
    quadro_medalhas_json = []
    for posicao, linha in enumerate(quadro_medalhas, start=1):
        quadro_dict = {
            "posicao": posicao,
            "pais": linha[1],
            "ouro": linha[2],
            "prata": linha[3],
            "bronze": linha[4],
            "total": linha[5]
        }
        quadro_medalhas_json.append(quadro_dict)
    return quadro_medalhas_json

def formatar_medalhas_pais_json(medalhas_pais):
    ouro = []
    prata = []
    bronze = []
    for medalha in medalhas_pais:
        if medalha[2] == 'ouro':
            ouro.append(f"{medalha[1]} {medalha[0]}")
        elif medalha[2] == 'prata':
            prata.append(f"{medalha[1]} {medalha[0]}")
        elif medalha[2] == 'bronze':
            bronze.append(f"{medalha[1]} {medalha[0]}")
    return {
        "pais": medalhas_pais[0][1],
        "ouro": ouro,
        "prata": prata,
        "bronze": bronze
    }


@app.route('/medalhas', methods=['POST'])
def adicionar_medalha():
    medalha = request.get_json()
    inserir_atualizar_medalha(medalha)
    return jsonify({"message": "Medalha adicionada com sucesso!"}), 201

@app.route('/medalhas/<int:id_medalha>', methods=['PUT'])
def atualizar_medalha(id_medalha):
    medalha = request.get_json()
    # Adicione lógica para atualizar a medalha com o ID fornecido
    # ...
    return jsonify({"message": "Medalha atualizada com sucesso!"})

@app.route('/medalhas/<int:id_medalha>', methods=['DELETE'])
def deletar_medalha(id_medalha):
    # Adicione lógica para excluir a medalha com o ID fornecido
    # ...
    return jsonify({"message": "Medalha deletada com sucesso!"})

# Função para inserir ou atualizar uma medalha no banco de dados
def inserir_atualizar_medalha(medalha):
    # Implemente a lógica para gerar o ID da medalha
    # ...

    # Inserir ou atualizar o país na tabela de países
    cursor.execute("""
        INSERT INTO paises (nome) VALUES (:pais) ON DUPLICATE KEY UPDATE id=id RETURNING id INTO :pais_id
    """, {'pais': medalha['pais'].lower(), 'pais_id': cursor.var(oracledb.NUMBER)})
    pais_id = cursor.var(oracledb.NUMBER)
    cursor.execute("SELECT id INTO :pais_id FROM paises WHERE nome = :pais", {'pais': medalha['pais'].lower()})
    pais_id = pais_id.getvalue()

    # Inserir a medalha na tabela de medalhas
    cursor.execute("""
        INSERT INTO medalhas (id, modalidade, genero, pais_id, atletas, medalha)
        VALUES (:id, :modalidade, :genero, :pais_id, :atletas, :medalha)
    """, {'id': 1, 'modalidade': medalha['modalidade'], 'genero': medalha['genero'],
          'pais_id': pais_id, 'atletas': ', '.join(medalha['atletas']), 'medalha': medalha['medalha']})

# ... (funções auxiliares aqui)

if __name__ == '__main__':
    app.run(debug=True)
