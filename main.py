from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import firebase_admin
import pyrebase
import secrets
from search import search_videos
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from firebase_admin import credentials
import requests
from flask_cors import CORS
import json


firebaseConfig = {
    "apiKey": "AIzaSyAprkEYSoGL6AiulfFf3vrVyXSCh0ybUTI",
    "authDomain": "skillflix-a23c3.firebaseapp.com",
    "projectId": "skillflix-a23c3",
    "storageBucket": "skillflix-a23c3.appspot.com",
    "messagingSenderId": "924409818048",
    "appId": "1:924409818048:web:e68611dcff76a34a22f625",
    "databaseURL": ""
}


firebaseConfigB = {
    "apiKey": "AIzaSyAprkEYSoGL6AiulfFf3vrVyXSCh0ybUTI",
  "authDomain": "skillflix-a23c3.firebaseapp.com",
  "projectId": "skillflix-a23c3",
  "storageBucket": "skillflix-a23c3.appspot.com",
  "messagingSenderId": "924409818048",
  "appId": "1:924409818048:web:e68611dcff76a34a22f625"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


cred = credentials.Certificate('./skillflix.json')

firebaseSocial = firebase_admin.initialize_app(cred)



app = Flask(__name__)
CORS(app)

app.secret_key = secrets.token_hex(16)


app.config['SOCIAL_AUTH_FACEBOOK_KEY'] = '248418171016883'
app.config['SOCIAL_AUTH_FACEBOOK_SECRET'] = 'df9d9304528ad32b130c7e11cac631ff'

facebook_bp = make_facebook_blueprint(scope='email')

app.register_blueprint(facebook_bp, url_prefix='/login')

def user_authenticated():
    return 2
    if 'user_id' in session:
        print(session['user_id'])
        return 'user_id' in session
    else:
        return False



def signup_with_email(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        
        ask = input("Do you want to login? [y/n]")
        if ask == 'y':
            login_with_email(email, password)
    except:
        print("Email already exists")


def login_with_email(email, password):
    try:
        login = auth.sign_in_with_email_and_password(email, password)
        print("Successfully logged in!")
        return True
    except:
        print("Invalid email or password")
        return False



@app.route('/login', methods=['POST'])
def login_email():
    # Recuperar os dados do formulário de login
    login_name = request.form.get('loginName')
    login_password = request.form.get('loginPassword')

    user_id = user_authenticated()  # Supondo que essa função retorne o ID do usuário autenticado

    # Faça o processamento necessário para adicionar o comentário ao vídeo
    api_url = f'https://flask-production-6371.up.railway.app/api/login'  # Substitua pelo URL da API desejada
    data = {
        'email': login_name,
        'pw': login_password
    }

    response = requests.post(api_url, json=data)

    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data.get('user_id')

        # Adicionar o user ID à session do Flask
        session['user_id'] = user_id
        return redirect(url_for('homepage'))
    else:
        # Ocorreu um erro durante o registro, retorne uma resposta de erro ou redirecione para uma página de erro
        return redirect('/error')



@app.route('/login', methods=['GET'])
def login():
    print("droga")
    if request.method == 'POST':
        email = request.form['loginName']
        password = request.form['loginPassword']

        # Chame a função de login com e-mail aqui
        login_successful = login_with_email(email, password)

        # Verifique o resultado do login e redirecione para a página adequada
        if login_successful:
            # Redirecione para a página inicial
            return redirect('/homepage')
        else:
            # Redirecione de volta para a página de login com uma mensagem de erro
            return redirect('/login?error=1')

    return render_template('login.html')

@app.route('/login_with_google', methods=['GET'])
def login_with_google():
    name = request.args.get('name')
    email = request.args.get('email')
    uid = request.args.get('uid')

    print(name)
    print(email)
    print(uid)


    # Faça o processamento necessário com os parâmetros recebidos
    api_url = f'https://flask-production-6371.up.railway.app/api/google/login'  # Substitua pelo URL da API desejada
    data = {
        'name': name,
        'email': email,
        'pw': uid
    }

    print("piu")
    response = requests.post(api_url, json=data)

    if response.status_code == 200 or response.status_code==201:
        user_data = response.json()
        user_id = user_data.get('user_id')

        # Adicionar o user ID à session do Flask
        session['user_id'] = user_id
        print(session['user_id'])
        return redirect(url_for('homepage'))
    else:
        # Ocorreu um erro durante o registro, retorne uma resposta de erro ou redirecione para uma página de erro
        return redirect('/error')





@app.route('/account')
def account():
    # Certifique-se de que o usuário esteja autenticado antes de acessar essa rota
    id_user = session['user_id']
    if not user_authenticated():
        return redirect('/login')

    user_api_url = f"https://flask-production-6371.up.railway.app/api/user/{id_user}"
    response = requests.get(user_api_url)

    if response.status_code == 200:
        user_data = response.json()
        email = user_data.get('email', '')
        name = user_data.get('name', '')

        return render_template("pagina_perfil.html", email=email, name=name)
    else:
        # Trate o caso de falha na obtenção dos dados do usuário
        return redirect('/error')



@app.route('/my_playlists')
def my_playlists():
    # Certifique-se de que o usuário esteja autenticado antes de acessar essa rota
    user_id = session['user_id']

    if not user_authenticated():
        return redirect('/login')
    
    playlists = f"https://flask-production-6371.up.railway.app/api/playlists/{user_id}"


    playlist_response = requests.get(playlists)
    if playlist_response.status_code == 200:
        playlist_data = playlist_response.json()
        playlists = []
        
        if len(playlist_data) > 0 and 'message' not in playlist_data:
            for playlist in playlist_data:
                playlist_id = playlist.get('id')
                playlist_name = playlist.get('name')
                playlists.append({'id': playlist_id, 'name': playlist_name})
        
        
        # Renderize o template HTML e passe as informações necessárias
        return render_template("pagina_playlist_lista.html",  playlists=playlists)

    else:
        # Trate o caso de falha na obtenção das playlists
                return redirect('/error')



@app.route('/playlist/<id>')
def playlist(id):
    # Certifique-se de que o usuário esteja autenticado antes de acessar essa rota
    if not user_authenticated():
        return redirect('/login')
    
    playlists_url = f"https://flask-production-6371.up.railway.app/api/playlists/videos/{id}"
    playlist_response = requests.get(playlists_url)
    if playlist_response.status_code == 200:
        playlist_data = playlist_response.json()
        print(playlist_data)
        videos = []
        if len(playlist_data) > 0 and 'message' not in playlist_data:
            for video in playlist_data:
                video_id = video.get('id_video')
                

                video_api_url = f"https://flask-production-6371.up.railway.app/api/videos/{video_id}"
                print("video" + str(video_id))

                # Faça a solicitação GET para a API de vídeos
                response = requests.get(video_api_url)

                if response.status_code == 200:
                    # A resposta foi bem-sucedida
                    video_data = response.json()
                    print(video_data)
                    video_id_platform = video_data.get("id_platform")

                    youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id_platform}&key=AIzaSyD6wOk7y5ll0i99zBpvAlgL2GVNVvOEVFQ&part=snippet"
                    video_response = requests.get(youtube_api_url)

                    if video_response.status_code == 200:
                        video_data = video_response.json()
                        video_info = video_data['items'][0]['snippet']
                        thumbnail_url = video_info['thumbnails']['high']['url']
                        title = video_info['title']

                        video_info = {
                            'thumbnail_url': thumbnail_url,
                            'title': title,
                            'id_video': video_id,  # Adiciona o ID do vídeo
                            'id_user_list': video.get('id_user_list')  # Adiciona o ID da playlist
                        }

                        videos.append(video_info)

        return render_template("pagina_playlist.html", videos=videos)

    return render_template("pagina_playlist.html")


@app.route('/logout')
def logout():
    # Limpar todos os dados da sessão
    session.clear()
    
    # Redirecionar para a página de login
    return redirect('/login')

@app.route('/about')
def about():
    return render_template("pagina_sobre.html")


@app.route('/homepage')
def homepage():
    # Certifique-se de que o usuário esteja autenticado antes de acessar essa rota
    if not user_authenticated():
        return redirect('/login')

    # Faça uma solicitação GET para obter os vídeos principais da API
    videos_api_url = "https://flask-production-6371.up.railway.app/api/videos/top/8"
    response = requests.get(videos_api_url)

    if response.status_code == 200:
        video_data = response.json()
        videos = []

        # Iterar sobre os dados dos vídeos
        for video in video_data:
            video_id_platform = video.get('id_platform', '')

            # Fazer uma solicitação à API do YouTube para obter informações adicionais do vídeo
            youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id_platform}&key=AIzaSyD6wOk7y5ll0i99zBpvAlgL2GVNVvOEVFQ"
            youtube_response = requests.get(youtube_api_url)

            if youtube_response.status_code == 200:
                youtube_data = youtube_response.json()
                if 'items' in youtube_data and len(youtube_data['items']) > 0:
                    item = youtube_data['items'][0]
                    # Restante do código

                    item = youtube_data['items'][0]
                    video_title = item['snippet']['title']
                    video_thumbnail_url = item['snippet']['thumbnails']['high']['url']
                    video_id = item['id']

                    videos.append({
                        'title': video_title,
                        'thumbnail_url': video_thumbnail_url,
                        'video_id': video_id
                    })
                    print(videos)

        return render_template("pagina_principal.html", videos=videos)
    else:
        # Trate o caso de falha na obtenção dos vídeos principais
        return redirect('/error')


