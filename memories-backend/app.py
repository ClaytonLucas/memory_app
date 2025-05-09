from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime
from flask_cors import CORS
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///memories.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

db = SQLAlchemy(app)
CORS(app)
memory_tags = db.Table('memory_tags',
    db.Column('memory_id', db.Integer, db.ForeignKey('memory.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Memory(db.Model):
    __tablename__ = "memory"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=False)  # Aumentei o tamanho para descrições maiores
    image = db.Column(db.String(255))  # Pode armazenar URLs de imagens
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Garante um padrão
    tags = db.relationship('Tag', secondary=memory_tags, backref=db.backref('memories', lazy='dynamic'))

    def __init__(self, title, description, image, date=None):
        self.title = title
        self.description = description
        self.image = image
        self.date = date if date else datetime.utcnow()  # Se não passar data, usa a data atual

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),  # Formata a data para JSON
            'tags': [tag.name for tag in self.tags]
        }
    
with app.app_context():
    db.create_all()

@app.route('/test', methods=['GET'])
def test():
    """Rota de teste."""
    return make_response(jsonify({'message': 'Test route'}), 200)




@app.route('/memory', methods=['POST'])
def create_memory():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ("title", "description", "image")):
            return make_response(jsonify({"error": "Missing fields: 'title', 'description', 'image'"}), 400)

        date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S') if 'date' in data else datetime.utcnow()
        tags_list = data.get("tags", []) 
        new_memory = Memory(title=data['title'], description=data['description'], image=data['image'], date=date)

        for tag_name in tags_list:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_memory.tags.append(tag)
        
        db.session.add(new_memory)
        db.session.commit()

        return make_response(jsonify({'message': 'Memory created', 'memory': new_memory.json()}), 201)
    except Exception as e:
        app.logger.error(f"Error creating memory: {str(e)}")
        return make_response(jsonify({'message': 'Error creating memory'}), 500)

# @app.route('/memories', methods=['GET'])
# def get_memories():
#     try:
#         memories = Memory.query.all()
#         return make_response(jsonify({'memories': [memory.json() for memory in memories]}), 200)

#     except Exception as e:
#         app.logger.error(f"Error creating user: {str(e)}")
#         return make_response(jsonify({'message': 'Error fetching memories'}), 500)
    
@app.route('/memories', methods=['GET'])
def get_memories():
    try:
        # Pegando os parâmetros de paginação e ordenação
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        order = request.args.get('order', 'desc', type=str).lower()

        # Definindo a ordenação
        if order == 'asc':
            order_by = Memory.date.asc()
        else:
            order_by = Memory.date.desc()

        # Aplicando paginação e ordenação
        memories_paginated = Memory.query.order_by(order_by).paginate(page=page, per_page=limit, error_out=False)

        return make_response(jsonify({
            'total': memories_paginated.total,
            'page': page,
            'limit': limit,
            'memories': [memory.json() for memory in memories_paginated.items]
        }), 200)

    except Exception as e:
        app.logger.error(f"Error fetching memories: {str(e)}")
        return make_response(jsonify({'message': 'Error fetching memories'}), 500)

@app.route('/memories/<int:id>', methods=["GET"])
def get_memory(id):
    try:
        memory = Memory.query.get(id)
        if memory:
            return make_response(jsonify({"memory": memory.json()}), 200)
        return make_response(jsonify({'memory': 'Memory not found'}), 404)
    except Exception as e:
        app.logger.error(f"Error fetching memory: {str(e)}")
        return make_response(jsonify({'message': 'Error fetching memory'}), 500)
    
@app.route('/memories/<int:id>', methods=['DELETE'])
def delete_memory(id):
    try:
        memory = Memory.query.get(id)
        if memory:
            db.session.delete(memory)
            db.session.commit()
            return make_response(jsonify({'message': 'Memory deleted'}), 200)
        return make_response(jsonify({'message': 'Memory not found'}), 404)
    except Exception as e:
        app.logger.error(f"Error deleting memory: {str(e)}")
        return make_response(jsonify({'message': 'error deleting memory'}), 500)
    
@app.route('/memories/<int:id>', methods=['PUT'])
def update_memory(id):
    try:
        data = request.get_json()
        memory = Memory.query.get(id)

        if not memory:
            return make_response(jsonify({'error': "Memory not found"}), 404)

        memory.title = data.get("title", memory.title)
        memory.description = data.get("description", memory.description)
        memory.image = data.get("image", memory.image)

        if "date" in data:
            memory.date = datetime.strptime(data["date"], '%Y-%m-%d %H:%M:%S')

        if "tags" in data:
            memory.tags.clear()  # Remove todas as tags atuais
            for tag_name in data["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                memory.tags.append(tag)
        db.session.commit()
        return make_response(jsonify({'memory': memory.json()}), 200)
    except Exception as e:
        app.logger.error(f"Error updating memory: {str(e)}")
        return make_response(jsonify({'message': 'Error updating memory'}), 500)

@app.route('/memories/search', methods=['GET'])
def search_or_filter_memories():
    query = request.args.get('query', None)
    tag_name = request.args.get('tag', None)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    # Se nenhum parâmetro for passado, retorna erro
    if not any([query, tag_name, start_date, end_date]):
        return make_response(jsonify({"error": "At least one search parameter is required"}), 400)

    memories = Memory.query

    # Se houver busca por texto
    if query:
        memories = memories.filter(
            (Memory.title.ilike(f"%{query}%")) | (Memory.description.ilike(f"%{query}%"))
        )

    # Se houver filtro por tag
    if tag_name:
        memories = memories.join(Memory.tags).filter(Tag.name == tag_name)

    # Se houver filtro por data
    if start_date:
        memories = memories.filter(Memory.date >= start_date)
    if end_date:
        memories = memories.filter(Memory.date <= end_date)

    results = memories.all()

    return make_response(jsonify({'memories': [memory.json() for memory in results]}), 200)


@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')