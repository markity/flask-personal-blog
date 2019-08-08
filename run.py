from config import init
from config import con

init()


con.app.run(host='0.0.0.0', port=80, debug=False)