@app.route('/search')
def search():
    # Certifique-se de que o usuário esteja autenticado antes de acessar essa rota
    query = request.args.get('q')
    if not user_authenticated():
        return redirect('/login')
    
    search_string = 'como ' + 'how ' + query + ' tutorial ' + 'learn ' + 'course ' + 'curso '
    results = search_videos(search_string)

    

    # a = ""
    # for video in results:
    #     a += f"Título: {video['titulo']}"
    #     a += f"<br>ID do vídeo: {video['video_id']}"
    #     a += f"<br>https://www.youtube.com/watch?v={video['video_id']}<br>"
    #     a += '---<br><br>'

    return render_template("pagina_tutorial.html", query=query, results=results)

@app.route('/get_video/<video_id>')
def get_video(video_id):
    # Certifique-se de que o usuário esteja autenticado antes de acessar essa rota
    if not user_authenticated():
        return redirect('/login')
    
    get_from_yt = f"https://flask-production-6371.up.railway.app/api/videos/youtube/{video_id}"
    response = requests.get(get_from_yt)
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        video_id = data['id']
        # Redireciona para a rota '/video/<video_id>'
        return redirect(url_for('view_video', video_id=video_id))
    return "piu"

@app.route('/video/<video_id>')
def view_video(video_id):

    user_id= session['user_id']
    # Certifique-se de que o usuário esteja autenticado antes de acessar essa rota
    if not user_authenticated():
        return redirect('/login')

    # Faça uma solicitação GET para a API para obter os dados do vídeo
    video_api_url = f"https://flask-production-6371.up.railway.app/api/videos/view/{video_id}"
    comments_api_url = f"https://flask-production-6371.up.railway.app/api/videos/{video_id}/comments"
    playlists = f"https://flask-production-6371.up.railway.app/api/playlists/{user_id}"

    response = requests.post(video_api_url)

    print("piu")

    if response.status_code == 200:
        video_data = response.json()
        likes = video_data.get('likes', 0)
        dislikes = video_data.get('dislikes', 0)
        views = video_data.get('views', 0)
        id_platform = video_data.get('id_platform', 0)
        print("piu")

        # Faça uma solicitação GET para a API para obter os comentários do vídeo
        comments_response = requests.get(comments_api_url)
        
        if comments_response.status_code == 200 or comments_response.status_code == 404:
            print("piu")
            comments_data = comments_response.json()
            comments = []

            if len(comments_data) > 0 and 'message' not in comments_data:
                for comment in comments_data:
                    name = comment.get('name', '')
                    descr = comment.get('descr', '')
                    comments.append({'name': name, 'descr': descr})

            
            playlist_response = requests.get(playlists)
            if playlist_response.status_code == 200:
                print("piu")
                playlist_data = playlist_response.json()
                playlists = []

                if len(playlist_data) > 0 and 'message' not in playlist_data:
                    for playlist in playlist_data:
                        playlist_id = playlist.get('id')
                        playlist_name = playlist.get('name')
                        playlists.append({'id': playlist_id, 'name': playlist_name})
                    
                # Renderize o template HTML e passe as informações necessárias
                api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={id_platform}&key=AIzaSyD6wOk7y5ll0i99zBpvAlgL2GVNVvOEVFQ"
                response = requests.get(api_url)
                if response.status_code == 200:
                    # A resposta foi bem-sucedida
                    data = response.json()
                    # Obtenha a descrição do vídeo
                    description = data['items'][0]['snippet']['description']

                    return render_template("pagina_video.html",description=description, likes=likes, dislikes=dislikes, views=views, comments=comments, video_id=video_id, playlists=playlists, id_platform=id_platform)

            else:
                # Trate o caso de falha na obtenção das playlists
                return redirect('/error')
        else:
            # Trate o caso de falha na obtenção dos comentários do vídeo
            return redirect('/error')
    else:
        # Trate o caso de falha na obtenção dos dados do vídeo
        return redirect('/error')
    

