from datetime import datetime
from bson.objectid import ObjectId
from utils.db import mongo

class User:
    @staticmethod
    def create(username, password_hash, email=None):
        user = {
            'username': username,
            'password': password_hash,
            'email': email,
            'created_at': datetime.now()
        }
        return mongo.db.users.insert_one(user).inserted_id
    
    @staticmethod
    def find_by_username(username):
        return mongo.db.users.find_one({'username': username})
    
    @staticmethod
    def get_user(user_id):
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
        return user

class Project:
    @staticmethod
    def create_project(user_id, project_data):
        project = {
            'user_id': user_id,
            'collaborators': [],  # Nova lista de colaboradores
            'title': project_data.get('title', 'New Project'),
            'description': project_data.get('description', ''),
            'bpm': project_data.get('bpm'),
            'instrument': project_data.get('instrument', 'piano'),
            'volume': project_data.get('volume', -10),
            'tempo': project_data.get('tempo'),
            'music_versions': [],  # Inicializa vazio, Music cuidará disso depois
            'created_at': datetime.now(),
            'created_by': user_id,
            'updated_at': datetime.now(),
            'last_updated_by': user_id
            #sem current_music_id mas o Music também vai cuidar papai
        }
        return str(mongo.db.projects.insert_one(project).inserted_id)

    @staticmethod
    def add_collaborator(project_id, user_id):
        result = mongo.db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {'$addToSet': {'collaborators': ObjectId(user_id)}}
        )
        return result.modified_count > 0

    @staticmethod
    def update_project(project_id, user_id, update_data):
        update_data['updated_at'] = datetime.now()
        update_data['last_updated_by'] = user_id

        result = mongo.db.projects.update_one(
            {'_id': ObjectId(project_id), 'user_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def get_project(project_id, user_id):
        # Baita de uma cabanagem pra depois o jsonify nn ficar chorando
        # ain ObjectID nao é serializável ain ain, vou dar erro ai, ain ain
        
        project = mongo.db.projects.find_one({
            '_id': ObjectId(project_id),
            'user_id': user_id
        })
        if project:
            project['_id'] = str(project['_id'])
            if 'current_music_id' in project:
                project['current_music_id'] = str(project['current_music_id'])
            if 'music_versions' in project:
                for version in project['music_versions']:
                    version['music_id'] = str(version['music_id'])
                    version['update_by'] = str(version.get('update_by', ''))
            project['created_by'] = str(project.get('created_by', ''))
            project['last_updated_by'] = str(project.get('last_updated_by', ''))
        return project
    
    @staticmethod
    def get_project_full_data(project_id, user_id):
        project = mongo.db.projects.find_one({
            '_id': ObjectId(project_id),
            'user_id': user_id
        })
        if project:
            project['_id'] = str(project['_id'])
            if 'current_music_id' in project:
                project['current_music_id'] = Music.get_music(project['current_music_id'])
            if 'music_versions' in project:
                for version in project['music_versions']:
                    version['music_id'] = Music.get_music(version['music_id'])
                    version['update_by'] = User.get_user(version['update_by'])
            project['created_by'] = User.get_user(project.get('created_by', ''))
            project['last_updated_by'] = User.get_user(project.get('last_updated_by', ''))
        return project

    @staticmethod
    def get_user_projects(user_id):
        # Busca projetos onde o usuário é dono OU colaborador
        projects = mongo.db.projects.find({
            '$or': [
                {'user_id': user_id},
                {'collaborators': ObjectId(user_id)}
            ]
        })
        return [{
            'id': str(p['_id']),
            'title': p.get('title'),
            'bpm': p.get('bpm'),
            'tempo': p.get('tempo'),
            'created_at': p.get('created_at'),
            'updated_at': p.get('updated_at'),
            'created_by': str(p.get('created_by', '')),
            'last_updated_by': str(p.get('last_updated_by', '')),
            'is_owner': p['user_id'] == user_id
        } for p in projects]

    @staticmethod
    def revert_to_version(project_id, target_music_id, user_id):
        music = mongo.db.musics.find_one({'_id': ObjectId(target_music_id)})
        if not music:
            return False

        result = mongo.db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {
                '$set': {
                    'current_music_id': ObjectId(target_music_id),
                    'updated_at': datetime.now(),
                    'last_updated_by': user_id
                },
                '$push': {
                    'music_versions': {
                        'music_id': ObjectId(target_music_id),
                        'updated_at': datetime.now(),
                        'update_by': user_id
                    }
                }
            }
        )
        return result.modified_count > 0
    
    

class Music:
    @staticmethod
    def create_music(project_id, layers, user_id):
        music = {
            'project_id': ObjectId(project_id),
            'layers': layers,
            'created_at': datetime.now(),
            'created_by': user_id
        }

        music_id = mongo.db.musics.insert_one(music).inserted_id

        # Ó ele ai, papai ama, papai cuida
        mongo.db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {
                '$set': {
                    'current_music_id': music_id,
                    'updated_at': datetime.now(),
                    'last_updated_by': user_id
                },
                '$push': {
                    'music_versions': {
                        'music_id': music_id,
                        'updated_at': datetime.now(),
                        'update_by': user_id
                    }
                }
            }
        )

        return str(music_id)

    @staticmethod
    def get_music(music_id):
        music = mongo.db.musics.find_one({'_id': ObjectId(music_id)})
        if music:
            music['_id'] = str(music['_id'])
            music['project_id'] = str(music['project_id'])
            music['created_by'] = str(music.get('created_by', ''))

        return music

# Adicionar nova coleção de convites
class Invitation:
    @staticmethod
    def create_invitation(project_id, from_user_id, to_user_id):
        invitation = {
            'project_id': ObjectId(project_id),
            'from_user_id': ObjectId(from_user_id),
            'to_user_id': ObjectId(to_user_id),
            'status': 'pending',  # pending, accepted, rejected
            'created_at': datetime.now()
        }
        return mongo.db.invitations.insert_one(invitation).inserted_id

    @staticmethod
    def find_by_id(invitation_id):
        return mongo.db.invitations.find_one({'_id': ObjectId(invitation_id)})
    
    @staticmethod
    def find_pending_by_user(user_id):
        return list(mongo.db.invitations.find({
            'to_user_id': ObjectId(user_id),
            'status': 'pending'
        }))
    
    @staticmethod
    def update_status(invitation_id, status):
        result = mongo.db.invitations.update_one(
            {'_id': ObjectId(invitation_id)},
            {'$set': {'status': status}}
        )
        return result.modified_count > 0
