from flask import Flask, request, jsonify, send_from_directory, abort
import os, uuid, json, glob
from datetime import datetime

RAW_DIR = 'data/raw'
CLASS_DIR = 'data/classified'
META_DIR = 'data/meta'

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLASS_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

app = Flask(__name__)

def save_meta(kind, id, meta):
    path = os.path.join(META_DIR, f"{kind}_{id}.json")
    with open(path, 'w') as f:
        json.dump(meta, f, indent=2)

@app.route('/upload_raw', methods=['POST'])
def upload_raw():
    if 'image' not in request.files:
        return jsonify({'error':'no image field'}), 400
    f = request.files['image']
    img_id = str(uuid.uuid4())
    filename = f"{img_id}_{f.filename}"
    f.save(os.path.join(RAW_DIR, filename))
    meta = {
        'id': img_id,
        'filename': filename,
        'timestamp': datetime.utcnow().isoformat()+'Z'
    }
    save_meta('raw', img_id, meta)
    return jsonify(meta), 201

@app.route('/list_raw')
def list_raw():
    items = []
    for p in glob.glob(os.path.join(META_DIR,'raw_*.json')):
        with open(p) as f:
            items.append(json.load(f))
    return jsonify(items)

@app.route('/download_raw/<img_id>')
def download_raw(img_id):
    matches = glob.glob(os.path.join(META_DIR,f"raw_{img_id}.json"))
    if not matches:
        abort(404)
    with open(matches[0]) as f:
        meta = json.load(f)
    return send_from_directory(RAW_DIR, meta['filename'], as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