@app.route('/video/<video_id>/like', methods=['POST'])
def like_video(video_id):
    # Processar a requisição de like
    user_id = session['user_id']  # Supondo que essa função retorne o ID do usuário autenticado

    # Faça o processamento necessário para adicionar o comentário ao vídeo
    api_url = f'https://flask-production-6371.up.railway.app/api/videos/like'  # Substitua pelo URL da API desejada
    data = {
        'id_video': video_id,
        'id_user': user_id
    }

    response = requests.post(api_url, json=data)

    if response.status_code == 200:
        return redirect(url_for('view_video', video_id=video_id))
    else:
        # Ocorreu um erro durante o registro, retorne uma resposta de erro ou redirecione para uma página de erro
        return redirect('/error')

@app.route('/video/<video_id>/dislike', methods=['POST'])
def dislike_video(video_id):
    # Processar a requisição de dislike
    user_id = session['user_id']  # Supondo que essa função retorne o ID do usuário autenticado

    # Faça o processamento necessário para adicionar o comentário ao vídeo
    api_url = f'https://flask-production-6371.up.railway.app/api/videos/dislike'  # Substitua pelo URL da API desejada
    data = {
        'id_video': video_id,
        'id_user': user_id
    }

    response = requests.post(api_url, json=data)

    if response.status_code == 200:
        return redirect(url_for('view_video', video_id=video_id))
    else:
        # Ocorreu um erro durante o registro, retorne uma resposta de erro ou redirecione para uma página de erro
        return redirect('/error')


