import pathlib, json, uvicorn, colorama
from fastapi import FastAPI, Response
from typing import List, Union
from models import Track

app = FastAPI()

data = []

@app.on_event("startup")
def startup_event():
    datapath = pathlib.Path() / 'data' / 'tracks.json'
    with open(datapath, 'r') as f:
        tracks = json.load(f)
        for track in tracks:
            data.append(Track(**track).dict())

@app.on_event("shutdown")
def shutdown_event():
    datapath = pathlib.Path() / 'data' / 'tracks.json'
    with open(datapath, 'w') as f:
        f.write(json.dumps(data, indent=2, default=str))

@app.get('/tracks', response_model=List[Track])
def get_tracks():
    return data

@app.get('/tracks/{id}', response_model=Union[Track, str])
def get_track(id: int, response: Response):
    track = None
    for t in data:
        if t['id'] == id:
            track = t
            break
    if track is None:
        response.status_code = 404
        return "Track not found"
    return track

@app.post('/tracks', response_model=Track, status_code=201)
def create_track(track:Track):
    track_dict = track.dict()
    track_dict['id'] = max(data, key=lambda x: x['id']).get('id') + 1
    data.append(track_dict)
    return track_dict

@app.put('/tracks/{id}', response_model=Union[Track, str])
def update_track(id: int, updated_track:Track, response: Response):
    track = None
    for t in data:
        if t['id'] == id:
            track = t
            break
    if track is None:
        response.status_code = 404
        return "Track not found"
    for k,v in updated_track.dict().items():
        if k != 'id':
            track[k] = v
    return track

@app.delete('/tracks/{id}')
def delete_track(id: int, response: Response):
    delete_index = next((idx for idx, track in enumerate(data) if track["id"] == id), None)
    if delete_index is None:
        response.status_code = 404
        return "Track not found"

    del data[delete_index]
    return Response(status_code=200)

if __name__ == "__main__":
    colorama.init()
    config = uvicorn.Config("main:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()
