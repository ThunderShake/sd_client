from googleapiclient.discovery import build

# Configure a chave de API
api_key = 'AIzaSyD6wOk7y5ll0i99zBpvAlgL2GVNVvOEVFQ'

# Crie um serviço da API do YouTube
youtube = build('youtube', 'v3', developerKey=api_key)

# Realize uma pesquisa de vídeos
def search_videos(query):
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=20
    )
    response = request.execute()
    
    # Extraia informações relevantes dos resultados da pesquisa
    videos = []
    for item in response['items']:
        video = {
            'titulo': item['snippet']['title'],
            'video_id': item['id']['videoId']
        }
        videos.append(video)
    
    return videos

# Exemplo de uso da função de pesquisa
# search_string =  query+ ' tutorial ' + 'learn '+ 'course ' + 'curso '
# results = search_videos(search_string)

# # Imprime os resultados
# for video in results:
#     print(f"Título: {video['titulo']}")
#     print(f"ID do vídeo: {video['video_id']}")
#     print('---')