@app.route('/video/<video_id>/comments', methods=['POST'])
def add_comment(video_id):
    comment = request.form.get('comment')
    user_id = session['user_id']  # Supondo que essa função retorne o ID do usuário autenticado

    # Faça o processamento necessário para adicionar o comentário ao vídeo
    api_url = f'https://flask-production-6371.up.railway.app/api/videos/{video_id}/comments'  # Substitua pelo URL da API desejada
    data = {
        'id_user': user_id,
        'comment': comment
    }

    response = requests.post(api_url, json=data)

    if response.status_code == 200:
        return redirect(url_for('view_video', video_id=video_id))
    else:
        # Ocorreu um erro durante o registro, retorne uma resposta de erro ou redirecione para uma página de erro
        return redirect('/error')

@app.route("/create_playlist/<nome_playlist>", methods=['POST'])
def criar_playlist(nome_playlist):
    user_id = session['user_id']
    url = 'https://flask-production-6371.up.railway.app/api/playlists'
    data = {
        'id_user': user_id,
        'name': nome_playlist
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 201:
        return jsonify({"message": "Playlist criada com sucesso!"}), 201
    else:
        return jsonify({"error": "Erro ao criar a playlist"}), 500

@app.route("/add_to_playlist/<id_playlist>", methods=['POST'])
def add_to_playlist(id_playlist):
    user_id = 2
    video_id = request.args.get('videoId')  # Obtém o ID do vídeo a partir dos parâmetros da solicitação
    url = f'https://flask-production-6371.up.railway.app/api/playlists/videos'
    data = {
        'id_user_list': id_playlist,
        'id_video': video_id
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    print(response.status_code)

    if response.status_code == 200:
        return jsonify({"message": "Vídeo adicionado à playlist com sucesso!"}), 201
    else:
        return jsonify({"error": "Erro ao adicionar o vídeo à playlist"}), 500





@app.route('/register', methods=['POST'])
def register():
    # Obtenha os dados do formulário de registro
    name = request.form['registerName']
    email = request.form['registerEmail']
    password = request.form['registerPassword']
    repeat_password = request.form['registerRepeatPassword']

    # Verifique se as senhas coincidem
    if password != repeat_password:
        # Senhas não coincidem, retorne uma resposta de erro ou redirecione para uma página de erro
        return redirect('/error')

    print(name, email, password)
    # Faça a chamada para a API usando os dados do registro
    api_url = 'https://flask-production-6371.up.railway.app/api/register'  # Substitua pelo URL da API desejada
    data = {
        'name': name,
        'email': email,
        'pw': password
    }

    response = requests.post(api_url, json=data)
    
    print(response.text)
    print(response.status_code)
    # Verifique o código de status da resposta
    if response.status_code == 201:
        register_data = response.json()
        user_id = register_data['user_id']

        # Armazene o user_id na variável de sessão do Flask
        session['user_id'] = user_id

        # Redirecione para a página desejada
        return redirect('/homepage')
    else:
        # Ocorreu um erro durante o registro, retorne uma resposta de erro ou redirecione para uma página de erro
        return redirect('/error')




if __name__ == '__main__':
    app.run()
