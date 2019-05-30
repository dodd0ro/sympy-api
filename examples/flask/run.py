import os, sys
sys.path.append(
    os.path.dirname(
        os.path.realpath(__file__ + "/../../")))
        
from app import app

print(app.run)
if __name__ == '__main__':
    app.run(debug=True, port=5000)