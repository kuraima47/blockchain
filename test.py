import base64
import json

node_info = {
    "pub_key": "4a44599974518ea5b0f14c31c4463692ac0329cb84851f3435e6d1b18ee4eae4aa495f846a0fa1219bd58035671881d44423876e57db2abd57254d0197da0ebe",
    "ip": "5.1.83.226",
    "port": "30303",
}

encoded_info = base64.b64encode(json.dumps(node_info).encode()).decode()
node_id = f"mychain://v1.{encoded_info}"
print(f"node : {node_id}")
decoded_info = json.loads(
    base64.b64decode(node_id.split("://")[1].split(".")[1]).decode()
)
print(
    f"Public Key: {decoded_info['pub_key']}\nIP Address: {decoded_info['ip']}\nPort: {decoded_info['port']}"
)
